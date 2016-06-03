"""gludb.backends.postgresql - backend postgresql database module."""

# pylama:ignore=E501

import threading

import psycopg2

from ..utils import uuid


class Backend(object):
    """PostgreSQL backend for gludb."""

    def __init__(self, **kwrds):
        """Ctor requires conn_string to be specified."""
        self.conn_string = kwrds.get('conn_string', '')
        if not self.conn_string:
            raise ValueError('postgresql backend requires a conn_string parameter')

        # We technically don't need a conn per thread (since psycopg2 is
        # thread-safe), but this should give us a balance between a connection
        # per request (lots of TCP/SSL connections) and one global connection
        # (all transactions for this process get serialized)
        self.thread_local = threading.local()
        self._conn()

    def _conn(self):
        conn = getattr(self.thread_local, "conn", None)

        if not conn:
            conn = psycopg2.connect(self.conn_string)
            self.thread_local.conn = conn

        return conn

    def ensure_table(self, cls):
        """Ensure table's existence - as per the gludb spec."""
        id_len = len(uuid())
        index_names = cls.index_names() or []
        cols = [
            'id char(%d) primary key' % (id_len,),
            'value jsonb'
        ] + [
            name + ' text' for name in index_names
        ]

        table_name = cls.get_table_name()

        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute('create table if not exists %s (%s);' % (
                    table_name,
                    ','.join(cols)
                ))
                for name in index_names:
                    cur.execute('create index if not exists %s on %s(%s);' % (
                        table_name + '_' + name + '_idx',
                        table_name,
                        name
                    ))
        # End of conn with - transction should commit here if not exception

    def find_one(self, cls, id):
        """Find single keyed row - as per the gludb spec."""
        found = self.find_by_index(cls, 'id', id)
        return found[0] if found else None

    def find_all(self, cls):
        """Find all rows - as per the gludb spec."""
        return self.find_by_index(cls, '1', 1)

    def find_by_index(self, cls, index_name, value):
        """Find all rows matching index query - as per the gludb spec."""
        cur = self._conn().cursor()

        # psycopg2 supports using Python formatters for queries
        # we also request our JSON as a string for the from_data calls
        query = 'select id, value::text from {0} where {1} = %s;'.format(
            cls.get_table_name(),
            index_name
        )

        found = []
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (value,))
                for row in cur:
                    id, data = str(row[0]).strip(), row[1]
                    obj = cls.from_data(data)
                    assert id == obj.id
                    found.append(obj)

        return found

    def save(self, obj):
        """Save current instance - as per the gludb spec."""
        cur = self._conn().cursor()

        tabname = obj.__class__.get_table_name()

        index_names = obj.__class__.index_names() or []

        col_names = ['id', 'value'] + index_names
        value_holders = ['%s'] * len(col_names)
        updates = ['%s = EXCLUDED.%s' % (cn, cn) for cn in col_names[1:]]

        if not obj.id:
            id = uuid()
            obj.id = id

        query = 'insert into {0} ({1}) values ({2}) on conflict(id) do update set {3};'.format(
            tabname,
            ','.join(col_names),
            ','.join(value_holders),
            ','.join(updates),
        )

        values = [obj.id, obj.to_data()]

        index_vals = obj.indexes() or {}
        values += [index_vals.get(name, 'NULL') for name in index_names]

        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, tuple(values))

    def delete(self, obj):
        """Required functionality."""
        del_id = obj.get_id()
        if not del_id:
            return

        cur = self._conn().cursor()

        tabname = obj.__class__.get_table_name()
        query = 'delete from {0} where id = %s;'.format(tabname)

        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (del_id,))
