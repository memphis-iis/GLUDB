#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

set -e

npm install -g dynalite

pip install virtualenv

virtualenv -p python2.7 dynalite_env
source ./dynalite_env/bin/activate
pip install --upgrade supervisor wsgiref meld3

touch /tmp/dynamodb_supervisor.sock
chmod 777 /tmp/dynamodb_supervisor.sock
./dynalite_env/bin/supervisord -c "$SCRIPT_DIR/supervisord.conf"
