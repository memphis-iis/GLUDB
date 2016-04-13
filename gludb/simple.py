"""gludb.simple

Provides the simplest possible interface to our functionality.

We provide a simple annotation to create classes with fields (with optional
default values), parameterized constructors, persistence, and data operations.
You are free to derive from any object you wish. See gludb.data if you need
custom or more advanced functionality.

    @DBObject
    class Demo(object):
        some_field = Field()
        my_number = Field(default=42)

    d = Demo(some_field='foo', my_number=3.14)
    print(d.to_data())  # Prints a JSON representation
    d1 = Demo.from_data(d.to_data())  # Clone using persistence functions
    d.save()  # Save to database
    for obj in Demo.find_all():  # Print json rep of all objects in DB
        print(obj.to_data())

Also note that currently we aren't supporting nested DBObject objects.
HOWEVER, we make no restrictions on a field being a JSON-compatible Python
type. We make it possible to supply a decent default value by allowing a
function to be specified as a default value - it will be called when a default
value is needed. For example:

    @DBObject
    class Complicated(object):
        name = Field(default='')
        complex_data = Field(default=dict)

    c = Complicate(name)
    c.complex_data['a'] = 123
    c.complex_data['b'] = 456

IMPORTANT: you should *NOT* just use a default object like this:
`Field(default={})`. Modifications made to the default object will become the
NEW default for other classes. See
[here](http://effbot.org/zone/default-values.htm). However, you may supply
a function that will be called to retreive a default value. In this example
you should use `Field(default=dict)`.
"""

import json

from .utils import now_field
from .data import Storable, DatabaseEnabled, orig_version
from .versioning import VersioningTypes, record_diff, append_diff_hist


class _NO_VAL:
    """Simple helper we use instead of None (in case they want to use a default
    value of None)."""
    pass


class Field(object):
    """Support for class-level field declaration.
    """
    def __init__(self, default=''):
        self.name = None
        self.default = default

    def get_default_val(self):
        """Helper to expand default value (support callables)"""
        val = self.default
        while callable(val):
            val = val()
        return val


def _auto_init(self, *args, **kwrds):
    """Our decorator will add this as __init__ to target classes
    """
    for fld in getattr(self, '__fields__', []):
        val = kwrds.get(fld.name, _NO_VAL)
        if val is _NO_VAL:
            val = fld.get_default_val()
        setattr(self, fld.name, val)

    if callable(getattr(self, 'setup', None)):
        self.setup(*args, **kwrds)

# Sneaky trick - we tag __init__ functions that are Ok to be overwritten...
# this is mainly for Python 2 (in Python 3 we can successfully do an equality
# comparison between _auto_init and a replaced __init__)
_auto_init._clobber_ok = True

# Actual check for an overridable __init__ given a class
def ctor_overridable(cls):
    prev_init = getattr(cls, "__init__", None)
    if not callable(prev_init):
        return True
    if prev_init in [object.__init__, _auto_init]:
        return True
    if getattr(prev_init, '_clobber_ok', False):
        return True

    print(cls, prev_init, getattr(prev_init, '_clobber_ok', 'missing'))
    return False  # Not on our list


def _get_table_name(cls):
    return cls.__table_name__


def _get_id(self):
    return self.id


def _set_id(self, new_id):
    self.id = new_id


def _to_data(self):
    def getval(fld):
        val = getattr(self, fld.name, _NO_VAL)
        if val is _NO_VAL:
            val = fld.get_default_val()
        return val

    # Update the datetime fields that we add automatically
    now = now_field()
    setattr(self, '_last_update', now)
    if not getattr(self, '_create_date', ''):
        setattr(self, '_create_date', now)

    data = dict([(fld.name, getval(fld)) for fld in self.__fields__])

    return json.dumps(data)


def _from_data(cls, data):
    data_dict = json.loads(data)
    return cls(**data_dict)


def _index_names(cls):
    def is_index(name):
        attr = getattr(cls, name, None)
        return getattr(attr, 'is_index', False)

    return [name for name in dir(cls) if is_index(name)]


def _indexes(self):
    def get_val(name):
        attr = getattr(self, name, None)
        while callable(attr):
            attr = attr()
        return attr

    return dict([
        (name, get_val(name)) for name in self.__class__.index_names()
    ])


def _delta_save(save_method):
    def wrapper(self):
        # Get the diff's being saved
        pre_changes = orig_version(self)
        curr_data = self.to_data()
        diff = record_diff(pre_changes, curr_data) if pre_changes else None

        # Need to save changes?
        if diff:
            ver_hist = self.get_version_hist()
            ver_hist = append_diff_hist(diff, ver_hist)
            setattr(self, '_version_hist', ver_hist)

        return save_method(self)

    return wrapper


def _get_version_hist(self):
    if self.__versioning__ == VersioningTypes.NONE:
        return None
    elif self.__versioning__ == VersioningTypes.DELTA_HISTORY:
        return getattr(self, '_version_hist', list())
    else:
        raise ValueError("Unknown versioning type")


def DBObject(table_name, versioning=VersioningTypes.NONE):
    """Classes annotated with DBObject gain persistence methods."""
    def wrapped(cls):
        field_names = set()
        all_fields = []

        for name in dir(cls):
            fld = getattr(cls, name)
            if fld and isinstance(fld, Field):
                fld.name = name
                all_fields.append(fld)
                field_names.add(name)

        def add_missing_field(name, default='', insert_pos=None):
            if name not in field_names:
                fld = Field(default=default)
                fld.name = name
                all_fields.insert(
                    len(all_fields) if insert_pos is None else insert_pos,
                    fld
                )

        add_missing_field('id', insert_pos=0)
        add_missing_field('_create_date')
        add_missing_field('_last_update')
        if versioning == VersioningTypes.DELTA_HISTORY:
            add_missing_field('_version_hist', default=list)

        # Things we count on as part of our processing
        cls.__table_name__ = table_name
        cls.__versioning__ = versioning
        cls.__fields__ = all_fields

        # Give them a ctor for free - but make sure we aren't clobbering one
        if not ctor_overridable(cls):
            raise TypeError(
                'Classes with user-supplied __init__ should not be decorated '
                'with DBObject. Use the setup method'
            )
        cls.__init__ = _auto_init

        # Duck-type the class for our data methods
        cls.get_table_name = classmethod(_get_table_name)
        cls.get_id = _get_id
        cls.set_id = _set_id
        cls.to_data = _to_data
        cls.from_data = classmethod(_from_data)
        cls.index_names = classmethod(_index_names)
        cls.indexes = _indexes
        # Bonus methods they get for using gludb.simple
        cls.get_version_hist = _get_version_hist

        # Register with our abc since we actually implement all necessary
        # functionality
        Storable.register(cls)

        # And now that we're registered, we can also get the database
        # read/write functionality for free
        cls = DatabaseEnabled(cls)

        if versioning == VersioningTypes.DELTA_HISTORY:
            cls.save = _delta_save(cls.save)

        return cls

    return wrapped


def Index(func):
    """Marks instance methods of a DBObject-decorated class as being used for
    indexing. The function name is used as the index name, and the return
    value is used as the index value.

    Note that callables are call recursively so in theory you can return
    a function which will be called to get the index value"""
    func.is_index = True
    return func
