#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Get $1 for the python number and then shift 0 and 1
# out so that we can pass parm along with $*
py_ver="$1"
shift

# Stop on any failures - note that we do this AFTER our
# shift calls above
set -e

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

    reset)
        echo "Received reset command - deleting env2 and env3"
        rm "$SCRIPT_DIR/env2" -fr
        rm "$SCRIPT_DIR/env3" -fr
        echo "Done - exiting"
        exit 3
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
