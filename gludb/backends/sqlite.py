"""gludb.backends.sqlite - backend sqlite database module."""

import threading

import sqlite3

from ..utils import uuid


class Backend(object):
    """SQLite backend for gludb."""

    def __init__(self, **kwrds):
        """Ctor requires filename to be specified."""
        self.filename = kwrds.get('filename', '')
        if not self.filename:
            raise ValueError('sqlite backend requires a filename parameter')

        # sqlite requires one connection per thread in Python
        self.thread_local = threading.local()

        conn = getattr(self.thread_local, "conn", None)
        if not conn:
            self.thread_local.conn = sqlite3.connect(self.filename)

    def ensure_table(self, cls):
        """Ensure table's existence - as per the gludb spec."""
        cur = self.thread_local.conn.cursor()

        table_name = cls.get_table_name()
        index_names = cls.index_names() or []

        cols = ['id text primary key', 'value text']
        for name in index_names:
            cols.append(name + ' text')

        cur.execute('create table if not exists %s (%s)' % (
            table_name,
            ','.join(cols)
        ))

        for name in index_names:
            cur.execute('create index if not exists %s on %s(%s)' % (
                table_name + '_' + name + '_idx',
                table_name,
                name
            ))

        self.thread_local.conn.commit()
        cur.close()

    def find_one(self, cls, id):
        """Find single keyed row - as per the gludb spec."""
        found = self.find_by_index(cls, 'id', id)
        return found[0] if found else None

    def find_all(self, cls):
        """Find all rows - as per the gludb spec."""
        return self.find_by_index(cls, '1', 1)

    def find_by_index(self, cls, index_name, value):
        """Find all rows matching index query - as per the gludb spec."""
        cur = self.thread_local.conn.cursor()

        query = 'select id,value from %s where %s = ?' % (
            cls.get_table_name(),
            index_name
        )

        found = []
        for row in cur.execute(query, (value,)):
            id, data = row[0], row[1]
            obj = cls.from_data(data)
            assert id == obj.id
            found.append(obj)

        cur.close()

        return found

    def save(self, obj):
        """Save current instance - as per the gludb spec."""
        cur = self.thread_local.conn.cursor()

        tabname = obj.__class__.get_table_name()

        index_names = obj.__class__.index_names() or []

        col_names = ['id', 'value'] + index_names
        value_holders = ','.join(['?' * len(col_names)])

        if not obj.id:
            id = uuid()
            obj.id = id

        query = 'insert or replace into %s (%s) values (%s)' % (
            tabname,
            ','.join(col_names),
            ','.join(value_holders)
        )

        values = [obj.id, obj.to_data()]

        index_vals = obj.indexes() or {}
        values += [index_vals.get(name, 'NULL') for name in index_names]

        cur.execute(query, tuple(values))
        self.thread_local.conn.commit()

        cur.close()
