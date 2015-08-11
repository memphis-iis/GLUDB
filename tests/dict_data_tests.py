"""Testing gludb.simple classes with complex data (dictionaries)
"""

import unittest

from gludb.simple import DBObject, Field

from utils import compare_data_objects


@DBObject(table_name='SetupTest')
class ComplexData(object):
    name = Field('')
    complex_data = Field(dict)


class ComplexDataTesting(unittest.TestCase):
    def setUp(self):
        pass

    def assertObjEq(self, obj1, obj2):
        self.assertTrue(compare_data_objects(obj1, obj2))

    def test_fields(self):
        s = ComplexData()
        self.assertEquals('', s.id)
        self.assertEquals('', s.name)
        self.assertEquals({}, s.complex_data)

        s = ComplexData(name='Bob', complex_data={'a': 123, 'b': 345})
        self.assertEquals('', s.id)
        self.assertEquals('Bob', s.name)
        self.assertEquals({'a': 123, 'b': 345}, s.complex_data)

    def test_persistence(self):
        s = ComplexData(name='Bob', complex_data={'a': 123, 'b': 345})
        s2 = ComplexData.from_data(s.to_data())
        self.assertObjEq(s, s2)

        self.assertEquals('', s2.id)
        self.assertEquals('Bob', s2.name)
        self.assertEquals({'a': 123, 'b': 345}, s2.complex_data)

    def test_prop_sets(self):
        s = ComplexData(name='Bob')
        s.complex_data['a'] = 123
        s.complex_data['b'] = 456
        s2 = ComplexData.from_data(s.to_data())
        self.assertEquals({'a': 123, 'b': 456}, s2.complex_data)
