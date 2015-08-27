"""GLUDB provides a fairly simple way to read/write data to some popular
datastores like Amazon's DynamoDB and Google Cloud Datastore. We provide:

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
"""
