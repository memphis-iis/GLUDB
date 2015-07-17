"""gludb.backends.sqlite - backend sqlite database module
"""

import sqlite3


class Backend(object):
    def __init__(self, **kwrds):
        self.filename = kwrds.get('filename', '')
        if not self.filename:
            raise ValueError('sqlite backend requires a filename parameter')

    def ensure_table(self, cls):
        conn = sqlite3.connect(self.filename)
        cur = conn.cursor()

        cur.execute(
            'create table if not exists ' + cls.get_table_name() +
            ' (id text primary key, value text)'
        )
        conn.commit()

        cur.close()
        conn.close()

    def find_one(self, cls, id):
        conn = sqlite3.connect(self.filename)
        cur = conn.cursor()

        cur.execute(
            'select id,value from ' + cls.get_table_name() + ' where id = ?',
            id
        )

        rec = cur.fetchone()
        id, data = rec[0], rec[1]
        obj = cls.from_data(data)
        assert id == obj.id

        cur.close()
        conn.close()

        return obj

    def find_all(self, cls):
        found = []

        conn = sqlite3.connect(self.filename)
        cur = conn.cursor()

        for row in cur.execute('select id,value from ' + cls.get_table_name()):
            id, data = row[0], row[1]
            obj = cls.from_data(data)
            assert id == obj.id
            found.append(obj)

        cur.close()
        conn.close()

        return found

    def save(self, obj):
        conn = sqlite3.connect(self.filename)
        cur = conn.cursor()

        tabname = obj.__class__.get_table_name()

        if not obj.id:
            id = "TODO: uuid"  # TODO: actual UUID
            obj.id = id

        cur.execute(
            'insert or replace into ' + tabname + '(id,value) values (?, ?)',
            (obj.id, obj.to_data())
        )
        conn.commit()

        cur.close()
        conn.close()
