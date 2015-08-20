#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

set -e

# Dynalite install for DynamoDB testing
npm install -g dynalite

# gcd install for google cloud datastore testing
# note: if this file should disappear from Google's download site before they
# have a better solution, Craig saved a copy of the ZIP file in question. See
# him to work around Google's buffoonery.
GCD_BASE=gcd-v1beta2-rev1-2.1.1
wget https://s3.amazonaws.com/public-service/${GCD_BASE}.zip
unzip ${GCD_BASE}.zip
${SCRIPT_DIR}/${GCD_BASE}/gcd.sh create -d gcd-data ${SCRIPT_DIR}/gcd-data
echo "#!/bin/bash" > /tmp/gcdrun
echo "${SCRIPT_DIR}/${GCD_BASE}/gcd.sh start ${SCRIPT_DIR}/gcd-data" >> /tmp/gcdrun
chmod +x /tmp/gcdrun
echo "Dumping contents of /tmp/gcdrun"
cat /tmp/gcdrun

# setup a virtualenv with supervisord to run our services
pip install virtualenv
virtualenv -p python2.7 test_services_env
# Note that s3server.sh depends on the name and location of this virtualenv
source ./test_services_env/bin/activate

# Install supervisord and reqs
pip install --upgrade supervisor wsgiref meld3
# Install s3server reqs
pip install --upgrade tornado==4.2.1

# Actually run supervisord
touch /tmp/test_services_supervisor.sock
chmod 777 /tmp/test_services_supervisor.sock
PATH=$PATH:$SCRIPT_DIR
./test_services_env/bin/supervisord -c "$SCRIPT_DIR/supervisord.conf"
