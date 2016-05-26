"""gludb.data - "core" functionality.

If you're unsure what to use, you should look into
gludb.simple. This module is for those needing advanced functionality or
customization
"""

from abc import ABCMeta, abstractmethod

from .config import get_mapping

# pylama:ignore=E501


class DeleteNotSupported(Exception):  # NOQA
    """Exception thrown when delete is not supported by the backend."""
    pass


# A little magic for using metaclasses with both Python 2 and 3
def _with_metaclass(meta, *bases):
    """Taken from future.utils, who took it from jinja2/_compat.py (BSD license)."""
    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__

        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)

    return metaclass('temporary_class', None, {})


class Storable(_with_metaclass(ABCMeta)):
    """Our abstract base class.

    It marks subclasses as persistable and storable. Note that the DBObject
    annotation in gludb.simple registers all annotated classes as 'virtual base
    classes' of Storage so that you can test them with isinstance(obj, Storable)
    """

    # This is field we use for the original version of the object (saved after
    # retrieval and before any edits occur)
    ORIG_VER_FIELD_NAME = "_prev_version"

    @classmethod
    @abstractmethod
    def get_table_name(self):
        """Return the name of the table/collection/etc where objects should be saved/loaded."""
        pass

    @abstractmethod
    def get_id(self):
        """The instance should return the current key/ID for the instance.

        If a 'falsey' value is return, on save one will be created and set via a
        call to self.set_id
        """
        pass

    @abstractmethod
    def set_id(self, new_id):
        """The instance should accept a new key/ID. See also get_id."""
        pass

    @abstractmethod
    def to_data(self):
        """The instance should return JSON representation of it's internal state. See also from_data."""
        pass

    @classmethod
    @abstractmethod
    def from_data(self):
        """Return a new instance of the subclass populated from the JSON representation."""
        pass

    @classmethod
    def index_names(self):
        """Return an iterable of index names.

        Optional method. These names should correspond to the names used in the
        dictionary returned by the instance method `indexes` (below).
        """
        return None

    def indexes(self):
        """Return a dictionary of index name values that can be used in a query.

        Optional method. Note that this is not considered required data, so a
        backend could ignore indexes if necessary.
        """
        return None


def _ensure_table(cls):
    get_mapping(cls).ensure_table(cls)


def _post_load(obj):
    # Perform all necessary post load operations we want done when reading
    # from the database. We return the changed object, but make NO EFFORT
    # to keep from mutating the original object.
    if obj:
        setattr(obj, Storable.ORIG_VER_FIELD_NAME, obj.to_data())
    return obj


def _find_one(cls, id):
    return _post_load(get_mapping(cls).find_one(cls, id))


def _find_all(cls):
    return [
        _post_load(obj)
        for obj in get_mapping(cls).find_all(cls)
    ]


def _find_by_index(cls, index_name, value):
    return [
        _post_load(obj)
        for obj in get_mapping(cls).find_by_index(cls, index_name, value)
    ]


def _save(self):
    # Actual save
    get_mapping(self.__class__).save(self)

    # Now we have a new original version
    setattr(self, Storable.ORIG_VER_FIELD_NAME, self.to_data())


def _delete(self):
    # Actual delete - and note no version changes
    get_mapping(self.__class__).delete(self)


# TODO: we need a function ensure_package_db - it should work mainly like the
#       package_add functionality in Backup. Once the class list is create,
#       we would loop over every class and call ensure_table


def DatabaseEnabled(cls):
    """Given persistence methods to classes with this annotation.

    All this really does is add some functions that forward to the mapped
    database class.
    """
    if not issubclass(cls, Storable):
        raise ValueError(
            "%s is not a subclass of gludb.datab.Storage" % repr(cls)
        )

    cls.ensure_table = classmethod(_ensure_table)
    cls.find_one = classmethod(_find_one)
    cls.find_all = classmethod(_find_all)
    cls.find_by_index = classmethod(_find_by_index)
    cls.save = _save
    cls.delete = _delete

    return cls


def orig_version(obj):
    """Return the original version of an object.

    Original version is defined as what was read from the database before any
    user edits. If there isn't a previous version (for instance, newly created
    objects don't have a previous version), then None is returned. Mainly useful
    for testing.
    """
    return getattr(obj, Storable.ORIG_VER_FIELD_NAME, None)
