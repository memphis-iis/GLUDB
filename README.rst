GLUDB
=====

|Travis CI Build State| `Travis CI
Details <https://travis-ci.org/memphis-iis/GLUDB>`__

|Documentation State| See our documentation at
http://gludb.readthedocs.io/

Generalized Learning Utilities Database Library
-----------------------------------------------

For more GLU, see also
`SuperGLU <https://github.com/GeneralizedLearningUtilities/SuperGLU>`__

GLUDB provides a simple way to read/write data to some popular
datastores like Amazon's DynamoDB and Google Cloud Datastore. We
provide:

-  A simple abstraction layer for annotating classes that need
   serialization
-  Support for versioning by automatically storing change history with
   the data
-  Automated "indexing", which includes querying on the value of indexes
-  Automated, configurable backup to Amazon's S3 (and Glacier depending
   on how you configure the S3 buckets)

We support Python 2 (2.7 and greater) and 3 (3.4 and greater). The data
stores supported are:

-  sqlite
-  DynamoDB
-  Google Cloud Datastore
-  MongoDB

Installing
----------

You can install from PyPI using pip:

::

    pip install gludb

You will also need to install any dependencies you need based on the
functionality you want to use:

-  DynamoDB Backend - boto
-  Google Cloud Datastore - googledatastore
-  MongoDB - pymongo
-  Backups - boto

setup.py includes these dependencies so that you can install them all at
the same time (assuming a decently recent version of pip). As an
example, you could install gludb and the dependencies needed for
dynamodb and backup support into a virtualenv using Python 3 like this:

::

    user@host:~$ virtualenv -p python3 env
    user@host:~$ . env/bin/activate
    user@host:~$ pip install --upgrade pip wheel
    user@host:~$ pip install gludb[dynamodb,backups]

.. |Travis CI Build State| image:: https://travis-ci.org/memphis-iis/GLUDB.svg?branch=master
.. |Documentation State| image:: https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat

