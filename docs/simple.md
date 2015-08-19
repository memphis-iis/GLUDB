# Using gludb.simple

## Introduction

Although GLUDB provides a way for you to customize (i.e. "write the code
yourself"), the general expectation is that you will use the gludb.simple
package. You define "fields" in your class with a default value
and you annotate your class. GLUDB provides an ID field, a default constructor
(`__init__` method), functions to serialize/deserialize you class to/from JSON,
and data store methods to read/write records. Here a simple example that we'll
be referring to throughout this article:

    from gludb.simple import DBObject, Field, Index
    from gludb.config import default_database, Database

    @DBObject(table_name='SimpleTableName')
    class SimpleObject(object):
        name = Field('default name')
        descrip = Field('')
        extra_data = Field(dict)

        @Index
        def rev_name(self):
            return ''.join(reversed(self.name.lower()))

    # Perform initial configuration (only needed when your program starts us)
    default_database(Database('sqlite', filename=':memory:'))
    # Make sure our table (and any indexes) exists
    SimpleObject.ensure_table()

    # Create a new object with default values in the fields
    obj1 = SimpleObject()
    # Create an object and specify fields
    obj2 = SimpleObject(name='Bob', descrip='Test Person')
    # You can change fields
    obj1.name = 'Alice'
    obj1.extra_data = {'test': True, 'silly': 'yes'}

    # Save objects
    obj1.save()
    obj2.save()

    # You can use the serialization methods directly
    json_data = obj1.to_data()
    copy_obj = SimpleObject.from_data(json_data)

    # You can read the objects back from the database
    found = SimpleObject.find_one(obj1.id)
    # You can find all objects stored
    object_list = SimpleObject.find_all()
    # You can read using your defined indexes
    idx_obj = SimpleObject.find_by_index('rev_name', 'ecila')

## Fields

TODO: default values

TODO: complete walkthrough with sqlite and some very simple mapping,
      including complex field, indexes, and a setup method

## DBObject annotation

TODO: table name and ensure_table

TODO: versioning

TODO: ctor and fields

TODO: to/from data

TODO: Data storage methods

## Indexes

Indexes are fairly simple to use. You define an instance method on class that
returns the value you want to be able to use to find the current instance of
the class. You annotate that function. Whenever you save an instance of that
class to the database, that index value is saved as well.

Later when you want to query that index, you can call `find_by_index` on your
class. Note that `find_by_index` takes the index name and the value that you
are looking for. The index name is the name of the function that you wrote.

Although they aren't requirements, there are a few guidelines that you should
keep in mind:

* Too many indexes can slow your database down needlessly. Some backends might
  even limit the number indexes allowed. In general, five or fewer is always OK
  and 100 is always too many :)
* Although not strictly necessary, it's usually a good idea to design index
  functions that always return the same value for the same data object.
* All index functions are called every time an object is saved, so you probably
  don't want long-running logic in an index function.

If you have an index function that seems to violate one or both of the last
two guidelines, you probably want a Field and an Index that returns the value
of that field:

    @DBObject(table_name='Blah')
    class Yadd(object):
        hard_to_calc = Field(0)

        def perform_hard_calc(self):
            self.hard_to_calc = some_really_awesome_function()

        @Index
        def hard_calc_search(self):
            return self.hard_to_calc

This way you call `perform_hard_calc` when necessary (if at all), and you don't
need to worry about how often the object is saved (at least from the standpoint
of calling your index function).


## Configuration

You'll notice that after the class is created, there are a couple of lines
of configuration code. As we'll discuss below, this ordinarily wouldn't be
alongside the classes you're storing in the database, but we wanted a complete
sample.

The first statement maps all classes to an in-memory sqlite database by default.
(You can also map specific classes to other data backends.) The next line ensures
that the table/collection/whatever where the data is actually stored is created.
Note that it doesn't hurt to call ensure_table over and over again, so you can
call this every time your application starts.

See [Configuration and Mapping](config.md) for more details.

## General design patterns

The gludb.simple package was created with a few assumptions:

* You want to define your model/data classes very simply.
* You want to be able to map those classes to data storage multiple ways.

As a result, there is a separate configuration step. For instance, you might
use nothing but sqlite for unit testing, and then use DynamoDB for your "real"
deployment to Amazon Web Services. You could even have additional, separate
configs for MongoDB for your local server and GCD for a Google Compute
deployment.

So how should you structure your application? Generally, design your
model/data classes as you would normally, but using the Field/DBObject help as
described above. Then, wherever you place code to start and configure your
application, add a section for configuring the gludb backends used. Use those
classes however you would normally (for instance, in your Flask routes if
you're writing a Flask-based web app).

For unit testing, you should provide some kind of mapping in a setup method,
and clear that mapping in the teardown method. Here's an example using
Python's `unittest` library and assuming that the SimpleObject class from the
demo code above is in the package `myapp.models`:

    from gludb.config import default_database, Database, clear_database_config
    from myapp.models import SimpleObject

    class SomeDemoTesting(unittest.TestCase):
        def setUp(self):
            default_database(gludb.config.Database('sqlite', filename=':memory:'))
            SimpleStorage.ensure_table()

        def tearDown(self):
            # Undo any database setup
            clear_database_config()

Because the sqlite database is kept in-memory, no files need to be cleaned and
testing runs very quickly.
