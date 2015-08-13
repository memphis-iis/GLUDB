#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# This should have been created for us in start_ci_server.sh
source ./test_services_env/bin/activate

python ./s3server.py
