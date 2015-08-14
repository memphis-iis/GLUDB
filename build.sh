#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Note that it is assumed that you have a recent version of"
echo "   pip, wheel, and twine"
echo "Currently installed."
echo ""
echo "You should have an account on PyPI that is able to deploy"
echo "gludb (and you'll need to enter your username and password"
echo "if you don't have a ~/.pypirc file)"
echo ""
echo "ALSO: you HAVE checked the version in setup.py, right?"
echo ""
read -p "Are you sure you want to continue? " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

echo "Cleaning up previous build and dist directories"
rm -fr build/ dist/

echo "Cleaning up and re-installing build tool virtualenv"
rm -fr build_env/
virtualenv -p python3 build_env
. build_env/bin/activate
pip install --upgrade pip wheel
pip install --upgrade twine

echo "Building source distribution"
python setup.py sdist

echo "Building universal wheel"
python setup.py bdist_wheel --universal

echo "Uploading to PyPI using twine"
twine upload dist/*
