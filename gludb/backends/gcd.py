"""gludb.backends.gcd - backend Google Cloud Datastore module
"""

import sys

from ..utils import uuid

if sys.version_info >= (3, 0):
    raise ImportError("GLUDB GCD Backend only supports Python 2.7")

import googledatastore as datastore
# TODO: one day use this instead (when it has Python3 support)
# from gcloud import datastore


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


def make_key(table_name, objid):
    key = datastore.Key()
    path = key.path_element.add()
    path.kind = table_name
    path.name = str(objid)
    return key


def write_rec(table_name, objid, data, index_name_values):
    with DatastoreTransaction() as tx:
        entity = tx.get_upsert()

        entity.key.CopyFrom(make_key(table_name, objid))

        prop = entity.property.add()
        prop.name = 'id'
        prop.value.string_value = objid

        prop = entity.property.add()
        prop.name = 'value'
        prop.value.string_value = data

        for name, val in index_name_values:
            prop = entity.property.add()
            prop.name = name
            prop.value.string_value = str(val)


def extract_entity(found):
    obj = dict()
    for prop in found.entity.property:
        obj[prop.name] = prop.value.string_value
    return obj


def read_rec(table_name, objid):
    req = datastore.LookupRequest()
    req.key.extend([make_key(table_name, objid)])

    for found in datastore.lookup(req).found:
        yield extract_entity(found)


def read_by_indexes(table_name, index_name_values=None):
    req = datastore.RunQueryRequest()

    query = req.query
    query.kind.add().name = table_name

    if not index_name_values:
        index_name_values = []
    for name, val in index_name_values:
        queryFilter = query.filter.property_filter
        queryFilter.property.name = name
        queryFilter.operator = datastore.PropertyFilter.EQUAL
        queryFilter.value.string_value = str(val)

    loop_its = 0
    have_more = True

    while have_more:
        resp = datastore.run_query(req)

        found_something = False
        for found in resp.batch.entity_result:
            yield extract_entity(found)
            found_something = True

        if not found_something:
            # This is a guard against bugs or excessive looping - as long we
            # can keep yielding records we'll continue to execute
            loop_its += 1
            if loop_its > 5:
                raise ValueError("Exceeded the excessive query threshold")

        if resp.batch.more_results != datastore.QueryResultBatch.NOT_FINISHED:
            have_more = False
        else:
            have_more = True
            end_cursor = resp.batch.end_cursor
            query.start_cursor.CopyFrom(end_cursor)


def delete_table(table_name):
    """Mainly for testing"""

    to_delete = [
        make_key(table_name, rec['id'])
        for rec in read_by_indexes(table_name, [])
    ]

    with DatastoreTransaction() as tx:
        tx.get_commit_req().mutation.delete.extend(to_delete)


class Backend(object):
    def __init__(self, **kwrds):
        pass  # No current keywords needed/used

    def ensure_table(self, cls):
        pass  # Currently nothing needs to be done

    def find_one(self, cls, id):
        db_result = None
        for rec in read_rec(cls.get_table_name(), id):
            db_result = rec
            break  # Only read the first returned - which should be all we get
        if not db_result:
            return None

        obj = cls.from_data(db_result['value'])
        return obj

    def find_all(self, cls):
        final_results = []
        for db_result in read_by_indexes(cls.get_table_name(), []):
            obj = cls.from_data(db_result['value'])
            final_results.append(obj)

        return final_results

    def find_by_index(self, cls, index_name, value):
        table_name = cls.get_table_name()
        index_name_vals = [(index_name, value)]

        final_results = []
        for db_result in read_by_indexes(table_name, index_name_vals):
            obj = cls.from_data(db_result['value'])
            final_results.append(obj)

        return final_results

    def save(self, obj):
        if not obj.id:
            obj.id = uuid()

        index_names = obj.__class__.index_names() or []
        index_dict = obj.indexes() or {}
        index_name_values = [
            (key, index_dict.get(key, ''))
            for key in index_names
        ]

        write_rec(
            obj.__class__.get_table_name(),
            obj.id,
            obj.to_data(),
            index_name_values
        )
