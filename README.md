GLUDB
=============

![Travis CI Build State](https://travis-ci.org/memphis-iis/GLUDB.svg?branch=master)
[Travis CI Details](https://travis-ci.org/memphis-iis/GLUDB)

Generalized Learning Utilities Database Library
--------------------------------------------------

For more GLU, see also
[SuperGLU](https://github.com/GeneralizedLearningUtilities/SuperGLU)

GLUDB is meant to provide a fairly simple way to read/write data to some
popular datastores (like DynamoDB and BigTable). Depending on the data
backend, we hope to provide:


* A simple abstraction layer for annotating classes that should be stored in
  the database
* Support for versioning by automatically storing change history when possible
* A lightweight permissions module for handling authenticated read and write
* Limited query support
* Automated, configurable backup scheduling

To claim version 1.0 status, we will need to implement backend adaptors for:
* DynamoDB
* BigTable
* MongoDB

We are currently planning on supporting both Python 2 (2.7+) and Python 3
(3.4+). *However*, please keep in mind that we will be emphasizing Python 3
going forward.

Testing
----------

Local unit testing can be run via the run_tests.sh script in the tests
directory. It takes care of ensuring that there is a virtualenv present
and then using it to run the unit tests via nose. It accepts a single
required parameter specifying the Python version (2 or 3) and optionally
parameters to be passed to `nosetests`. For example, to test against Python
2 "normally" and then against Python 3 with extra verbose output:

    user@GLUDB $ ./tests/run_tests.sh 2
    user@GLUDB $ ./tests/run_tests.sh 3 -v -v

**Important:** you'll need to have local DynamoDB running. Currently we
recommend DynamoDB Local from Amazon themselves. Whether you use DynamoDB
Local or dynalite, you'll need to start them yourself.

This project is also set up to run on Travis CI. Check out .travis.yml for
details.
