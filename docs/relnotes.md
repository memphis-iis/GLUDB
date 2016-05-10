# GLUDB Release Notes

## v0.1.6

Fix for v0.1.5 - we now support the sqlite backend across multiple threads. We
also detect and raise an error when the in-memory sqlite feature (where
filename == ":memory:") is used across multiple threads (because each thread
would receive it's own copy of the database)

## v0.1.5

***Broken Release*** This release was only to fix the sqlite backend - and that
fix wasn't correct. This is why you write good unit tests!

## v0.1.4

We no longer clobber __init__ in DBObject-annotated classes. We throw
a TypeError instead.

## v0.1.3

Made the automatic date-time fields `_create_date` and `_last_update` official
(including docs on how they differ from versioning dates). Also added a small
util function to parse `now_field()` results.

## v0.1.2

Bug-fix only version - has fix for missing records when `find_one` is called:
now None is returned (instead of an exception being thrown)

## v0.1.1

Finished the bulk of the documentation, and cleaned up versioning (including
a new helper method for simple classes)

## v0.1.0a2

Second alpha release. Mainly a README and procedural update to the previous
alpha release

## v0.1.0a1

First alpha release. Includes 3 backends and basic backup functionality.
Documentation is still lacking.
