import unittest

from gludb.simple import DBObject, Field
from gludb.data import Storable
import gludb.versioning


@DBObject(table_name='SimpleTest', versioning=gludb.versioning.NONE)
class SimpleData(object):
    name = Field('default name')
    descrip = Field()
    age = Field(42)


@DBObject(table_name='SetupTest', versioning=gludb.versioning.NONE)
class SetupData(object):
    name = Field('setup default')

    def setup(self, *args, **kwrds):
        self.found_arg = args[0] if len(args) == 1 else repr(args)
        self.found_name = kwrds.get('name', '<NAME MISSING!>')
        self.extra_data = "Hello World " + self.name


class BasicAbstractionTesting(unittest.TestCase):
    def setUp(self):
        pass

    def test_typing(self):
        for cls in [SimpleData, SetupData]:
            self.assertTrue(issubclass(cls, Storable))
            self.assertTrue(isinstance(cls(), Storable))

    def test_setup_called(self):
        s = SetupData('passthru', name='R')
        self.assertTrue('passthru', s.found_arg)
        self.assertTrue('R', s.found_name)
        self.assertTrue("Hellow World R", s.extra_data)

    def test_fields(self):
        s = SimpleData()
        self.assertEquals('default name', s.name)
        self.assertEquals('', s.descrip)
        self.assertEquals(42, s.age)

        s = SimpleData(name='Bob', descrip='abc', age=101)
        self.assertEquals('Bob', s.name)
        self.assertEquals('abc', s.descrip)
        self.assertEquals(101, s.age)

    def test_persistence(self):
        s = SimpleData(name='Bob', descrip='abc', age=101)
        data = s.to_data()
        s2 = SimpleData.from_data(data)
        self.assertEquals(data, s2.to_data())

        self.assertEquals('Bob', s2.name)
        self.assertEquals('abc', s2.descrip)
        self.assertEquals(101, s2.age)

# TODO: prop sets
# TODO: setup() call test (no params, args, and keywords)
