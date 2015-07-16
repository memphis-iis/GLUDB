"""gludb.data

The "core" functionality. If you're unsure what to use, you should look into
gludb.simple. This module is for those needing advanced functionality or
customization
"""

from abc import ABCMeta, abstractmethod


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
    can test them with isinstance(obj, Storable)
    """
    @abstractmethod
    def to_data(self):
        pass

    @classmethod
    @abstractmethod
    def from_data(self):
        pass
