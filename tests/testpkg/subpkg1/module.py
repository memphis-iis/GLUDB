from gludb.simple import DBObject, Field


@DBObject(table_name='MidDataOne')
class MidData1(object):
    name = Field('name')
