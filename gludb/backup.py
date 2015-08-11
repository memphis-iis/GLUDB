"""Supply backup functionality for gludb. Note that we mainly provide a way for
users to create a small script that backs up their data to S3. We are assuming
that the S3 bucket used will be configured for archival (either deletion or
archival to Glacier)
"""

# TODO: need unit tests

import os
import os.path as pth
import datetime
import pkgutil
import tarfile
from importlib import import_module
from inspect import getmembers, isclass, getmro
from tempfile import NamedTemporaryFile

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from .config import get_mapping
from .data import Storable
from .simple import DBObject, Field


# TODO: we need to refactor this now_field stuff into a single place
def now_field():
    """Return a string we use for storing our date time values"""
    return 'UTC:' + datetime.datetime.utcnow().isoformat()


def is_backup_class(cls):
    return (
        isclass(cls) and
        issubclass(Storable) and
        get_mapping(cls, no_mapping_ok=True)
    )


def backup_name(cls):
    return cls.__name__ + ':' + cls.get_table_name()


# Turns out the library qualname doesn't handle annotated classes and we need
# Python 2 for gcd docs .... so we'll force-annotated Backup below
class Backup(object):
    name = Field('backup')
    timestamp = Field(now_field)
    aws_access_key = Field('')
    aws_secret_key = Field('')
    bucketname = Field('')
    class_instance_stats = Field(dict)
    backup_log = Field(list)

    def setup(self):
        # We don't ever store this name-to-class mapping
        self.classes = dict()

        # If we they didn't manually specify AWS creds when we were created,
        # then we read them from the AWS-documented environ variables that
        # boto would use anyway
        if not self.aws_access_key:
            self.aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID', '')
        if not self.aws_secret_key:
            self.aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY', '')

    def add_package(self, pkg_name, recurse=True, include_bases=True):
        pkg = __import__(pkg_name)

        for module_loader, name, ispkg in pkgutil.walk_packages(pkg.__path__):
            if not ispkg:
                # Module
                mod = import_module('.' + name, pkg.__name__)
                for name, member in getmembers(mod):
                    if is_backup_class(member):
                        self.add_class(member, include_bases=include_bases)
            elif recurse:
                # Package and we're supposed to recurse
                self.add_package(name, True)

    def add_class(self, cls, include_bases=True, fail_on_cls_mismatch=True):
        if not is_backup_class(cls):
            if fail_on_cls_mismatch:
                raise ValueError(cls.__name__ + " not valid for backup")
            return

        cls_name = backup_name(cls)
        self.class_instance_stats[cls_name] = 0
        self.classes[cls_name] = cls

        if include_bases:
            for candidate_cls in getmro(cls):
                if is_backup_class(cls):
                    # Note that we don't keep recursing on base classes
                    self.add_class(candidate_cls, include_bases=False)

    def log(self, entry, *args):
        if args:
            entry = entry % args
        self.backup_log.append(entry)

    def run_backup(self):
        self.log("Starting backup")

        # Start the compressed tarball our data is stored in
        backup_file = NamedTemporaryFile(suffix=".tar.gz")
        backup_tarfile = tarfile.open(fileobj=backup_file, mode='w:gz')

        for cls_name, cls in self.classes.items():
            self.log("Backing up %s", cls_name)

            rec_count = 0

            with NamedTemporaryFile() as record_file:
                for rec in cls.find_all():
                    record_file.write(rec.to_data())
                    record_file.write('\n')
                    rec_count += 1

                record_file.flush()
                backup_tarfile.add(record_file.name, arcname=cls_name+'.json')

            self.log("%s => %d records backed up", cls_name, rec_count)

        # Finalize archive
        backup_tarfile.close()
        backup_file.flush()
        backup_size = os.stat(backup_file.name)[6]

        # upload archive to s3
        if os.environ.get('DEBUG', False) or os.environ.get('travis', False):
            # TODO: running locally or Travis - we need to mock/stub/etc
            class TestingKey(object):
                def set_contents_from_filename(subself, fn):
                    if not pth.isfile(fn):
                        raise ValueError(fn + " is not a file")
                    self.log("DEBUG/TRAVIS backup - no S3 xfer")
                    self.log("Would have transmitted %s", fn)
            key = TestingKey()
        else:
            conn = S3Connection(self.aws_access_key, self.aws_secret_key)
            bucket = conn.get_bucket(self.bucketname)
            key = Key(bucket)
            key.key = 'Backup:' + now_field()

        self.log("Sending %s [size=%d bytes]", backup_file.name, backup_size)
        key.set_contents_from_filename(backup_file.name)
        self.log("Sent %s", backup_file.name)

        # All done
        backup_file.close()
        self.log("Backup completed")

# TODO:
Backup = DBObject(table_name='BackupHistory')(Backup)
