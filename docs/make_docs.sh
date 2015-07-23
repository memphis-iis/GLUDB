#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Stop on any failures - note that we do this AFTER our
# shift calls above
set -e

# Use our virtualenv (and create if necessary)
VE_DIR="$SCRIPT_DIR/env"
if [ -d "$VE_DIR" ];
then
    echo "$VE_DIR already exists"
    source "$VE_DIR/bin/activate"
else
    echo "Creating $VE_DIR"
    virtualenv -p python3 "$VE_DIR"
    source "$VE_DIR/bin/activate"
    pip install --upgrade pip setuptools wheel
    pip install --upgrade mkdocs
    pip install --upgrade -r ../dev-requirements.txt
    pip install -e ..
fi

cd ..
echo "In $(pwd), running:"
echo "  mkdocs $*"
mkdocs $*
