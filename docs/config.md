# GLUDB Configuration and Mapping

## Introduction

Whether you use gludb.simple or prefer to everything yourself, you're going to
need to configure the back end(s) used by your model classes. That might sound
like a pain, but it's what allows you to have a single code base but use
different data storage back ends.

For most situations you will just need to specify a default location to store
your data. You do this by creating a gludb.config.Database instance for your
chosen back end (see below for back end details) and passing it to
gludb.config.default_database:

````
from gludb.config import default_database, Database

# A couple of examples:
default_database(Database('sqlite', filename=':memory:'))
default_database(Database('dynamodb'))
````

That's all there is to it.

## Using Method Resolution Order for Classes

If you are using more than one back end then you'll need to specify something
other than a default. In that case you should use the function
`gludb.config.class_database`:

````
from gludb.config import default_database, Database, class_database

# By default, everything is in dynamodb, but we store InMemoryClass in
# an in-memory database in SQLite
default_database(Database('dynamodb'))
class_database(InMemoryClass, Database('sqlite', filename=':memory:'))
````

So now the question is: If a class declares `InMemoryClass` as a base class,
how will it get mapped?

The answer is that gludb uses MRO (Method Resolution Order) to resolve class
to back end mapping. When you use one of the data storage/retrieval methods
(like `save` or `find_all`), gludb looks for a mapping for the current class.
If there isn't an explicit mapping, gludb checks all the classes in the Method
Resolution Order and uses the first explicit mapping found. If gludb fails to
find a mapping then it choose the default mapping.

It may be easier to see this in an example. Suppose a class Busy derives from
the three classes X, Y, and Z - and all those classes derive from class Base:

    class Base(object):
        pass

    class X(Base):
        pass
    class Y(Base):
        pass
    class Z(Base):
        pass

    class Busy(X, Y, Z):
        pass

If you call `Busy.find_all()`, then a check for mapping would first look at
class Busy, then (in order) classes X, Y, Z, Base, and object. If this is the
first time you've seen multiple inheritance, you'll note that the order of
Busy's super classes is important. This is how Python resolves method calls
(we didn't just make this up). In fact, we depend on the results of the
standard library call `inspect.getmro`.

If none of the classes mentioned have a mapping, then gludb will use the
default mapping. If there is no default mapping, then no mapping is possible
and gludb will throw an error.

Astute readers will note that you could map the class `object` to a database
as a kind of default mapping. We generally don't recommend this, because it
would work *sort of*. Some notes:

* Recall that we support Python 2 and 3. In Python 3.4, classes declared
  without a base class get `object` as a base class automatically. In Python
  2.7 they just don't have a base class. That means that using an `object`
  DB mapping won't work as a default in every case.
* We always check for the default database mapping last, so mapping to object
  would be the last thing checked before the actual default. So mapping `object`
  wouldn't actually get you anything unless you have a strange case.

## DynamoDB Back End

The DynamoDB assumes that all necessary configuration details will be handled
via environment variables in AWS. As a result, there's no special configuration
to use for DynamoDB. You might need to manually specify environment variables
if you are using a DynamoDB backend on an EC2 instance, but Elastic Beanstalk
should "just work".

If you *do* need to specify environment variables, then you might want to look
into [Boto configuration](http://boto.readthedocs.io/en/latest/boto_config_tut.html).
Essentially, you should only need to define two environment variables:

* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY

If you define one of the two environment variables `DEBUG` and `travis` to a
"truthy" value, the DynamoDB backend will: use port 8000 on localhost, and use
string 'TEST' for both the AWS access ID and secret key. This should work with
the two most popular Dynamo testing servers: DynamoDB Local and Dynalite. This
used for unit testing both local workstations and on Travis-CI.

## Google Cloud Datastore Back End

__IMPORTANT__ - due to current limitations with the Python clients and test
servers available for Google Cloud Datastore, only Python 2.7 is supported.
That's right: _no_ Python 3 support for Google Cloud Datastore. When Google
fixes the situation we'll be adding Python 3 support.

Much like DynamoDB, the Google Cloud Datastore back end is also self-
configuring. For local testing, you should have something Google's GCD test
server listening on port 8080.


## MongoDB Back End

The MongoDB back end is configured via the keyword `mongo_url` which should be
a MongoDB Connection String URI as per the description
[here](https://docs.mongodb.org/v3.0/reference/connection- string/).
__IMPORTANT__ -  You should specify a default database, even though it is
technically an optional part of the URI. For example, to specify the database
TestDB on a local MongoDB instance listening on the default Mongo port you
would use:

    from gludb.config import default_database, Database
    default_database(Database(
        'mongodb',
        mongo_url='mongodb://localhost:27017/TestDB'
    ))

All options are passed through, so this should work for all advanced
configurations (including replica sets).

## SQLite Back End

The SQLite backend takes only the parameter `filename` to specify the location
used for the database file. You can also use the SQLite special file name
`:memory:` (as shown in our examples above) to have in-memory storage. While
this is generally used for testing, it can also be handy for caching.

## Table creation

As a general note, wherever you have the configuration for your data storage,
you should also have calls to `ensure_table`. Note that at this time you'll
need to explicitly list the tables you want created. Assuming that you want
all the classes/tables from the MRO example above to exist, you would want to
call something like this in your startup code:

    Base.ensure_table()
    X.ensure_table()
    Y.ensure_table()
    Z.ensure_table()
    Busy.ensure_table()

## Backup configuration

Much like table creation, you should also have some kind of Backup
configuration near or with your actual back end configuration. Please see
[Backing Up](backups.md) for details
