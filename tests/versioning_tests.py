"""Insure that we handle versioning OK
"""

import unittest
import json

import gludb.config

from gludb.simple import DBObject, Field

from gludb.versioning import (
    _isstr,
    record_diff,
    record_patch,
    append_diff_hist,
    parse_diff_hist,
    VersioningTypes
)

from utils import compare_data_objects


@DBObject(
    table_name='VersionedDataTest',
    versioning=VersioningTypes.DELTA_HISTORY
)
class VersionedData(object):
    name = Field('default name')
    descrip = Field()
    age = Field(42)


@DBObject(table_name='UnVersionedDataTest')
class UnVersionedData(object):
    name = Field('default name')


@DBObject(table_name='BadNews', versioning='nope-thats-not-right')
class BadVersionData(object):
    name = Field()


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
        self.start = {'a': 1, 'b': 11, 'c': 111}
        self.mid1 = {'a': 2, 'b': 22, 'c': 222}
        self.mid2 = {'a': 3, 'b': 33, 'c': 333}
        self.final = {'a': 4, 'b': 44, 'c': 444}
        self.series = [self.start, self.mid1, self.mid2, self.final]

    def tearDown(self):
        pass

    def test_empty_history(self):
        diff_hist = []
        obj_hist = list(parse_diff_hist(self.start, diff_hist))

        self.assertEquals(1, len(obj_hist))
        self.assertEquals(self.start, json.loads(obj_hist[0][0]))
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
        obj_list = list(reversed([json.loads(ver) for ver, _ in obj_hist]))
        self.assertEquals(self.series, obj_list)


class VersionSavedTesting(unittest.TestCase):
    def setUp(self):
        gludb.config.default_database(gludb.config.Database(
            'sqlite',
            filename=':memory:'
        ))
        VersionedData.ensure_table()

    def tearDown(self):
        # Undo any database setup
        gludb.config.clear_database_config()

    def test_versions_saved(self):
        expected = []

        d = VersionedData()

        def do_save():
            d.save()
            expected.append(d.to_data())

        do_save()

        d.name = 'first new name'
        d.descrip = 'Changed named once'
        d.age = 1
        do_save()

        d.name = 'last new name'
        d.descrip = 'Changed named twice'
        d.age = 2
        do_save()

        obj_hist = list(parse_diff_hist(d.to_data(), d.get_version_hist()))
        self.assertEquals(3, len(obj_hist))
        self.assertEquals(len(expected), len(obj_hist))

        for exp, act in zip(reversed(expected), obj_hist):
            exp = VersionedData.from_data(json.dumps(cmpfilt(exp)))

            actobj, actdate = act
            actobj = VersionedData.from_data(json.dumps(cmpfilt(actobj)))

            self.assertTrue(compare_data_objects(exp, actobj))

        print(type(obj_hist[0][0]), obj_hist[0][0])
        obj_hist_dct = [json.loads(o) for o, _ in obj_hist]

        # a little sanity checking
        self.assertEquals("last new name", obj_hist_dct[0]['name'])
        self.assertEquals("first new name", obj_hist_dct[1]['name'])
        self.assertEquals("default name", obj_hist_dct[2]['name'])


class VersionTypesTesting(unittest.TestCase):
    def setUp(self):
        gludb.config.default_database(gludb.config.Database(
            'sqlite',
            filename=':memory:'
        ))
        UnVersionedData.ensure_table()

    def tearDown(self):
        # Undo any database setup
        gludb.config.clear_database_config()

    # Note no delta history checking - that's testing above in
    # VersionSavedTesting.test_versions_saved

    def test_no_versioning(self):
        obj = UnVersionedData(name='a')
        self.assertIsNone(obj.get_version_hist())

        obj.save()
        obj.name = 'B'
        obj.save()

        self.assertIsNone(obj.get_version_hist())

    def test_bad_versioning(self):
        def try_op():
            return BadVersionData(name='etc').get_version_hist()
        self.assertRaises(ValueError, try_op)
