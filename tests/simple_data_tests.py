"""Testing all the functionality in gludb.simple *except* for actual
data storage (that's in simple_data_tests.py)
"""

import unittest

import gludb.config
import gludb.versioning

from gludb.simple import DBObject, Field


@DBObject(table_name='SimpleStorageTest', versioning=gludb.versioning.NONE)
class SimpleStorage(object):
    name = Field('default name')
    descrip = Field()
    age = Field(42)

SQLITE_MEMORY = gludb.config.Database('sqlite', filename=':memory:')


class DefaultStorageTesting(unittest.TestCase):
    def setUp(self):
        gludb.config.default_database(SQLITE_MEMORY)
        SimpleStorage.ensure_table()

    def tearDown(self):
        # Undo any database setup
        gludb.config.clear_database_config()

    def assertReadable(self, obj):
        self.assertEquals(
            obj.to_data(),
            obj.__class__.find_one(obj.id).to_data()
        )

    def test_readwrite(self):
        s = SimpleStorage(name='Pre', descrip='Testing', age=-1)
        self.assertEquals('', s.id)
        self.assertEquals('Pre', s.name)
        self.assertEquals('Testing', s.descrip)
        self.assertEquals(-1, s.age)

        s.save()
        self.assertTrue(len(s.id) > 0)
        self.assertReadable(s)

        s2 = SimpleStorage(id=s.id, name='Post', descrip='AtItAgain', age=256)
        s2.save()
        self.assertReadable(s2)

        all_recs = SimpleStorage.find_all()
        self.assertEqual(1, len(all_recs))
        self.assertEquals(s2.to_data(), all_recs[0].to_data())


# Same tests as DefaultStorageTesting but with differnt setUp/tearDown
class SpecificStorageTesting(DefaultStorageTesting):
    def setUp(self):
        gludb.config.default_database(None)  # no default database
        gludb.config.class_database(SimpleStorage, SQLITE_MEMORY)
        SimpleStorage.ensure_table()

    def tearDown(self):
        # Undo any database setup
        gludb.config.clear_database_config()
