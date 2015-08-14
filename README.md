GLUDB
=============

![Travis CI Build State](https://travis-ci.org/memphis-iis/GLUDB.svg?branch=master)
[Travis CI Details](https://travis-ci.org/memphis-iis/GLUDB)

Generalized Learning Utilities Database Library
--------------------------------------------------

For more GLU, see also
[SuperGLU](https://github.com/GeneralizedLearningUtilities/SuperGLU)

GLUDB is meant to provide a fairly simple way to read/write data to some
popular datastores (like DynamoDB and Google Cloud Datastore). Depending on
the data backend, we hope to provide:

* A simple abstraction layer for annotating classes that should be stored in
  the database
* Support for versioning by automatically storing change history when possible
* A lightweight permissions module for handling authenticated read and write
* Limited query support
* Automated, configurable backup scheduling

To claim version 1.0 status, we will need to implement backend adaptors for:
* DynamoDB
* Google Cloud Datastore
* MongoDB

We are currently planning on supporting both Python 2 (2.7+) and Python 3
(3.4+). *However*, please keep in mind that we will be emphasizing Python 3
going forward.

Installing
------------

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
