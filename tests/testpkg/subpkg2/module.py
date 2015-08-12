from gludb.simple import DBObject, Field


@DBObject(table_name='MidDataTwo')
class MidData2(object):
    name = Field('name')
