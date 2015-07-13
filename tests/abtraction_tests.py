import unittest

import gludb.annotations
import gludb.versioning


@gludb.annotations.DBObject(
    table_name='SimpleTest',
    versioning=gludb.versioning.NONE
)
class SimpleData(object):
    pass


class BasicAbstractionTesting(unittest.TestCase):
    def setUp(self):
        self.simple = SimpleData()

    def test_persist_simple(self):
        data = self.simple.to_data()
        simple2 = SimpleData.from_data(data)
        self.assertEquals(self.simple, simple2)
