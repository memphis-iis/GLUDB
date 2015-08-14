"""MongoDB backend
"""

import json

from pymongo import MongoClient
from pymongo.errors import CollectionInvalid

from ..utils import uuid


def delete_collection(db_name, collection_name, host='localhost', port=27017):
    """Almost exclusively for testing"""
    client = MongoClient("mongodb://%s:%d" % (host, port))
    client[db_name].drop_collection(collection_name)


class Backend(object):
    def __init__(self, **kwrds):
        self.mongo_url = kwrds.get('mongo_url', 'mongodb://localhost:27017')
        self.mongo_client = MongoClient(self.mongo_url)

    def get_collection(self, collection_name):
        return self.mongo_client.get_default_database()[collection_name]

    def ensure_table(self, cls):
        coll_name = cls.get_table_name()
        try:
            db = self.mongo_client.get_default_database()
            db.create_collection(coll_name)
        except CollectionInvalid:
            pass  # Expected if collection already exists

        # Make sure we have indexes
        coll = self.get_collection(coll_name)
        for idx_name in cls.index_names():
            coll.ensure_index(idx_name)

    def _find(self, cls, query):
        coll = self.get_collection(cls.get_table_name())

        final_results = []
        for db_result in coll.find(query):
            # We need to give JSON to from_data
            obj_data = json.dumps(db_result['value'])
            obj = cls.from_data(obj_data)
            final_results.append(obj)

        return final_results

    def find_one(self, cls, id):
        one = self._find(cls, {"_id": id})
        if not one:
            return None
        return one[0]

    def find_all(self, cls):
        return self._find(cls, {})

    def find_by_index(self, cls, index_name, value):
        return self._find(cls, {index_name: str(value)})

    def save(self, obj):
        if not obj.id:
            obj.id = uuid()

        stored_data = {
            '_id': obj.id,
            'value': json.loads(obj.to_data())
        }

        index_vals = obj.indexes() or {}
        for key in obj.__class__.index_names() or []:
            val = index_vals.get(key, '')
            stored_data[key] = str(val)

        coll = self.get_collection(obj.__class__.get_table_name())
        coll.update({"_id": obj.id}, stored_data, upsert=True)
