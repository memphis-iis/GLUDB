"""Insure that we handle derived classes OK
"""

import unittest
import sys
import inspect
import random

import gludb.config

from gludb.simple import DBObject, Field
from gludb.data import Storable
from gludb.config import get_mapping

from utils import compare_data_objects


@DBObject(table_name='BaseClass')
class BaseClass(object):
    name = Field('')


@DBObject(table_name='MidA')
class MidA(BaseClass):
    pass


@DBObject(table_name='MidB')
class MidB(BaseClass):
    pass


@DBObject(table_name='MidC')
class MidC(BaseClass):
    pass


@DBObject(table_name='Derived1')
class Derived1(MidA, MidB, MidC):
    pass


@DBObject(table_name='Derived2')
class Derived2(MidC, MidB, MidA):
    pass


@DBObject(table_name='Derived3')
class Derived3(MidB, MidC, MidA):
    pass


class DefaultStorageTesting(unittest.TestCase):
    def setUp(self):
        gludb.config.default_database(gludb.config.Database(
            'sqlite',
            filename=':memory:'
        ))

        our_module = sys.modules[__name__]

        def our_class(cls):
            return (
                inspect.isclass(cls) and
                issubclass(cls, Storable) and
                cls.__module__ == our_module.__name__
            )
        self.all_data_classes = [
            cls
            for name, cls in inspect.getmembers(our_module)
            if our_class(cls)
        ]

        self.assertEquals(7, len(self.all_data_classes))
        for cls in self.all_data_classes:
            cls.ensure_table()

    def tearDown(self):
        # Undo any database setup
        gludb.config.clear_database_config()

    def assertObjEq(self, obj1, obj2):
        self.assertTrue(compare_data_objects(obj1, obj2))

    def assertReadable(self, obj):
        self.assertObjEq(obj, obj.__class__.find_one(obj.id))

    def assertWriteable(self, cls):
        obj = cls()
        SRC = 'abcdefghijklmnopqrstuvwxyz0123456789'
        obj.name = ''.join(random.choice(SRC) for _ in range(12))
        obj.save()
        self.assertReadable(obj)

    def test_can_readwrite(self):
        for cls in self.all_data_classes:
            self.assertWriteable(cls)


class MappedStorageTesting(unittest.TestCase):
    def setUp(self):
        self.defdb = gludb.config.Database('sqlite', filename=':memory:')
        self.mapdb = gludb.config.Database('sqlite', filename=':memory:')

    def tearDown(self):
        # Undo any database setup
        gludb.config.clear_database_config()

    def test_base_on_down(self):
        gludb.config.clear_database_config()
        gludb.config.default_database(self.defdb)
        gludb.config.class_database(BaseClass, self.mapdb)

        self.assertEquals(self.mapdb, get_mapping(BaseClass))
        self.assertEquals(self.mapdb, get_mapping(MidA))
        self.assertEquals(self.mapdb, get_mapping(MidB))
        self.assertEquals(self.mapdb, get_mapping(MidC))
        self.assertEquals(self.mapdb, get_mapping(Derived1))
        self.assertEquals(self.mapdb, get_mapping(Derived2))
        self.assertEquals(self.mapdb, get_mapping(Derived3))
