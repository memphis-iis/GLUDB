#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Cleaning up previous build and dist directories"
rm -fr build/ dist/

echo "Building source distribution"
python setup.py sdist

echo "Building universal wheel"
python setup.py bdist_wheel --universal
