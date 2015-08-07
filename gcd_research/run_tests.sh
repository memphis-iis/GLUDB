#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

VE_DIR="env"

# Use our virtualenv (and create if necessary)
if [ -d "$VE_DIR" ];
then
    echo "$VE_DIR already exists"
    source "$VE_DIR/bin/activate"
else
    echo "Creating $VE_DIR for $VE_VER"
    virtualenv -p python2 "$VE_DIR"
    source "$VE_DIR/bin/activate"
    pip install --upgrade pip wheel
    pip install --upgrade googledatastore==v1beta2-rev1-2.1.2
fi

# test config
export DEBUG=1
export DATASTORE_HOST="http://localhost:8080"
export DATASTORE_DATASET="gcd-data"

python ./test.py
