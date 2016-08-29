#!/bin/bash

# We assume that we are running in the Docker container defined by ../Dockerfile
export IN_DOCKER=1
cd /var/testing

# Start up postgres manually
su -m postgres -c "/etc/init.d/postgresql start"

# This should demonize
supervisord -c "/var/testing/supervisord.docker.conf"

# HACK: Sleep 1 second for each process + 1 for good measure
sleep 6

git clone https://github.com/memphis-iis/GLUDB.git
cd GLUDB

echo "Performing env setup first"
./tests/run_tests.sh 2 no-tests
./tests/run_tests.sh 3 no-tests
echo "Starting Python 2 testing"
./tests/run_tests.sh 2 --with-xunit --xunit-file=/var/testing/xunit-tests-py2.xml
echo "Starting Python 3 testing"
./tests/run_tests.sh 3 --with-xunit --xunit-file=/var/testing/xunit-tests-py3.xml

# TODO: remove this after we get the output somehow
echo "PRESS ANY KEY TO CONTINUE"
read -n 1 -s
