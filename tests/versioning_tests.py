"""Insure that we handle versioning OK
"""

import unittest
import json

from gludb.versioning import _isstr, record_diff, record_patch

# TODO: test append_diff_hist and parse_diff_hist

class InternalUtilTesting(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_str(self):
        self.assertTrue(_isstr(""))
        self.assertTrue(_isstr("aaa"))
        self.assertFalse(_isstr(None))
        self.assertFalse(_isstr(12))
        self.assertFalse(_isstr(dict()))


class RawDiffTesting(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def assertDiffable(self, old, new):
        diff = record_diff(old, new)
        recover = record_patch(new, diff)

        def cmpfilt(o):
            return json.loads(o) if _isstr(o) else o
        self.assertEquals(recover, cmpfilt(recover))

        if old == new:
            self.assertEquals(cmpfilt(new), cmpfilt(recover))
        else:
            self.assertNotEquals(cmpfilt(new), cmpfilt(recover))

        print("OLD:%s NEW:%s DIFF:%s RECOVER:%s" % (old, new, diff, recover))

    def test_strings(self):
        self.assertDiffable('{}', '{}')
        self.assertDiffable('{}', '{"a":1, "b":2}')
        self.assertDiffable('{"a":1, "b":2}', '{}')
        self.assertDiffable('{"a":1, "b":2}', '{"a":11, "b":22}')

    def test_objs(self):
        self.assertDiffable(dict(), dict())
        self.assertDiffable(dict(), {'a': 1, 'b': 2})
        self.assertDiffable({'a': 1, 'b': 2}, dict())
        self.assertDiffable({'a': 1, 'b': 2}, {'a': 11, 'b': 22})
