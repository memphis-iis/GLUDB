from gludb.simple import DBObject, Field


@DBObject(table_name='TopData')
class TopData(object):
    name = Field('name')
