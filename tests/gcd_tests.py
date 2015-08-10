"""Testing for Google Cloud Datastore backend"""

import sys

if sys.version_info < (3, 0):
    # Sad, but true - gcd currently only runs under Python 2.7
    import unittest

    import json

    import googledatastore as datastore

    # TODO: one day use this instead (when it has Python3 support)
    # from gcloud import datastore

    ENTITY_KIND = "TestingObject"

    def make_key(objid):
        key = datastore.Key()
        path = key.path_element.add()
        path.kind = ENTITY_KIND
        path.name = str(objid)
        return key

    class DatastoreTransaction(object):
        def __init__(self):
            self.tx = None
            self.commit_req = None

        def __enter__(self):
            req = datastore.BeginTransactionRequest()
            resp = datastore.begin_transaction(req)
            self.tx = resp.transaction
            return self

        def get_commit_req(self):
            if not self.commit_req:
                self.commit_req = datastore.CommitRequest()
                self.commit_req.transaction = self.tx
            return self.commit_req

        def get_upsert(self):
            return self.get_commit_req().mutation.upsert.add()

        def __exit__(self, type, value, traceback):
            if self.commit_req:
                datastore.commit(self.commit_req)
                self.commit_req = None

            if self.tx:
                # Simple, but we might want to log or troubleshoot one day
                self.tx = None

    def write_something(objid, name, descrip_dict):
        with DatastoreTransaction() as tx:
            entity = tx.get_upsert()
            entity.key.CopyFrom(make_key(objid))

            prop = entity.property.add()
            prop.name = 'objname'
            prop.value.string_value = str(name)

            prop = entity.property.add()
            prop.name = 'objvalue'
            prop.value.string_value = json.dumps(descrip_dict)

    def extract_entity(found):
        obj = dict()
        for prop in found.entity.property:
            obj[prop.name] = prop.value.string_value
        return obj

    def read_something(objid):
        req = datastore.LookupRequest()
        req.key.extend([make_key(objid)])

        for found in datastore.lookup(req).found:
            yield extract_entity(found)

    def read_by_name(name):
        req = datastore.RunQueryRequest()

        query = req.query
        query.kind.add().name = ENTITY_KIND
        queryFilter = query.filter.property_filter
        queryFilter.property.name = 'objname'
        queryFilter.operator = datastore.PropertyFilter.EQUAL
        queryFilter.value.string_value = str(name)

        loop_its = 0
        have_more = True

        while have_more:
            resp = datastore.run_query(req)

            found_something = False
            for found in resp.batch.entity_result:
                yield extract_entity(found)
                found_something = True

            if not found_something:
                # This is a guard against bugs or excessive looping - as long
                # we can keep yielding records we'll continue to execute
                loop_its += 1
                if loop_its > 5:
                    raise ValueError("Exceeded the excessive query threshold")

            mr = resp.batch.more_results
            if mr != datastore.QueryResultBatch.NOT_FINISHED:
                have_more = False
            else:
                have_more = True
                end_cursor = resp.batch.end_cursor
                query.start_cursor.CopyFrom(end_cursor)

    def dump_read(title, results):
        print(title)
        reccount = 0
        for obj in results:
            print('ObjFound: ' + repr(obj))
            reccount += 1
        print("...All done: %d recs" % (reccount,))
        print("")

    class DummyTest(unittest.TestCase):
        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_readwrite(self):
            write_something('id1', 'my_name', {'a': 1, 'b': 1})
            print('Write 1 performed')
            dump_read('key read for id1', read_something('id1'))

            write_something('id1', 'my_name', {'a': 2, 'b': 2})
            print('Write 2 performed')
            dump_read('key read for id1', read_something('id1'))

            dump_read('key read for missing id', read_something('id_missing'))

            dump_read('query for name', read_by_name('my_name'))
            dump_read('query for wrong name', read_by_name('no name'))

            print("Writing 50 records with name batchname")
            for i in range(50):
                write_something('id%d' % i, 'batchname', {'a': i, 'b': i})
            dump_read('query for batch name', read_by_name('batchname'))

OLD_CODE_TO_BE_CHANGED = """
    import gludb.config

    from .simple_data_tests import SimpleStorage, DefaultStorageTesting
    from .index_tests import IndexReadWriteTesting, IndexedData


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
"""
