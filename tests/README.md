GLUDB Unit Tests
================

Currently we expect developers to be running local unit tests. We also have
CI tests running on Travis CI

Local Unit Testing
--------------------------

Local unit testing can be run via the `run_tests.sh` script in the tests
directory. It takes care of ensuring that there is a virtualenv present
and then using it to run the unit tests via nose. It accepts a single
required parameter specifying the Python version (2 or 3) and optionally
parameters to be passed to `nosetests`. For example, to test against Python
2 "normally" and then against Python 3 with extra verbose output:

    user@GLUDB $ ./tests/run_tests.sh 2
    user@GLUDB $ ./tests/run_tests.sh 3 -v -v

**Important**: We set the environment variables `DEBUG` to `1` in
`run_tests.sh`. This isn't currently in *many* places, but there *are* tests
(e.g. DynamoDB backend testing) that will break without it.

**Important:** you'll need to have local "test servers" running if you want to
execute the tests. That currently means:

 * "DynamoDB Local" from Amazon or dynalite (available via npm)
 * The gcd test server
 * s3server.sh as provided in this directory.

We are currently working on a script for workstations, but in the mean time
you might find inspiration in the `start_ci_services.sh` script that we use
for CI on travis-ci.org

Travis CI Testing
----------------------

Check out .travis.yml for details.

**Important**: We set the environment variables `travis` to `1` and do NOT
set the `DEBUG` variable. If you need to differentiate between local and
Travis CI testing, this is how you should do it.
