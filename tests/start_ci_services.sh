#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

set -e

# Dynalite install for DynamoDB testing
npm install -g dynalite

# gcd install for google cloud datastore testing
GCD_BASE=gcd-v1beta2-rev1-2.1.1
wget http://storage.googleapis.com/gcd/tools/${GCD_BASE}.zip
unzip ${GCD_BASE}.zip
${SCRIPT_DIR}/${GCD_BASE}/gcd.sh create -d gcd-data ${SCRIPT_DIR}/gcd-data
echo "#!/bin/bash" > /tmp/gcdrun
echo "${SCRIPT_DIR}/${GCD_BASE}/gcd.sh start ${SCRIPT_DIR}/gcd-data" >> /tmp/gcdrun
chmod +x /tmp/gcdrun

# setup a virtualenv with supervisord to run our services
pip install virtualenv

virtualenv -p python2.7 dynalite_env
source ./dynalite_env/bin/activate
pip install --upgrade supervisor wsgiref meld3

touch /tmp/dynamodb_supervisor.sock
chmod 777 /tmp/dynamodb_supervisor.sock
./dynalite_env/bin/supervisord -c "$SCRIPT_DIR/supervisord.conf"
