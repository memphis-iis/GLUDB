"""gludb.backends.dynamodb - backend dynamodb database module
"""

import os

from uuid import uuid4

import boto.exception
import boto.dynamodb2  # NOQA

from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.table import Table
from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.items import Item
from boto.dynamodb2.exceptions import ResourceNotFoundException, ItemNotFound
from boto.exception import JSONResponseError


def uuid():
    return uuid4().hex


def get_conn():
    """Return a connection to DynamoDB (and handle local/debug possibilities)
    """
    if os.environ.get('DEBUG', None):
        # In DEBUG mode - use the local DynamoDB
        conn = DynamoDBConnection(
            host='localhost',
            port=8000,
            aws_access_key_id='TEST',
            aws_secret_access_key='TEST',
            is_secure=False
        )
    elif os.environ.get('travis', None):
        # TODO: we need a mocking library for DynamoDB that we can use
        #       on Travis CI. (ddbmock is Python 2.7 only)
        conn = None
    else:
        # Regular old production
        conn = DynamoDBConnection()

    return conn


def delete_table(table_name):
    """Mainly for testing"""
    Table(table_name, connection=get_conn(), schema=[HashKey('id')]).delete()


class Backend(object):
    def __init__(self, **kwrds):
        pass  # No current keywords needed/used

    def ensure_table(self, cls):
        exists = True
        conn = get_conn()
        table_name = cls.get_table_name()
        try:
            descrip = conn.describe_table(table_name)
            assert descrip is not None
        except ResourceNotFoundException:
            # Expected - this is what we get if there is no table
            exists = False
        except JSONResponseError:
            # Also assuming no table
            exists = False

        if exists:
            return  # Nothing to do

        # TODO: indexes
        table = Table.create(
            table_name,
            connection=get_conn(),
            schema=[HashKey('id')]
        )
        assert table is not None

    def get_class_table(self, cls):
        """Return a DynamoDB table object for the given class
        """
        return Table(
            cls.get_table_name(),
            connection=get_conn(),
            schema=[HashKey('id')]
        )
        # TODO: indexes

    def find_one(self, cls, id):
        try:
            db_result = self.get_class_table(cls).lookup(id)
        except ItemNotFound:
            # according to docs, this shouldn't be required, but it IS
            db_result = None

        if not db_result:
            return None

        obj = cls.from_data(db_result['value'])
        return obj

    def find_all(self, cls):
        final_results = []
        table = self.get_class_table(cls)
        for db_result in table.scan():
            obj = cls.from_data(db_result['value'])
            final_results.append(obj)

        return final_results

    def find_by_index(self, cls, index_name, value):
        return []  # TODO: indexes

    def save(self, obj):
        if not obj.id:
            obj.id = uuid()

        table = self.get_class_table(obj.__class__)
        item = Item(table, data={
            'id': obj.id,
            'value': obj.to_data()
        })

        # TODO: indexes

        item.save(overwrite=True)
