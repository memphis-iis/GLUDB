"""Testing for Google Cloud Datastore backend."""

# pylama:ignore=D101,D102

import sys
import gludb.config

from gludb.data import DeleteNotSupported

if sys.version_info < (3, 0):
    import simple_data_tests
    from simple_data_tests import SimpleStorage

    import index_tests
    from index_tests import IndexedData

    class SpecificStorageTesting(simple_data_tests.DefaultStorageTesting):
        def setUp(self):
            gludb.config.default_database(None)  # no default database
            gludb.config.class_database(SimpleStorage, gludb.config.Database(
                'gcd'
            ))
            SimpleStorage.ensure_table()

        def tearDown(self):
            # Undo any database setup
            gludb.backends.gcd.delete_table(
                SimpleStorage.get_table_name()
            )
            gludb.config.clear_database_config()

        def test_delete(self):
            s = SimpleStorage()
            self.assertRaises(DeleteNotSupported, s.delete)

    class GCDIndexReadWriteTesting(index_tests.IndexReadWriteTesting):
        def setUp(self):
            gludb.config.default_database(gludb.config.Database('gcd'))
            IndexedData.ensure_table()

        def tearDown(self):
            # Undo any database setup
            gludb.backends.gcd.delete_table(
                IndexedData.get_table_name()
            )
            gludb.config.clear_database_config()
else:
    import unittest

    class VersionSpecificGCDTesting(unittest.TestCase):
        def test_no_import(self):
            def import_gcd():
                gludb.config.default_database(gludb.config.Database('gcd'))
            self.assertRaises(ImportError, import_gcd)
