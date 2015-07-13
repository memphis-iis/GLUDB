#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

if [ "x$2" != "x" ];
then
    echo "Only one run mode at a time!"
    exit 1
fi

case "$1" in
    2)
        VE_VER=python2
        VE_DIR="$SCRIPT_DIR/env2"
        ;;

    3)
        VE_VER=python3
        VE_DIR="$SCRIPT_DIR/env3"
        ;;

    *)
        echo "Run with 2 or 3 for Python2 or Python3 testing"
        exit 2
esac

if [ -d "$VE_DIR" ];
then
    echo "$VE_DIR already exists"
    source "$VE_DIR/bin/activate"
else
    echo "Creating $VE_DIR for $VE_VER"
    virtualenv -p $VE_VER "$VE_DIR"
    source "$VE_DIR/bin/activate"
    pip install --upgrade -r ../dev-requirements.txt
fi

echo "Using nose version:"
nosetests --version

nosetests
