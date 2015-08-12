from gludb.simple import DBObject, Field


@DBObject(table_name='BottomData')
class BottomData(object):
    name = Field('name')
