"""Testing for postgresql backend."""

# pylama:ignore=D101,D102,D103,E501

import os

import unittest

import gludb.config

import simple_data_tests
from simple_data_tests import SimpleStorage

import index_tests
from index_tests import IndexedData

if os.environ.get('travis', False):
    # Testing on travis CI
    PG_CONN_STR = "host='localhost' dbname='gludb_test' user='postgres'"
elif os.environ.get('IN_DOCKER', False):
    # Testing with the Dockerfile
    PG_CONN_STR = "host='localhost' dbname='docker' user='docker' password='docker'"
else:
    # Workstation/local testing
    # TODO: let this be locally configurable
    PG_CONN_STR = "host='localhost' dbname='test' user='test' password='S#jp/hYlxKYB'"


def delete_test_tables():
    import psycopg2
    with psycopg2.connect(PG_CONN_STR) as conn:
        with conn.cursor() as cur:
            cur.execute("drop table if exists " + SimpleStorage.get_table_name())
            cur.execute("drop table if exists " + IndexedData.get_table_name())


# TODO: check https://github.com/travis-ci/travis-ci/issues/4264 to see we we can remove this
# Sadly, Travis CI doesn't support PostgresSQL 9.5 - 9.4 doesn't support 2
# features that we use: upserts and "if not exists" for index creation
if not os.environ.get('travis', False):
    class SpecificStorageTesting(simple_data_tests.DefaultStorageTesting):
        def setUp(self):
            gludb.config.default_database(None)  # no default database
            gludb.config.class_database(SimpleStorage, gludb.config.Database(
                'postgresql',
                conn_string=PG_CONN_STR
            ))
            delete_test_tables()
            SimpleStorage.ensure_table()

        def tearDown(self):
            # Undo any database setup
            delete_test_tables()
            gludb.config.clear_database_config()

    class PostgreSQLIndexReadWriteTesting(index_tests.IndexReadWriteTesting):
        def setUp(self):
            gludb.config.default_database(gludb.config.Database(
                'postgresql',
                conn_string=PG_CONN_STR
            ))
            delete_test_tables()
            IndexedData.ensure_table()

        def tearDown(self):
            delete_test_tables()
            gludb.config.clear_database_config()

    class CollectionCreationTesting(unittest.TestCase):
        def setUp(self):
            gludb.config.default_database(gludb.config.Database(
                'postgresql',
                conn_string=PG_CONN_STR
            ))
            delete_test_tables()

        def tearDown(self):
            # Undo any database setup
            delete_test_tables()
            gludb.config.clear_database_config()

        def test_repeated_creates(self):
            SimpleStorage.ensure_table()
            SimpleStorage.ensure_table()
            SimpleStorage.ensure_table()

            IndexedData.ensure_table()
            IndexedData.ensure_table()
            IndexedData.ensure_table()
