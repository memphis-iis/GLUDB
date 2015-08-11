"""Testing for dynamodb backend"""

import gludb.config

from simple_data_tests import SimpleStorage, DefaultStorageTesting
from index_tests import IndexReadWriteTesting, IndexedData


class SpecificStorageTesting(DefaultStorageTesting):
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


class DynamoDBIndexReadWriteTesting(IndexReadWriteTesting):
    def setUp(self):
        gludb.config.default_database(gludb.config.Database('dynamodb'))
        IndexedData.ensure_table()

    def tearDown(self):
        # Undo any database setup
        gludb.backends.dynamodb.delete_table(
            IndexedData.get_table_name()
        )
        gludb.config.clear_database_config()
