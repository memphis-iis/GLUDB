# GLUDB Testing

Currently we expect developers to be running local unit tests. We also have
CI tests running on Travis CI

## Local testing with Docker

First, you need to build the docker image:

```
$ sudo docker build -t gludb-test .
```

(Note that the name `gludb-test` isn't a requirement - you can name your image
whatever your want.)

Then anytime you want to test the master branch, you can just run the image:

```
sudo docker run -i -t gludb-test
```

Of course, you might want to test against the code committed in your current
branch. Assuming that you're current directory is the root of the repository,
you can run:

```
sudo docker run -i -v $(pwd):/var/testing/src-repo -t gludb-test
```

You can check `tests/docker-run-tests.sh` for details, but it's pretty easy:
if there is a git repo inside the Docker container at `/var/testing/src-repo`
then the tests will clone from there instead of the master branch on GitHub.

Some gotchas to look out for:

* These are local CI tests, so the env will be built from scratch: you need an
  active Internet connection
* If you're testing local code, remember that the code will be cloned: you need
  to commit code before it can be tested.
* If you change something that is part of the build (like
  `tests/docker-run-tests.sh`), then you need to rebuild the Docker image

## Local Unit Testing

*Important* -- If you need to run all the tests locally, we highly recommend
using the Docker testing directions above.

Local unit testing can be run via the `run_tests.sh` script in the tests
directory. It takes care of ensuring that there is a virtualenv present
and then using it to run the unit tests via nose. It accepts a single
required parameter specifying the Python version (2 or 3) and optionally
parameters to be passed to `nosetests`. For example, to test against Python
2 "normally" and then against Python 3 with extra verbose output:

    user@GLUDB:~/gludb $ ./tests/run_tests.sh 2
    user@GLUDB:~/gludb $ ./tests/run_tests.sh 3 -v -v

**Important**: We set the environment variables `DEBUG` to `1` in
`run_tests.sh`. This isn't currently in *many* places, but there *are* tests
(e.g. DynamoDB backend testing) that will break without it.

**Important:** you'll need to have local "test servers" running if you want to
execute the tests. That currently means:

* "DynamoDB Local" from Amazon or dynalite (available via npm)
* The gcd test server
* s3server.sh as provided in the tests directory.
* A locally running MongoDB
* A locally running PostgreSQL server (>= 9.5)

The last 2 (MongoDB and Postgres) need to be running locally. You can get the
first 3 via the script `./tests/local_test_services.sh` which will setup an
environment to run all of the above for you. Note that changes to this script
might *also* involve changes to tests/supervisord.conf; *however*, that
configuration file is also used by the Travis-CI script (see below). Proceed
with caution!

## Travis CI Testing

Check out .travis.yml for details.

Perhaps the most important part is that we use the script
`./tests/start_ci_services.sh` to run all the mock backends we need for testing.
As mentioned above, this script shares tests/supervisord.conf with the "local"
testing script.

**Important**: We set the environment variables `travis` to `1` and do NOT
set the `DEBUG` variable. If you need to differentiate between local and
Travis CI testing, this is how you should do it.
