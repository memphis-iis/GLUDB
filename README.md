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
