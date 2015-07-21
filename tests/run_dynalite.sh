#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

set -e

npm install -g dynalite

sudo pip install virtualenv

pushd tests
virtualenv -p python2.7 dynalite_env
source ./dynalite_env/bin/activate
pip install --upgrade supervisor wsgiref meld3
./dynalite_env/bin/supervisorctl start dynalite
popd


# Figure out to do about our python version
case "$py_ver" in
    2)
        VE_VER=python2
        VE_DIR="$SCRIPT_DIR/env2"
        ;;

    3)
        VE_VER=python3
        VE_DIR="$SCRIPT_DIR/env3"
        ;;

    *)
        echo "Run with 2 or 3 for Python2 or Python3 testing, all other parms passed to nose"
        exit 2
esac

# Use our virtualenv (and create if necessary)
if [ -d "$VE_DIR" ];
then
    echo "$VE_DIR already exists"
    source "$VE_DIR/bin/activate"
else
    echo "Creating $VE_DIR for $VE_VER"
    virtualenv -p $VE_VER "$VE_DIR"
    source "$VE_DIR/bin/activate"
    pip install --upgrade -r ../dev-requirements.txt
    pip install -e ..
fi

# Tell what we're doing and then do it
# Note that python 2 send --version to stderr, but 3 sends to stdout
echo "Using Python version: $(python --version 2>&1)"
echo "Using nose version: $(nosetests --version)"
echo nosetests -w "$SCRIPT_DIR" $*

# test config
export DEBUG=1

# Some notes
echo "Be sure DynamoDB Local is running for dyanmodb backend tests"

nosetests -w "$SCRIPT_DIR" $*
