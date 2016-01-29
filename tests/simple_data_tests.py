"""Testing data storage functionality in gludb.simple (see simple_tests.py for
testing of the rest of gludb.simple functionality)"""

import unittest
import datetime
import time

import gludb.config

from gludb.versioning import VersioningTypes
from gludb.data import orig_version
from gludb.simple import DBObject, Field
from gludb.utils import parse_now_field

from utils import compare_data_objects


@DBObject(table_name='SimpleStorageTest', versioning=VersioningTypes.NONE)
class SimpleStorage(object):
    name = Field('default name')
    descrip = Field()
    age = Field(42)
    extra_data = Field(dict)


# Same tests as DefaultStorageTesting but with differnt setUp/tearDown
class MissingMapTesting(unittest.TestCase):
    def setUp(self):
        gludb.config.default_database(None)  # no default database

    def tearDown(self):
        # Undo any database setup
        gludb.config.clear_database_config()

    def test_failedops(self):
        def try_op():
            return gludb.config.get_mapping(SimpleStorage)
        self.assertRaises(ValueError, try_op)

    def test_justnomap(self):
        mapped = gludb.config.get_mapping(SimpleStorage, no_mapping_ok=True)
        self.assertIsNone(mapped)


class DefaultStorageTesting(unittest.TestCase):
    def setUp(self):
        gludb.config.default_database(gludb.config.Database(
            'sqlite',
            filename=':memory:'
        ))
        SimpleStorage.ensure_table()

    def tearDown(self):
        # Undo any database setup
        gludb.config.clear_database_config()

    def assertObjEq(self, obj1, obj2):
        self.assertTrue(compare_data_objects(obj1, obj2))

    def assertReadable(self, obj):
        read_back = obj.__class__.find_one(obj.id)
        self.assertObjEq(obj, read_back)
        orig_ver = obj.__class__.from_data(orig_version(read_back))
        self.assertObjEq(obj, orig_ver)

    def assertCloseTimes(self, d1, d2, eps=0.15):
        self.assertTrue(abs((d1 - d2).total_seconds()) < eps)

    def assertNotCloseTimes(self, d1, d2, eps=0.15):
        self.assertTrue(abs((d1 - d2).total_seconds()) >= eps)

    def test_missing(self):
        self.assertIsNone(SimpleStorage.find_one('not there'))
        
    def test_table_has_prefix(self):
        self.assertIsEqual(SimpleStorage.get_table_name(), cls.__table_name__)

    def test_extra_fields(self):
        s = SimpleStorage(name='TimeTracking', descrip='FirstSave')
        s.save()

        create1 = parse_now_field(s._create_date)
        update1 = parse_now_field(s._last_update)

        self.assertCloseTimes(datetime.datetime.utcnow(), update1)
        self.assertCloseTimes(create1, update1)

        # Sucks, but we need to space out our timestamps
        time.sleep(0.3)

        s.descrip = 'SecondSave'
        s.save()

        create2 = parse_now_field(s._create_date)
        update2 = parse_now_field(s._last_update)

        self.assertCloseTimes(datetime.datetime.utcnow(), update2)
        self.assertCloseTimes(create1, create2)
        self.assertNotCloseTimes(update1, update2)

        s2 = SimpleStorage.find_one(s.id)
        create3 = parse_now_field(s2._create_date)
        update3 = parse_now_field(s2._last_update)

        # Note that we DON'T check for string equality - that's because
        # _last_update is updated every time the instance method to_data is
        # called. See simple.md for extra details on auto fields
        self.assertCloseTimes(create2, create3)
        self.assertCloseTimes(update2, update3)

    def test_readwrite(self):
        s = SimpleStorage(name='Pre', descrip='Testing', age=-1)
        self.assertEquals('', s.id)
        self.assertEquals('Pre', s.name)
        self.assertEquals('Testing', s.descrip)
        self.assertEquals(-1, s.age)
        self.assertEquals({}, s.extra_data)

        s.extra_data['coolness'] = {'a': 123, 'b': 456}
        s.extra_data['list-thing'] = [1, 2, 3, 4, 5, 6]
        s.extra_data['oscar'] = 'grouch'
        s.extra_data['fp'] = 42.42

        self.assertTrue(orig_version(s) is None)

        s.save()
        self.assertTrue(len(s.id) > 0)
        self.assertReadable(s)
        # Saved - so should have a prev version that is identical
        self.assertObjEq(s, SimpleStorage.from_data(orig_version(s)))

        s2 = SimpleStorage(id=s.id, name='Post', descrip='AtItAgain', age=256)
        s2.save()
        self.assertReadable(s2)

        all_recs = SimpleStorage.find_all()
        self.assertEqual(1, len(all_recs))
        self.assertObjEq(s2, all_recs[0])

        # Change the object we read and then insure that the pervious version
        # saved on load is correct
        read_obj = all_recs[0]
        read_obj.name = 'Pre2'
        read_obj.descrip = 'Testing2'
        read_obj.age = -2

        s0 = SimpleStorage.from_data(orig_version(read_obj))
        self.assertEquals(s.id, s0.id)
        self.assertEquals('Post', s0.name)
        self.assertEquals('AtItAgain', s0.descrip)
        self.assertEquals(256, s0.age)
        self.assertEquals({}, s0.extra_data)


# Same tests as DefaultStorageTesting but with differnt setUp/tearDown
class SpecificStorageTesting(DefaultStorageTesting):
    def setUp(self):
        gludb.config.default_database(None)  # no default database
        gludb.config.class_database(SimpleStorage, gludb.config.Database(
            'sqlite',
            filename=':memory:'
        ))
        SimpleStorage.ensure_table()

    def tearDown(self):
        # Undo any database setup
        gludb.config.clear_database_config()

        
# Same tests as DefaultStorageTesting but with differnt setUp/tearDown
class PrefixedStorageTesting(DefaultStorageTesting):
    PREFIX = "Prefix"
    
    def setUp(self):
        gludb.config.default_database(None)  # no default database
        gludb.config.class_database(SimpleStorage, gludb.config.Database(
            'sqlite',
            filename=':memory:'
        ))
        gludb.config.set_db_application_prefix(self.PREFIX)
        SimpleStorage.ensure_table()

    def tearDown(self):
        # Undo any database setup
        gludb.config.clear_database_config()
        gludb.config.set_db_application_prefix(None)
        
    def test_table_has_prefix(self):
        expectedName = PREFIX + gludb.config.APPLICATION_SEP + cls.__table_name__
        self.assertIsEqual(SimpleStorage.get_table_name(), expectedName)