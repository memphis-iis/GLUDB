"""Testing gludb.utils functionality
"""

import unittest
import datetime

from gludb.utils import uuid, now_field, parse_now_field


class UtilsTesting(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_uuid(self):
        # Tough to test UUID, but we'll at least make sure a low N count of
        # them are unique and non-empty
        COUNT = 100
        found = set([uuid() for _ in range(COUNT)])
        self.assertEquals(COUNT, len(found))
        self.assertFalse('' in found)

    def assertCloseTimes(self, d1, d2, eps=1.0):
        self.assertTrue(abs((d1 - d2).total_seconds()) < eps)

    def test_now(self):
        # First just make sure that we can accurately create parse date time
        # strings. We just create a low N amount for testing
        COUNT = 100
        for _ in range(COUNT):
            s = now_field()
            d = parse_now_field(s)
            # We assume that we got a parseable date string - we confirm that
            # we got this back by subtracting from a known datetime and then
            # making sure that the difference is sane
            self.assertCloseTimes(d, datetime.datetime.utcnow())

        # Make sure that we work with and without microseconds
        ref = datetime.datetime(2050, 12, 1, 14, 45, 55, 123)

        # with microseconds
        self.assertCloseTimes(
            ref,
            parse_now_field('UTC:' + '2050-12-01T14:45:55.000123')
        )

        # withOUT microseconds
        self.assertCloseTimes(
            ref,
            parse_now_field('UTC:' + '2050-12-01T14:45:55')
        )
