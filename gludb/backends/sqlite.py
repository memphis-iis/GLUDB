"""gludb.backends.sqlite - backend sqlite database module
"""

import sqlite3


class Backend(object):
    def __init__(self, **kwrds):
        self.filename = kwrds.get('filename', '')
        if not self.filename:
            raise ValueError('sqlite backend requires a filename parameter')

        self.conn = sqlite3.connect(self.filename)

    def ensure_table(self, cls):
        cur = self.conn.cursor()

        cur.execute(
            'create table if not exists ' + cls.get_table_name() +
            ' (id text primary key, value text)'
        )
        self.conn.commit()
        cur.close()

    def find_one(self, cls, id):
        cur = self.conn.cursor()

        cur.execute(
            'select id,value from ' + cls.get_table_name() + ' where id = ?',
            (id,)
        )

        rec = cur.fetchone()
        id, data = rec[0], rec[1]
        obj = cls.from_data(data)
        assert id == obj.id

        cur.close()

        return obj

    def find_all(self, cls):
        cur = self.conn.cursor()

        found = []
        for row in cur.execute('select id,value from ' + cls.get_table_name()):
            id, data = row[0], row[1]
            obj = cls.from_data(data)
            assert id == obj.id
            found.append(obj)

        cur.close()

        return found

    def save(self, obj):
        cur = self.conn.cursor()

        tabname = obj.__class__.get_table_name()

        if not obj.id:
            id = "TODO: uuid"  # TODO: actual UUID
            obj.id = id

        cur.execute(
            'insert or replace into ' + tabname + '(id,value) values (?, ?)',
            (obj.id, obj.to_data())
        )
        self.conn.commit()

        cur.close()
