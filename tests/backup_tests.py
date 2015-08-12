"""Testing backup functionality
"""

import unittest

import gludb.config
from gludb.simple import DBObject, Field
from gludb.backup import Backup, is_backup_class

from utils import compare_data_objects


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

        # TODO: all of these values are wrong
        self.backup = Backup(
            aws_access_key='TODO',
            aws_secret_key='TODO',
            bucketname='BackupTesting'
        )

    def tearDown(self):
        # Undo any database setup
        print('\n'.join(self.backup.backup_log))
        gludb.config.clear_database_config()

    def assertObjEq(self, obj1, obj2):
        self.assertTrue(compare_data_objects(obj1, obj2))

    def test_simple_backup(self):
        for i in range(7):
            SimpleData(name='Name', descrip='Descrip', age=i).save()
            ComplexData(name='Name'+str(i), complex_data={'a': i}).save()

        self.assertEquals(
            1,
            self.backup.add_class(SimpleData, include_bases=False)
        )
        self.assertEquals(
            1,
            self.backup.add_class(ComplexData, include_bases=False)
        )

        self.assertEquals(2, len(self.backup.classes))

        self.backup.run_backup()  # TODO: check results

    def test_include_bases_backup(self):
        for i in range(7):
            SimpleData(name='Name', descrip='Descrip', age=i).save()
            ComplexData(name='Name'+str(i), complex_data={'a': i}).save()
            InheritedData(only_inherited=i).save()

        self.assertEquals(
            3,
            self.backup.add_class(InheritedData, include_bases=True)
        )

        self.assertEquals(3, len(self.backup.classes))

        self.backup.run_backup()  # TODO: check results

    def test_include_package(self):
        from testpkg.module import TopData
        from testpkg.subpkg1.module import MidData1
        from testpkg.subpkg2.module import MidData2
        from testpkg.subpkg1.subsubpkg.module import BottomData

        for cls in [TopData, MidData1, MidData2, BottomData]:
            cls.ensure_table()
            for i in range(7):
                cls(name='Name'+str(i)).save()

        self.backup.add_package("testpkg")

        self.assertEquals(4, len(self.backup.classes))

        self.backup.run_backup()  # TODO: check results
