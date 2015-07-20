"""gludb.data

The "core" functionality. If you're unsure what to use, you should look into
gludb.simple. This module is for those needing advanced functionality or
customization
"""

from abc import ABCMeta, abstractmethod

from .config import get_mapping


# A little magic for using metaclasses with both Python 2 and 3
def _with_metaclass(meta, *bases):
    """Taken from future.utils, who took is from  from jinja2/_compat.py.
    License: BSD."""
    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__

        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)

    return metaclass('temporary_class', None, {})


class Storable(_with_metaclass(ABCMeta)):
    """Our abstract base class that marks subclasses as persistable and
    storable. Note that the DBObject annotation in gludb.simple registers
    all annotated classes as 'virtual base classes' of Storage so that you
    can test them with isinstance(obj, Storable)"""

    @classmethod
    @abstractmethod
    def get_table_name(self):
        """Return the name of the table/collection/etc where objects should
        be saved/loaded"""
        pass

    @classmethod
    @abstractmethod
    def get_versioning(self):
        """Return the type of versioning to be used - should be one of the
        values defined in gludb.versioning"""
        pass

    @abstractmethod
    def get_id(self):
        """The instance should return the current key/ID for the instance. If
        a 'falsey' value is return, on save one will be created and set via a
        call to self.set_id"""
        pass

    @abstractmethod
    def set_id(self, new_id):
        """The instance should accept a new key/ID. See also get_id"""
        pass

    @abstractmethod
    def to_data(self):
        """The instance should return JSON representation of it's internal
        state. See also from_data"""
        pass

    @classmethod
    @abstractmethod
    def from_data(self):
        """This classmethod returns a new instance of the subclass populated
        from the JSON representation"""
        pass

    def indexes(self):
        """This optional method should return a dictionary of index name values
        that can be used in a query. Note that this is not considered required
        data, so a backend could ignore indexes if necessary."""
        return None


def _ensure_table(cls):
    get_mapping(cls).ensure_table(cls)


def _find_one(cls, id):
    return get_mapping(cls).find_one(cls, id)


def _find_all(cls):
    return get_mapping(cls).find_all(cls)


def _save(self):
    return get_mapping(self.__class__).save(self)


def DatabaseEnabled(cls):
    """Classes annotated with DatabaseEnabled gain persistence methods. All
    this really does is add some functions that forward to the mapped database
    class"""
    if not issubclass(cls, Storable):
        raise ValueError(
            "%s is not a subclass of gludb.datab.Storage" % repr(cls)
        )

    cls.ensure_table = classmethod(_ensure_table)
    cls.find_one = classmethod(_find_one)
    cls.find_all = classmethod(_find_all)
    cls.save = _save

    return cls
