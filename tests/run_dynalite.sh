#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

set -e

npm install -g dynalite

pip install virtualenv

pushd tests
virtualenv -p python2.7 dynalite_env
source ./dynalite_env/bin/activate
pip install --upgrade supervisor wsgiref meld3
./dynalite_env/bin/supervisorctl start dynalite
popd
