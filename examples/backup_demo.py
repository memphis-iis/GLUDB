"""This is a VERY simple backup demo. Generally this file would be split across
3 different places:

 1. The DBObject classes would be defined as part of your model/biz/etc classes
 2. The database config would be part of your config/startup code
 3. The actual backup script would import all of the above and then run

Dependencies you'll need installed when this is running:

 * gludb (obviously)
 * boto (because the backup module currently only supports Amazon S3)
"""


##############################################################################
# Model classes

from gludb.simple import DBObject, Field


@DBObject(table_name='MyDataTable')
class MyData(object):
    name = Field('')
    descrip = Field('')


##############################################################################
# Config

from gludb.config import default_database, Database

default_database(Database('sqlite', filename=':memory:'))
MyData.ensure_table()

# A little extra config - we need some records!
MyData(name='Alice', descrip='A Person').save()
MyData(name='Bob', descrip='Another Person').save()


##############################################################################
# Our backup script

from gludb.backup import Backup


def main():
    AWS_ACCESS_KEY = 'Enter-Yours-Here'
    AWS_SECRET_KEY = 'Enter-Yours-Here'
    BUCKET_NAME = 'Enter-Yours-Here'

    if 'Enter-Yours-Here' in [AWS_ACCESS_KEY, AWS_SECRET_KEY, BUCKET_NAME]:
        print("You need to change this file and supply some AWS information")
        return

    backup = Backup(
        aws_access_key=AWS_ACCESS_KEY,
        aws_secret_key=AWS_SECRET_KEY,
        bucketname=BUCKET_NAME
    )

    backup.add_class(MyData)
    backup.run_backup()

    # Backups are DBObject's! So we'll just pretty print the backup object to
    # show what we did...
    def pretty_json(json):
        import json
        parsed = json.loads(backup.to_data())
        return json.dumps(parsed, indent=4, sort_keys=True)
    print("Backup completed: here's the backup object")
    print(pretty_json(backup.to_data()))

if __name__ == "__main__":
    main()
