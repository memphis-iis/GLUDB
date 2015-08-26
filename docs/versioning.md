# Versioning

One of things provided by gludb is data versioning. The package
gludb.versioning provides the raw tools you need to track changes made to
objects. This can be handy if you're planning on "advanced" use cases. For
instance, if you're hand-rolling your data classes as described in
[Advanced Use](advanced.md). However, if you're [using gludb.simple](simple.md)
then you can just include the correct versioning type in you `DBObject`
annotation.

Currently the only direct type of versioning that we support is DELTA_HISTORY,
which stores a list of deltas that led to the current version of the object
(and a date/time stamp for that change). The idea is that you can iteratively
apply these deltas to deduce the saved state of the object at any point in the
past.

Other types of versioning are certainly possible, but are not currently
planned. However, pull requests are always welcome :)

## Minimal versioning

It's important to note that even "advanced" classes that directly inherit from
`gludb.data.Storable` get some versioning for free. Any class deriving from
Storable that has been annotated with `gludb.data.DatabaseEnabled` gets
"original version tracking". The idea is that object instances maintain a copy
of their state from before any in-memory changes have been made. Specifically:

* After an object is loaded from a datastore, the state is saved
* After an object is saved to a datastore, the state is saved
* The last state saved for an object may be retrieved via a call to
  `gludb.data.orig_version`

For example:

    from gludb.simple import DBObject, Field
    from gludb.data import orig_version

    @DBObject(table_name="Ver")
    class Ver(object):
        name = Field('')

    v = Ver(name='First')
    v.save()
    v.name = "Middle"
    orig_v = Ver.from_data(orig_version(v))
    print(v.name + " was " + orig_v.name)  # prints 'Middle was First'

    v.save()

    v2 = Ver.find_one(v.id)
    v2.name = "Last"
    orig_v = Ver.from_data(orig_version(v2))
    print(v2.name + " was " + orig_v.name)  # prints 'Last was Middle'


## Versioning with gludb.simple

By default, classes annotated with `gludb.simple.DBObject` don't track their
versions. You need to add a versioning type to the `DBObject` annotation. Take
this example:

    from gludb.simple import DBObject, Field
    from gludb.config import default_database, Database
    from gludb.versioning import VersioningTypes

    @DBObject(table_name="Ver", versioning=VersioningTypes.DELTA_HISTORY)
    class Ver(object):
        name = Field('')

    default_database(Database('sqlite', filename=':memory:'))
    Ver.ensure_table()

    v = Ver(name='A')
    v.save()
    v.name = 'B'
    v.save()
    v.name = 'C'
    v.save()

    from gludb.versioning import parse_diff_hist

    for objdata, chgdate in parse_diff_hist(v.to_data(), v.get_version_hist()):
        if chgdate:
            print("Historical Version from: %s" % chgdate)
        else:
            print("Current Version")
        print(Ver.from_data(objdata).name)

The printed results would be something like:

````Text
Current Version
C
Historical Version from: UTC:2015-08-26T20:43:30.210610
B
Historical Version from: UTC:2015-08-26T20:43:30.208385
A
````

Of course, the date/time stamps would be different.

The latest version of the object `v` contains all the information necessary to
reconstruct past saved versions. All that information is retrieved via the
call to `get_version_hist`. That method (provided by gludb.simple to all
classes annotated with `DBObject`) returns a list where each element is a
dictionary with the keys 'diff' and 'diff-date'. The value attached to 'diff'
is a JSON-compatible object containing the delta information, and the value
attached to 'diff-date' is a string giving the UTC date and time of the save.

We use the `gludb.versioning` function `parse_diff_hist` to actually
historical copies of our object for us. It is a generator, so if you just want
to capture everything, be sure to wrap it in `list`. Each item that you
iterate over is actually a tuple of the kind (data, date) where the data is a
JSON representation of the historical version of the object and date is a
string giving the UTC date and time of the save. The JSON data is compatible
with the class's `from_data` classmethod (as you can see in the final print
statement).

## Using gludb.versioning

For an example of how to use `gludb.versioning` functions with "advanced"
classes, please see the source code for
[gludb.simple](https://github.com/memphis-iis/GLUDB/blob/master/gludb/simple.py)

At the lowest level, `gludb.versioning` supplies the functions `record_diff`
and `record_patch` to create and apply delta's, respectively. Currently this
functionality is provided by the excellent library
[json_delta](http://json-delta.readthedocs.org).

You can use `record_diff` in conjunction with the function `append_diff_hist`
in order to maintain a list that is parsable by `parse_diff_hist`.
