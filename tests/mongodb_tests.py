"""Testing for mongodb backend"""

import unittest

import gludb.config

from simple_data_tests import SimpleStorage, DefaultStorageTesting
from index_tests import IndexReadWriteTesting, IndexedData


def delete_test_colls():
    gludb.backends.mongodb.delete_collection(
        'gludb_testing',
        SimpleStorage.get_table_name()
    )
    gludb.backends.mongodb.delete_collection(
        'gludb_testing',
        IndexedData.get_table_name()
    )


class SpecificStorageTesting(DefaultStorageTesting):
    def setUp(self):
        gludb.config.default_database(None)  # no default database
        gludb.config.class_database(SimpleStorage, gludb.config.Database(
            'mongodb',
            mongo_url='mongodb://localhost:27017/gludb_testing'
        ))
        delete_test_colls()
        SimpleStorage.ensure_table()

    def tearDown(self):
        # Undo any database setup
        delete_test_colls()
        gludb.config.clear_database_config()


class MongoDBIndexReadWriteTesting(IndexReadWriteTesting):
    def setUp(self):
        gludb.config.default_database(gludb.config.Database(
            'mongodb',
            mongo_url='mongodb://localhost:27017/gludb_testing'
        ))
        delete_test_colls()
        IndexedData.ensure_table()

    def tearDown(self):
        delete_test_colls()
        gludb.config.clear_database_config()


class CollectionCreationTesting(unittest.TestCase):
    def setUp(self):
        gludb.config.default_database(gludb.config.Database(
            'mongodb',
            mongo_url='mongodb://localhost:27017/gludb_testing'
        ))
        delete_test_colls()

    def tearDown(self):
        # Undo any database setup
        delete_test_colls()
        gludb.config.clear_database_config()

    def test_repeated_creates(self):
        SimpleStorage.ensure_table()
        SimpleStorage.ensure_table()
        SimpleStorage.ensure_table()

        IndexedData.ensure_table()
        IndexedData.ensure_table()
        IndexedData.ensure_table()
