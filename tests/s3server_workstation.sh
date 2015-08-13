#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# This should have been created by running run_tests.sh
source ./env2/bin/activate

python ./s3server.py
