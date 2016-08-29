FROM        ubuntu:16.04
MAINTAINER  Craig Kelly <cnkelly@memphis.edu>

# Setup - we want tests to be able to tell they're running in a docker container
ENV IN_DOCKER=1

# Install mongo DB - do this first since it requires an apt-get update
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927
RUN echo "deb http://repo.mongodb.org/apt/ubuntu $(cat /etc/lsb-release | grep DISTRIB_CODENAME | cut -d= -f2)/mongodb-org/3.2 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-3.2.list
RUN apt-get update && apt-get install -y mongodb-org
RUN mkdir -p /data/db

# Install everything we need/can get from apt-get
RUN apt-get install -y apt-utils python-software-properties software-properties-common unzip git wget
RUN apt-get install -y python-pip
RUN apt-get install -y python3 python3-dev python3-pip
RUN apt-get install -y openjdk-8-jre-headless
RUN apt-get install -y postgresql-9.5 postgresql-server-dev-9.5
RUN apt-get install -y nodejs-legacy npm

# Now install everything we need from other package managers (except for the
# packages for our mock servers - we do that per section below)
RUN pip2 install --upgrade pip wheel virtualenv
RUN pip2 install --upgrade supervisor wsgiref meld3 tornado==4.2.1
RUN npm install -g npm

# s3 and gcd are install at /var/servers
RUN mkdir -p /var/servers
WORKDIR /var/servers

# Setup Postgresql 9.5 - user, pwd, and db are all named "docker"
USER postgres
RUN /etc/init.d/postgresql start &&\
    psql --command "CREATE USER docker WITH SUPERUSER PASSWORD 'docker';" &&\
    createdb -O docker docker &&\
    sleep 1 &&\
    /etc/init.d/postgresql stop
USER root

# Dynalite
RUN npm install -g dynalite@0.19.1

# GCD - GCD_BASE=gcd-v1beta2-rev1-2.1.1
RUN wget https://s3.amazonaws.com/public-service/gcd-v1beta2-rev1-2.1.1.zip
RUN unzip gcd-v1beta2-rev1-2.1.1.zip
RUN /var/servers/gcd-v1beta2-rev1-2.1.1/gcd.sh create -d gcd-data /var/servers/gcd-data
RUN echo "#!/bin/bash" > /var/servers/gcdrun
RUN echo "/var/servers/gcd-v1beta2-rev1-2.1.1/gcd.sh start /var/servers/gcd-data" >> /var/servers/gcdrun
RUN chmod +x /var/servers/gcdrun

# It's time for our testing environment
RUN mkdir -p /var/testing

# S3 mimic
ADD tests/s3server.py /var/servers/s3server.py
ADD tests/utils.py /var/servers/utils.py

# Actually run supervisor with our config
WORKDIR /var/testing
ADD ./tests/supervisord.docker.conf ./supervisord.docker.conf
ADD ./tests/docker-run-tests.sh ./docker-run-tests.sh
RUN chmod +x ./docker-run-tests.sh

CMD /var/testing/docker-run-tests.sh
