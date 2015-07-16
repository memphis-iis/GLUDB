"""gludb.simple

Provides the simplest possible interface to our functionality.

We provide a simple annotation to create classes with fields (with
optional default values), parameterized constructors, persistence,
and data operations. You are free to derive from any object you wish.
See gludb.data if you need custom or more advanced functionality.

    @DBObject
    class Demo(object):
        some_field = Field()
        my_number = Field(default=42)


    d = Demo(some_field='foo', my_number=3.14)
    print d.to_data()  # Prints a JSON representation
    d1 = Demo.from_data(d.to_data())  # Clone using persistence functions
    d.save()  # Save to database
    for obj in Demo.find_all():  # Print json rep of all objects in DB
        print obj.to_data()
"""

# TODO: Indexing support
# TODO: nested objects, lists, lists of nested objects

import json  # TODO: look for other json impls first

from .data import Storable


class Field(object):
    """Support for class-level field declaration.
    """
    def __init__(self, default=''):
        self.name = None
        self.default = default


def _auto_init(self, *args, **kwrds):
    """Our decorator will add this as __init__ to target classes
    """
    for fld in getattr(self, '__fields__', []):
        val = kwrds.get(fld.name, fld.default)
        setattr(self, fld.name, val)

    if callable(getattr(self, 'setup', None)):
        self.setup(*args, **kwrds)


def _get_id(self):
    return self.id


def _set_id(self, new_id):
    self.id = new_id


def _to_data(self):
    data = dict([
        (fld.name, getattr(self, fld.name, fld.default))
        for fld in self.__fields__
    ])
    return json.dumps(data)


def _from_data(cls, data):
    data_dict = json.loads(data)
    return cls(**data_dict)


def DBObject(table_name, versioning):
    """Classes annotated with DBObject gain persistence methods.
    """
    def wrapped(cls):
        field_names = set()
        all_fields = []

        for name in dir(cls):
            fld = getattr(cls, name)
            if fld and isinstance(fld, Field):
                fld.name = name
                all_fields.append(fld)
                field_names.add(name)

        if 'id' not in field_names:
            fld = Field(default='')
            fld.name = 'id'
            all_fields.insert(0, fld)

        # Things we count on as part of our processing
        cls.__table_name__ = table_name
        cls.__versioning__ = versioning
        cls.__fields__ = all_fields

        # Give them a ctor for free
        cls.__init__ = _auto_init

        # Duck-type the class for our data methods
        cls.get_id = _get_id
        cls.set_id = _set_id
        cls.to_data = _to_data
        cls.from_data = classmethod(_from_data)

        # Register with our abc since we actually implement all necessary
        # functionality
        Storable.register(cls)

        return cls

    return wrapped
