# GLUDB

## Generalized Learning Utilities Database Library

For more GLU, see also
[SuperGLU](https://github.com/GeneralizedLearningUtilities/SuperGLU)

GLUDB provides a fairly simple way to read/write data to some popular datastores
like Amazon's DynamoDB and Google Cloud Datastore. We provide:

* A simple abstraction layer for annotating classes that should be stored in
  the database
* Support for versioning by automatically storing change history with the data
* Automated "indexing", which includes querying on the value of indexes
* Automated, configurable backup to Amazon's S3 (and Glacier depending on how
  you configure the S3 buckets)

We currently support Python 2 (2.7 and greater) and 3 (3.4 and greater). The
data stores currently supported are:

* sqlite
* DynamoDB
* Google Cloud Datastore
* MongoDB

## Who is this for?

GLUDB is for people who want a document-oriented storage solution for the major
cloud providers (and some other back ends), but also want it dead simple. This
is *NOT* meant to be a replacement for sqlalchemy or Django Models. If you
think that you need a relational database or if you might need advanced functionality,
then GLUDB might not be for you. (Although it's open source, so you should feel
free to steal what you can use.)

However, this might be the library for you if:

* You want to be able to switch between MongoDB, Amazon DynamoDB, and/or
  Google Cloud Datastore (and don't forget sqlite for caching!)
* You want a dead-simple way to read and write data
* You don't plan on having tremendously complicated queries
* You want to keep a history of changes to your objects
* You want a manual backup/snapshot mechanism to AWS S3


## Installing

You can install from PyPI using pip:

    pip install gludb

You will also need to install any dependencies you need based on the
functionality you want to use:

* DynamoDB Backend - boto
* Google Cloud Datastore - googledatastore
* MongoDB - pymongo
* Backups - boto

These dependencies are included in setup.py so that you can install them all
at the same time (assuming a fairly recent version of pip). As an example,
you could install gludb and the dependencies needed for dynamodb and backup
support into a virtualenv using Python 3 like this:

    user@host:~$ virtualenv -p python3 env
    user@host:~$ . env/bin/activate
    user@host:~$ pip install --upgrade pip wheel
    user@host:~$ pip install gludb[dynamodb,backups]

You can also view the [release notes](relnotes.md)

## The easy intro

To get started, check out the simple interface provided:
[Using gludb.simple](simple.md)

The basic idea is that you define "fields" in your class with a default value
and you annotate your class. GLUDB provides an ID field, a default constructor
(`__init__` method), functions to serialize/deserialize you class to/from JSON,
and data store methods to read/write records. Here a simple example:

    from gludb.simple import DBObject, Field, Index
    from gludb.config import default_database, Database

    @DBObject(table_name='SomeTableName')
    class DemoObject(object):
        name = Field('default name')

        @Index
        def reversed_name(self):
            return ''.join(reversed(self.name.lower()))

    # Perform initial configuration (only needed when your program starts us)
    default_database(Database('sqlite', filename=':memory:'))
    # Make sure our table (and any indexes) exists
    DemoObject.ensure_table()

    # Create a new object with default values in the fields
    obj1 = DemoObject()
    # Create an object and specify fields
    obj2 = DemoObject(name='Bob')
    # You can change fields
    obj1.name = 'Alice'

    # Save objects
    obj1.save()
    obj2.save()

    # You can use the serialization methods directly
    json_data = obj1.to_data()
    copy_obj = DemoObject.from_data(json_data)

    # You can read the objects back from the database
    found = DemoObject.find_one(obj1.id)
    # You can find all objects stored
    object_list = DemoObject.find_all()
    # You can read using your defined indexes
    idx_obj = DemoObject.find_by_index('reversed_name', 'ecila')

For further details see [Using gludb.simple](simple.md)

## Development

Check out the [development page](development.md) and the
[testing overview](testing.md)
