"""Testing all the functionality in gludb.simple *except* for actual
data storage (that's in simple_data_tests.py)
"""

import unittest

from gludb.simple import DBObject, Field
from gludb.data import Storable
from gludb.versioning import VersioningTypes

from utils import compare_data_objects


@DBObject(table_name='SimpleTest')
class SimpleData(object):
    name = Field('default name')
    descrip = Field()
    age = Field(42)
    setup = "Dummy variable to make sure optional setup calling doesn't choke"


@DBObject(table_name='SetupTest')
class SetupData(object):
    name = Field('setup default')

    def setup(self, *args, **kwrds):
        self.found_arg = args[0] if len(args) == 1 else repr(args)
        self.found_name = kwrds.get('name', '<NAME MISSING!>')
        self.extra_data = "Hello World " + self.name


@DBObject(table_name='SetupTest')
class ComplexData(object):
    name = Field('')
    complex_data = Field(dict)


class BasicAbstractionTesting(unittest.TestCase):
    def setUp(self):
        pass

    def assertObjEq(self, obj1, obj2):
        self.assertTrue(compare_data_objects(obj1, obj2))

    def test_typing(self):
        for cls in [SimpleData, SetupData]:
            self.assertTrue(issubclass(cls, Storable))
            self.assertTrue(isinstance(cls(), Storable))

    def test_storage_metadata(self):
        s = SimpleData()
        self.assertEquals('SimpleTest', s.get_table_name())
        self.assertEquals(VersioningTypes.NONE, s.__versioning__)

    def test_setup_called(self):
        s = SetupData('passthru', name='R')
        self.assertEquals('', s.id)
        self.assertEquals('passthru', s.found_arg)
        self.assertEquals('R', s.found_name)
        self.assertEquals("Hello World R", s.extra_data)

    def test_fields(self):
        s = SimpleData()
        self.assertEquals('', s.id)
        self.assertEquals('default name', s.name)
        self.assertEquals('', s.descrip)
        self.assertEquals(42, s.age)

        s = SimpleData(name='Bob', descrip='abc', age=101)
        self.assertEquals('', s.id)
        self.assertEquals('Bob', s.name)
        self.assertEquals('abc', s.descrip)
        self.assertEquals(101, s.age)

    def test_persistence(self):
        s = SimpleData(name='Bob', descrip='abc', age=101)
        data = s.to_data()
        s2 = SimpleData.from_data(data)
        self.assertObjEq(s, s2)

        self.assertEquals('', s2.id)
        self.assertEquals('Bob', s2.name)
        self.assertEquals('abc', s2.descrip)
        self.assertEquals(101, s2.age)

    def test_prop_sets(self):
        s = SimpleData(name='Bob', descrip='abc', age=101)
        s.name = 'Alice'
        s.descrip = 'xyz'
        s.age = -42

        # Make sure defaults all overridden
        s2 = SimpleData.from_data(s.to_data())
        self.assertEquals('', s2.id)
        self.assertEquals('Alice', s2.name)
        self.assertEquals('xyz', s2.descrip)
        self.assertEquals(-42, s2.age)

    def test_id(self):
        s = SimpleData(id='key', name='Bob', descrip='abc', age=101)
        self.assertEquals('key', s.id)
        self.assertEquals('key', s.get_id())
        self.assertEquals('Bob', s.name)
        self.assertEquals('abc', s.descrip)
        self.assertEquals(101, s.age)

        # Direct setting
        s.id = 'key2'
        self.assertEquals('key2', s.id)
        self.assertEquals('key2', s.get_id())

        s2 = SimpleData.from_data(s.to_data())
        self.assertEquals('key2', s2.id)
        self.assertEquals('key2', s2.get_id())
        self.assertEquals('Bob', s2.name)
        self.assertEquals('abc', s2.descrip)
        self.assertEquals(101, s2.age)

        # Use the set_id method required by Storable
        s.set_id('key3')
        self.assertEquals('key3', s.id)
        self.assertEquals('key3', s.get_id())

        s2 = SimpleData.from_data(s.to_data())
        self.assertEquals('key3', s2.id)
        self.assertEquals('key3', s2.get_id())
        self.assertEquals('Bob', s2.name)
        self.assertEquals('abc', s2.descrip)
        self.assertEquals(101, s2.age)
