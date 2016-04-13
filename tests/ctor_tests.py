"""Testing constructor-related functionality in gludb.simple.
"""

import unittest

from gludb.simple import DBObject, Field
from gludb.data import Storable
from gludb.versioning import VersioningTypes

from utils import compare_data_objects


@DBObject(table_name='SetupTest')
class SetupData(object):
    name = Field('setup default')

    def setup(self, *args, **kwrds):
        self.found_arg = args[0] if len(args) == 1 else repr(args)
        self.found_name = kwrds.get('name', '<NAME MISSING!>')
        self.extra_data = "Hello World " + self.name


@DBObject(table_name='SetupGrandParentClass')
class GrandParent(object):
    gpsetup = Field('oops')
    def setup(self, *args, **kwrds):
        self.gpsetup = 'Done'


@DBObject(table_name='SetupParentClass1')
class Parent1(GrandParent):
    psetup1 = Field('oops')
    def setup(self, *args, **kwrds):
        super(Parent1, self).setup(*args, **kwrds)
        self.psetup1 = 'Done'


@DBObject(table_name='SetupParentClass2')
class Parent2(GrandParent):
    psetup2 = Field('oops')
    def setup(self, *args, **kwrds):
        super(Parent2, self).setup(*args, **kwrds)
        self.psetup2 = 'Done'


@DBObject(table_name='SetupChildClass')
class Child(Parent1, Parent2):
    csetup = Field('oops')
    def setup(self, *args, **kwrds):
        super(Child, self).setup(*args, **kwrds)
        self.csetup = 'Done'


class CtorTesting(unittest.TestCase):
    def setUp(self):
        pass

    def test_setup_called(self):
        s = SetupData('passthru', name='R')
        self.assertEquals('', s.id)
        self.assertEquals('passthru', s.found_arg)
        self.assertEquals('R', s.found_name)
        self.assertEquals("Hello World R", s.extra_data)

    def test_setup_with_subclasses(self):
        c = Child()
        self.assertEquals(c.gpsetup, 'Done')
        self.assertEquals(c.psetup1, 'Done')
        self.assertEquals(c.psetup2, 'Done')
        self.assertEquals(c.csetup, 'Done')

    def test_bad_old_object(self):
        # Mainly for Python 2
        class Bad:
            f1 = Field()
            def __init__(self):
                pass
        class Badder(Bad):
            f2 = Field()
            def __init__(self):
                pass
        class StillBad(Bad):
            f3 = Field()

        def create_class():
            return DBObject('FakeTable')(Bad)
        def create_subclass1():
            return DBObject('FakeTable')(Badder)
        def create_subclass2():
            return DBObject('FakeTable')(StillBad)

        self.assertRaises(TypeError, create_class)
        self.assertRaises(TypeError, create_subclass1)
        self.assertRaises(TypeError, create_subclass2)

    def test_bad_new_object(self):
        class Bad(object):
            f1 = Field()
            def __init__(self):
                pass
        class Badder(Bad):
            f2 = Field()
            def __init__(self):
                pass
        class StillBad(Bad):
            f3 = Field()

        def create_class():
            return DBObject('FakeTable')(Bad)
        def create_subclass1():
            return DBObject('FakeTable')(Badder)
        def create_subclass2():
            return DBObject('FakeTable')(StillBad)

        self.assertRaises(TypeError, create_class)
        self.assertRaises(TypeError, create_subclass1)
        self.assertRaises(TypeError, create_subclass2)
