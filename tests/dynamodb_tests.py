"""Testing for dynamodb backend."""

# pylama:ignore=D101,D102

import gludb.config
from gludb.data import DeleteNotSupported

import simple_data_tests
from simple_data_tests import SimpleStorage

import index_tests
from index_tests import IndexedData


class SpecificStorageTesting(simple_data_tests.DefaultStorageTesting):
    def setUp(self):
        gludb.config.default_database(None)  # no default database
        gludb.config.class_database(SimpleStorage, gludb.config.Database(
            'dynamodb'
        ))
        SimpleStorage.ensure_table()

    def tearDown(self):
        # Undo any database setup
        gludb.backends.dynamodb.delete_table(
            SimpleStorage.get_table_name()
        )
        gludb.config.clear_database_config()

    def test_delete(self):
        s = SimpleStorage()
        self.assertRaises(DeleteNotSupported, s.delete)


class DynamoDBIndexReadWriteTesting(index_tests.IndexReadWriteTesting):
    def setUp(self):
        gludb.config.default_database(gludb.config.Database('dynamodb'))
        IndexedData.ensure_table()

    def tearDown(self):
        # Undo any database setup
        gludb.backends.dynamodb.delete_table(
            IndexedData.get_table_name()
        )
        gludb.config.clear_database_config()
