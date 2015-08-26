# GLUDB Backups

One of the stated goals for gludb was to have a sane, easy method for backing
up the data stored. The current backup functionality provides an easy way to
get all the data you're interested in (as defined by the Storable-derived
classes that you include in your backup) in a single gzip'ed tarball stored
in Amazon S3

If you learn better by example, we have
[one](https://github.com/memphis-iis/GLUDB/blob/master/examples/backup_demo.py)!

## Why Amazon S3

Before describing the backup, we should take a moment to discuss Amazon's S3.
S3 (which stands for "Simple Storage Service") let's you define "buckets" where
you can store large blobs of data, each under it's own key. If you like file system
analogies, you can think of buckets as directories, keys as file names, and the data
stored as file contents. S3 is reasonably priced and offers a variety of ways
to handle access to your data.

Those familiar with Amazon's storage offering might be wondering why we didn't
choose Amazon's Glacier service. There are two main reasons:

1. You might want fairly fast access to your backups. If you want to use the
   backup functionality for snapshots to examine, ETL projects, or for some
   other purpose, Glacier's access time just isn't feasible. (Glacier only
   guarantees that you can access a file within 5 hours.)
2. You can update the storage policy on S3 buckets to archive the contents
   to Glacier after a certain amount of time, so S3 backups can actually use
   Glacier.

In fact, S3 bucket policies mean that you can create fairly sophisticated
backup plans by using different buckets for different kinds of backups. For
instance, you might send daily backups to a bucket where files older than 30
days are deleted. Once a month you could run a backup that archives files to
Glacier every 60 days. That way you have permanent monthly backups in Glacier,
recent monthly backups for instance access, and daily backups for the last
month with instance access

## Requirements for S3

You'll need to have the name of your S3 bucket (which should already exist).
You will also need an AWS Access ID and private key will rights to add data to
buckets. You can create user accounts for accessing S3 (using IAM), add S3
buckets, and configure your buckets by using the
[AWS Console](https://console.aws.amazon.com/).

## Backup setup

From here on our, we're going to assume that you've examined the backup
[example](https://github.com/memphis-iis/GLUDB/blob/master/examples/backup_demo.py)
that we mentioned above.

Assuming that you already have classes defined for storing and reading data
(which you can read about [here](simple.md)), there are really only three
things you need to perform a backup:

1. Create an instance of a gludb.backup.Backup, specifying values for
   `aws_access_key`, `aws_secret_key`, and `bucketname`
2. Add classes (or packages to be backed up) to the instance you created
3. Call perform_backup on the instance you've created.

Let's assume that you've already created an instance of a Backup object:

    from gludb.backup import Backup

    backup = Backup(
        aws_access_key='My Access ID',
        aws_secret_key='My Secret Key',
        bucketname='my-backup-bucket-name'
    )

If you just have a few classes in your model, you can just add them manually:

    from myapp.model import SomeClass, SomeOtherClass

    backup.add_class(SomeClass)
    backup.add_class(SomeOtherClass)

Note that by default, when you call `add_class`, all the base classes that are
also derived from Storable will be added to the backup. If you don't want this
behavior, you can do this with the parameter `include_bases` (which defaults
to true).

    backup.add_class(SomeClass, include_bases=False)
    backup.add_class(SomeOtherClass, include_bases=False)

If all the classes are in one (or a few) packages, you can just add a package
with the `add_package` method:

    backup.add_package("myapp.model")

Note that unlike `add_class`, you specify the package with a string. Also note
that the add_package call will examine all modules and sub-packages for
classes deriving from Storable. Each of those classes will be added to the
backup via a call to `add_class` with `include_bases=True`. When adding a
package:

* You can specify `include_bases`, which will be passed for all classes found.
  If you need to specify something differently for multiple classes, consider
  calling `add_class` instead.
* If you don't want sub-packages to be examined, pass `recurse=False`. The
  _modules_ of the package specified will be scanned, but sub-packages will
  be ignored
