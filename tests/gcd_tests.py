"""Testing for Google Cloud Datastore backend"""

import sys
import gludb.config

if sys.version_info < (3, 0):
    from .simple_data_tests import SimpleStorage, DefaultStorageTesting
    from .index_tests import IndexReadWriteTesting, IndexedData

    class SpecificStorageTesting(DefaultStorageTesting):
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

    # class GCDIndexReadWriteTesting(IndexReadWriteTesting):
    #     def setUp(self):
    #         gludb.config.default_database(gludb.config.Database('gcd'))
    #         IndexedData.ensure_table()
    #
    #     def tearDown(self):
    #         # Undo any database setup
    #         gludb.backends.gcd.delete_table(
    #             IndexedData.get_table_name()
    #         )
    #         gludb.config.clear_database_config()
else:
    import unittest

    class VersionSpecificGCDTesting(unittest.TestCase):
        def test_no_import(self):
            def import_gcd():
                gludb.config.default_database(gludb.config.Database('gcd'))
            self.assertRaises(ImportError, import_gcd)
