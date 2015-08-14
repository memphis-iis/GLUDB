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


Testing
----------

Please see tests/README.md for details.

Top-level directory contents
-----------------------------

Some newcomers might find the top-level directory for a little overwhelming.
Here's a complete breakdown of what you see here (in alphabetical order):

* .gitignore - This lists files that will be automatically ignored by git
* .travis.yml - The configuration file use by Travis CI (our continuous
  integration provider)
* build - Created when you use ./build.sh (in .gitignore)
* build.sh - A script to build distributions of the gludb library suitable for
  use by others (and upload to PyPI)
* dev-requirements.txt - Requirements to be installed into a virtualenv used
  for development on gludb. Mainly used by our testing scripts
* dev-requirements-27.txt - Development requirements specific to Python 2.7.
  This is currently necessary because we can only support Google Cloud
  Datastore on Python 2.7
* dist - Holds the final output of the ./build.sh command (in .gitignore)
* docs - Our documentation in mkdocs format (which is one of the two formats
  used by ReadTheDocs.org)
* examples - Simple examples for gludb use
* gludb - Our actual package info
* gludb.egg-info - Created as part of a process developing the gludb package
* LICENSE - The license under which the contents of this repository are placed
* mkdocs.yml - The configuration file for the documentation in the docs
  directory
* README.md - This file
* setup.cfg - Parameters used by setup.py
* setup.py - The main setup file for the gludb package - used by ./build.sh and
  other sources for install, remove, etc
* tests - Location for our unit tests
