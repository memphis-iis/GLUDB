#!/bin/bash

# Config variables
GCD_BASE=gcd-v1beta2-rev1-2.1.1
NODE_VER=env-0.12.7-prebuilt

set -e
# Know where the script is
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

if [ -d  test_services_env ];
then
    echo "Virtual environment env already exists"
    echo "(You can delete it and rerun this script to reinstall)"
    . test_services_env/bin/activate
else
    echo "Creating virtual environment env with python 2.7"
    virtualenv -p python2.7 test_services_env
    . test_services_env/bin/activate

    # Use latest pip
    pip install --upgrade pip wheel

    # Install deps we need for below
    pip install --upgrade nodeenv supervisor wsgiref meld3 tornado==4.2.1

    # Dynalite install for DynamoDB testing
    nodeenv -p --prebuilt ${NODE_VER}
    npm install -g dynalite

    # gcd install for google cloud datastore testing
    mkdir -p ./test_services_env/gcd
    pushd ./test_services_env/gcd
    wget https://s3.amazonaws.com/public-service/${GCD_BASE}.zip
    rm ./${GCD_BASE}/ ./gcd-data/ -fr
    unzip ${GCD_BASE}.zip
    ./${GCD_BASE}/gcd.sh create -d gcd-data ./gcd-data
    popd

    # s3server is already here and we installed the dep (tornado) above
fi

echo "#!/bin/bash" > /tmp/gcdrun
echo "${SCRIPT_DIR}/test_services_env/gcd/${GCD_BASE}/gcd.sh start ${SCRIPT_DIR}/test_services_env/gcd/gcd-data" >> /tmp/gcdrun
chmod +x /tmp/gcdrun

# Actually run supervisord
touch /tmp/test_services_supervisor.sock
chmod 777 /tmp/test_services_supervisor.sock
PATH=$PATH:$SCRIPT_DIR
echo "Running supervisord in foreground - use CTRL+C to quit"
./test_services_env/bin/supervisord -n -c "$SCRIPT_DIR/supervisord.conf"
