"""Testing all the functionality in gludb.simple *except* for actual
data storage (that's in simple_data_tests.py)
"""

import unittest

import gludb.config

from gludb.simple import DBObject, Field, Index

from utils import compare_data_objects


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
        return int(self.age/2)

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

        self.assertEquals(
            ['half_age', 'my_name'],
            sorted(IndexedData.index_names())
        )

        self.assertEquals({'my_name': 'Bob', 'half_age': 50}, s.indexes())

        s.name = 'changed'
        s.age = 2

        self.assertEquals({'my_name': 'changed', 'half_age': 1}, s.indexes())


class IndexReadWriteTesting(unittest.TestCase):
    def setUp(self):
        gludb.config.default_database(gludb.config.Database(
            'sqlite',
            filename=':memory:'
        ))
        IndexedData.ensure_table()

    def tearDown(self):
        # Undo any database setup
        gludb.config.clear_database_config()

    def assertObjEq(self, obj1, obj2):
        self.assertTrue(compare_data_objects(obj1, obj2))

    def assertReadable(self, obj):
        self.assertObjEq(obj, obj.__class__.find_one(obj.id))

    def test_readwrite(self):
        s = IndexedData(name='Pre', descrip='Testing', age=10)
        self.assertEquals('', s.id)
        self.assertEquals('Pre', s.name)
        self.assertEquals('Testing', s.descrip)
        self.assertEquals(10, s.age)

        s.save()
        self.assertTrue(len(s.id) > 0)
        self.assertReadable(s)

        s2 = IndexedData(id=s.id, name='Post', descrip='AtItAgain', age=256)
        s2.save()
        self.assertReadable(s2)

        all_recs = IndexedData.find_all()
        self.assertEqual(1, len(all_recs))
        self.assertObjEq(s2, all_recs[0])

        idx_recs = IndexedData.find_by_index('half_age', 128)
        self.assertEqual(1, len(idx_recs))
        self.assertObjEq(s2, idx_recs[0])

        idx_recs = IndexedData.find_by_index('my_name', 'Post')
        self.assertEqual(1, len(idx_recs))
        self.assertObjEq(s2, idx_recs[0])

        self.assertEqual(0, len(IndexedData.find_by_index('half_age', 0)))
        self.assertEqual(0, len(IndexedData.find_by_index('my_name', '')))
