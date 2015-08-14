"""Supply backup functionality for gludb. Note that we mainly provide a way for
users to create a small script that backs up their data to S3. We are assuming
that the S3 bucket used will be configured for archival (either deletion or
archival to Glacier)
"""

import sys
import os
import pkgutil
import tarfile

from importlib import import_module
from inspect import getmembers, isclass, getmro
from tempfile import NamedTemporaryFile

from boto.s3.connection import S3Connection, OrdinaryCallingFormat
from boto.s3.key import Key

from .utils import now_field
from .config import get_mapping
from .data import Storable
from .simple import DBObject, Field

# TODO: need the back to check for previous backups and only run if enough time
#       has elapsed. Best way is probably: store json for backup after
#       success. Then we read it back to get date/time of last backup


def is_backup_class(cls):
    return True if (
        isclass(cls) and
        issubclass(cls, Storable) and
        get_mapping(cls, no_mapping_ok=True)
    ) else False


def backup_name(cls):
    return cls.__name__ + '--' + cls.get_table_name()

if sys.version_info >= (3, 0):
    def write_line(file_obj, line):
        file_obj.write(bytes(str(line) + '\n', 'UTF-8'))
else:
    def write_line(file_obj, line):
        file_obj.write(str(line))
        file_obj.write('\n')


# Turns out the library qualname doesn't handle annotated classes and we need
# Python 2 for gcd docs .... so we'll force-annotated Backup below
class Backup(object):
    name = Field('backup')
    timestamp = Field(now_field)
    aws_access_key = Field('')
    aws_secret_key = Field('')
    bucketname = Field('')
    backup_log = Field(list)

    def setup(self, *args, **kwrds):
        # We don't ever store this name-to-class mapping
        self.classes = dict()

        # If we they didn't manually specify AWS creds when we were created,
        # then we read them from the AWS-documented environ variables that
        # boto would use anyway
        if not self.aws_access_key:
            self.aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID', '')
        if not self.aws_secret_key:
            self.aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY', '')

    def add_package(
        self,
        pkg_name,
        recurse=True,
        include_bases=True,
        parent_pkg=None
    ):
        if parent_pkg:
            pkg = import_module('.' + pkg_name, parent_pkg)
        else:
            pkg = import_module(pkg_name)

        for module_loader, name, ispkg in pkgutil.walk_packages(pkg.__path__):
            if not ispkg:
                # Module
                mod = import_module('.' + name, pkg_name)
                for name, member in getmembers(mod):
                    if is_backup_class(member):
                        self.add_class(member, include_bases=include_bases)
            elif recurse:
                # Package and we're supposed to recurse
                self.add_package(pkg_name + '.' + name, True)

    def add_class(self, cls, include_bases=True):
        if not is_backup_class(cls):
            return 0

        added = 0

        cls_name = backup_name(cls)
        if cls_name not in self.classes:
            self.classes[cls_name] = cls
            self.log("Added class for backup: %s", cls_name)
            added = 1

        if include_bases:
            for candidate_cls in getmro(cls):
                if is_backup_class(cls):
                    # Note that we don't keep recursing on base classes
                    added += self.add_class(candidate_cls, include_bases=False)

        return added

    def log(self, entry, *args):
        if args:
            entry = entry % args
        self.backup_log.append(entry)

    def run_backup(self):
        self.log("Starting backup at %s", now_field())
        self.log("Backup config object created at %s", self.timestamp)

        # Make sure we're good to go
        for fld in ['aws_access_key', 'aws_secret_key', 'bucketname']:
            val = getattr(self, fld, None)
            if not val:
                self.log("Backup cannot start: %s is a required field", fld)
                raise ValueError(self.backup_log[-1])

        # Start the compressed tarball our data is stored in
        backup_file = NamedTemporaryFile(suffix=".tar.gz")
        backup_tarfile = tarfile.open(fileobj=backup_file, mode='w:gz')

        for cls_name, cls in self.classes.items():
            self.log("Backing up %s", cls_name)

            rec_count = 0

            with NamedTemporaryFile() as record_file:
                for rec in cls.find_all():
                    write_line(record_file, rec.to_data())
                    rec_count += 1

                record_file.flush()
                backup_tarfile.add(record_file.name, arcname=cls_name+'.json')

            self.log("%s => %d records backed up", cls_name, rec_count)

        # Finalize archive
        backup_tarfile.close()
        backup_file.flush()
        backup_size = os.stat(backup_file.name)[6]

        # Figure out key name for archived file
        key_name = ('Backup_' + now_field() + '.tar.gz').replace(':', '_')

        # upload archive to s3
        if os.environ.get('DEBUG', False) or os.environ.get('travis', False):
            # Local or CI - connect to our mock s3 service
            conn = S3Connection(
                '', '',
                is_secure=False, port=8888, host='localhost',
                calling_format=OrdinaryCallingFormat()
            )
        else:
            conn = S3Connection(self.aws_access_key, self.aws_secret_key)

        bucket = conn.get_bucket(self.bucketname)
        key = Key(bucket)
        key.key = key_name

        self.log(
            "Sending %s [size=%d bytes] with key name %s",
            backup_file.name,
            backup_size,
            key_name
        )

        # TODO: should probably look into a multi-part upload for larger backup
        key.set_contents_from_filename(backup_file.name)
        self.log("Sent %s", backup_file.name)

        # All done
        backup_file.close()
        self.log("Backup completed")

# TODO: return to an annotation when we can use Python3 for our doc generation
Backup = DBObject(table_name='BackupHistory')(Backup)
