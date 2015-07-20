"""gludb.config

Provide gludb configuration. This consists mainly of a mapping from Storable
classes to a database configuration. It also includes a default mapping for
classes not specifically mapped to a database
"""

from importlib import import_module


class Database(object):
    """Configuration class representing a database instance supported by one
    of our backends"""
    def __init__(self, db_driver, **kwrds):
        mod = import_module('.backends.'+db_driver, __package__)
        Backend = getattr(mod, "Backend")
        self.backend = Backend(**kwrds)

    def ensure_table(self, cls):
        return self.backend.ensure_table(cls)

    def find_one(self, cls, id):
        return self.backend.find_one(cls, id)

    def find_all(self, cls):
        return self.backend.find_all(cls)

    def find_by_index(self, cls, index_name, value):
        return self.backend.find_by_index(cls, index_name, value)

    def save(self, obj):
        return self.backend.save(obj)


# Note our use of a class with a singleton instance - so configuration is
# process-wide. This makes things much simpler for some users (which is one
# of our main design drivers). One potential enhancement is to allow multiple
# database mappings - perhaps as a Flask Blueprint plugin/addon
class _DatabaseMapping(object):
    def __init__(self):
        self.clear_mappings()

    def add_mapping(self, cls, db):
        self.mapping[cls] = db

    def get_mapping(self, cls):
        db = self.mapping.get(cls, self.default_database)
        if db is None:
            raise ValueError("There is no database mapping for %s" % repr(cls))
        return db

    def clear_mappings(self):
        self.default_database = None
        self.mapping = {}

_database_mapping = _DatabaseMapping()


def default_database(db):
    """Set the default database configuration used for classes without a
    specific mapping"""
    _database_mapping.default_database = db


def class_database(cls, db):
    """Map a class (for which we assume issubclass(cls, Storable)==True) to
    a database configuration"""
    _database_mapping.add_mapping(cls, db)


def clear_database_config():
    """Reset all mappings to default state. Note that any in-memory databases
    will be lost"""
    _database_mapping.clear_mappings()


def get_mapping(cls):
    """Return a database config object for the given class"""
    return _database_mapping.get_mapping(cls)
