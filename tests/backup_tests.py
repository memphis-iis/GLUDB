"""Testing backup functionality
"""

import unittest
import tarfile
import os.path as pth

from itertools import chain

import gludb.config
from gludb.simple import DBObject, Field
from gludb.backup import Backup, is_backup_class, backup_name, strip_line

# Note that we expect our s3server.py mock server to be running, which will
# automatically created the bucket BACKUP_BUCKET_NAME
from utils import compare_data_objects, S3_DIR, BACKUP_BUCKET_NAME


@DBObject(table_name='SimpleTest')
class SimpleData(object):
    name = Field('default name')
    descrip = Field()
    age = Field(42)


@DBObject(table_name='SetupTest')
class ComplexData(object):
    name = Field('')
    complex_data = Field(dict)


@DBObject(table_name='InheritedTest')
class InheritedData(SimpleData, ComplexData):
    only_inherited = Field(42)


def no_blanks(t):
    return list(filter(None, t))


def extract_backup(bucketname, keyname):
    """Return a dict of (table-name, JSON-list) from the specified backup"""
    filename = pth.join(S3_DIR, bucketname, keyname)
    print("Opening backup archive %s" % filename)

    backup_dict = dict()

    with tarfile.open(filename, mode="r:gz") as backup:
        for member in backup:
            file = backup.extractfile(member)
            data = no_blanks([strip_line(i) for i in file.readlines()])
            backup_dict[member.name] = data
            file.close()

    return backup_dict


def extract_one(backup_dict, cls):
    """Given the dict from extract_backup and a class, return a list of objects
    from the backup"""
    name = backup_name(cls) + '.json'  # Don't forget file extension
    return [cls.from_data(i) for i in backup_dict[name]]


class BackupPlumbingTesting(unittest.TestCase):
    """Test basic functions and helpers in the backup module"""

    def setUp(self):
        gludb.config.default_database(gludb.config.Database(
            'sqlite',
            filename=':memory:'
        ))

    def tearDown(self):
        # Undo any database setup
        gludb.config.clear_database_config()

    def assertObjEq(self, obj1, obj2):
        self.assertTrue(compare_data_objects(obj1, obj2))

    def test_backup_obj_check(self):
        class NadaClass(object):
            pass

        def somefunc():
            pass

        @DBObject(table_name='Tiny')
        class TinyBackup(object):
            f = Field('')

        self.assertFalse(is_backup_class(None))
        self.assertFalse(is_backup_class(''))
        self.assertFalse(is_backup_class(42))
        self.assertFalse(is_backup_class([]))

        self.assertFalse(is_backup_class(NadaClass))
        self.assertFalse(is_backup_class(somefunc))

        self.assertFalse(is_backup_class(NadaClass))
        self.assertFalse(is_backup_class(somefunc))

        self.assertTrue(is_backup_class(TinyBackup))
        self.assertTrue(is_backup_class(SimpleData))
        self.assertTrue(is_backup_class(ComplexData))


class BackupRunTesting(unittest.TestCase):
    def setUp(self):
        gludb.config.default_database(gludb.config.Database(
            'sqlite',
            filename=':memory:'
        ))
        SimpleData.ensure_table()
        ComplexData.ensure_table()
        InheritedData.ensure_table()

        self.backup = Backup(
            aws_access_key='testing',
            aws_secret_key='testing',
            bucketname=BACKUP_BUCKET_NAME
        )

    def tearDown(self):
        # Undo any database setup
        print('\n'.join(self.backup.backup_log))
        gludb.config.clear_database_config()

    def assertObjEq(self, obj1, obj2):
        self.assertTrue(compare_data_objects(obj1, obj2))

    def assertObjListsEq(self, lst1, lst2):
        def key(obj):
            return getattr(obj, 'id', '')
        for o1, o2 in zip(sorted(lst1, key=key), sorted(lst2, key=key)):
            self.assertObjEq(o1, o2)

    def test_simple_backup(self):
        simple = [
            SimpleData(name='Name', descrip='Descrip', age=i)
            for i in range(7)
        ]
        complex = [
            ComplexData(name='Name'+str(i), complex_data={'a': i})
            for i in range(7)
        ]

        for obj in chain(simple, complex):
            obj.save()

        self.assertEquals(
            1,
            self.backup.add_class(SimpleData, include_bases=False)
        )
        self.assertEquals(
            1,
            self.backup.add_class(ComplexData, include_bases=False)
        )

        self.assertEquals(2, len(self.backup.classes))

        bucketname, keyname = self.backup.run_backup()
        backups = extract_backup(bucketname, keyname)

        self.assertObjListsEq(simple, extract_one(backups, SimpleData))
        self.assertObjListsEq(complex, extract_one(backups, ComplexData))

    def test_include_bases_backup(self):
        simple = [
            SimpleData(name='Name', descrip='Descrip', age=i)
            for i in range(7)
        ]
        complex = [
            ComplexData(name='Name'+str(i), complex_data={'a': i})
            for i in range(7)
        ]
        inherited = [InheritedData(only_inherited=i) for i in range(7)]

        for obj in chain(simple, complex, inherited):
            obj.save()

        self.assertEquals(
            3,
            self.backup.add_class(InheritedData, include_bases=True)
        )

        self.assertEquals(3, len(self.backup.classes))

        bucketname, keyname = self.backup.run_backup()
        backups = extract_backup(bucketname, keyname)

        self.assertObjListsEq(simple, extract_one(backups, SimpleData))
        self.assertObjListsEq(complex, extract_one(backups, ComplexData))
        self.assertObjListsEq(inherited, extract_one(backups, InheritedData))

    def test_include_package(self):
        from testpkg.module import TopData
        from testpkg.subpkg1.module import MidData1
        from testpkg.subpkg2.module import MidData2
        from testpkg.subpkg1.subsubpkg.module import BottomData

        expected_dict = dict()
        for cls in [TopData, MidData1, MidData2, BottomData]:
            cls.ensure_table()
            data = [cls(name='Name'+str(i)) for i in range(7)]
            for d in data:
                d.save()
            expected_dict[backup_name(cls)] = data

        self.backup.add_package("testpkg")

        self.assertEquals(4, len(self.backup.classes))

        bucketname, keyname = self.backup.run_backup()
        backups = extract_backup(bucketname, keyname)

        for cls in [TopData, MidData1, MidData2, BottomData]:
            expected = expected_dict[backup_name(cls)]
            self.assertObjListsEq(expected, extract_one(backups, cls))
