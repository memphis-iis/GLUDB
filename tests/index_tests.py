"""Testing all the functionality in gludb.simple *except* for actual
data storage (that's in simple_data_tests.py)
"""

import unittest

from gludb.simple import DBObject, Field, Index

from .utils import compare_data_objects


@DBObject(table_name='IndexTest')
class IndexedData(object):
    name = Field('default name')
    descrip = Field()
    age = Field(42)
    setup = "Dummy variable to make sure optional setup calling doesn't choke"

    @Index
    def my_name(self):
        return self.name

    @Index
    def half_age(self):
        return self.age/2

    def not_indexed(self):
        return 'duh'

    def setup(self, *args, **kwrds):
        self.extra_property = 'Hello There'


class IndexTesting(unittest.TestCase):
    def setUp(self):
        pass

    def assertObjEq(self, obj1, obj2):
        self.assertTrue(compare_data_objects(obj1, obj2))

    def test_index_function(self):
        s = IndexedData(name='Bob', descrip='abc', age=100)
        self.assertEquals('', s.id)
        self.assertEquals('Bob', s.name)
        self.assertEquals('abc', s.descrip)
        self.assertEquals(100, s.age)

        self.assertEquals({'my_name': 'Bob', 'half_age': 50}, s.indexes())

        s.name = 'changed'
        s.age = 2

        self.assertEquals({'my_name': 'changed', 'half_age': 1}, s.indexes())
