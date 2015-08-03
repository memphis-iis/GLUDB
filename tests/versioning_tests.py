"""Insure that we handle versioning OK
"""

import unittest
import json

from gludb.versioning import (
    _isstr,
    record_diff,
    record_patch,
    append_diff_hist,
    parse_diff_hist
)


def cmpfilt(o):
    return json.loads(o) if _isstr(o) else o


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


class DiffHistoryTesting(unittest.TestCase):
    def setUp(self):
        self.start = {'a':1, 'b':11, 'c':111}
        self.mid1 = {'a':2, 'b':22, 'c':222}
        self.mid2 = {'a':3, 'b':33, 'c':333}
        self.final = {'a':4, 'b':44, 'c':444}
        self.series = [self.start, self.mid1, self.mid2, self.final]

    def tearDown(self):
        pass

    def test_empty_history(self):
        diff_hist = []
        obj_hist = list(parse_diff_hist(self.start, diff_hist))

        self.assertEquals(1, len(obj_hist))
        self.assertEquals(self.start, obj_hist[0][0])
        self.assertIsNone(obj_hist[0][1])

    def test_full_history(self):
        diff_hist = []
        last_obj = self.series[0]
        for obj in self.series[1:]:
            diff = record_diff(last_obj, obj)
            diff_hist = append_diff_hist(diff, diff_hist)
            last_obj = obj

        obj_hist = list(parse_diff_hist(self.final, diff_hist))
        self.assertEquals(4, len(obj_hist))
        obj_list = list(reversed([ver for ver,verdate in obj_hist]))
        self.assertEquals(self.series, obj_list)
