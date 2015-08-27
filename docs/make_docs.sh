#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Stop on any failures - note that we do this AFTER our
# shift calls above
set -e

# TODO: switch from python2 to python3 once we don't need special Python2-only
#       req's for Google Datastore. This means we can remove qualname below

# Use our virtualenv (and create if necessary)
VE_DIR="$SCRIPT_DIR/env"
if [ -d "$VE_DIR" ];
then
    echo "$VE_DIR already exists"
    source "$VE_DIR/bin/activate"
else
    echo "Creating $VE_DIR"
    virtualenv -p python2 "$VE_DIR"
    source "$VE_DIR/bin/activate"
    pip install --upgrade pip setuptools wheel
    pip install --upgrade git+https://github.com/mkdocs/mkdocs
    pip install --upgrade -r ../dev-requirements.txt
    pip install --upgrade -r ../dev-requirements-27.txt
    pip install qualname
    pip install -e ..
fi

cd ..
echo "In $(pwd), running:"

if [ "$1" == "api" ];
then
    shift
    echo "  python2 docs/make_api_docs.py $* > docs/api.md"
    python2 docs/make_api_docs.py $* > docs/api.md
else
    echo "  mkdocs $*"
    mkdocs $*
fi
