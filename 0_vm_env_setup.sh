#!/bin/bash

echo
echo "===================================================="
echo "=====               GO INSTALL                 ====="
echo "===================================================="
sh ./scripts/go_install.sh

echo
echo "===================================================="
echo "=====             DOCKER INSTALL               ====="
echo "===================================================="
sh ./scripts/docker_install.sh

echo
echo "===================================================="
echo "=====         DOCKER-COMPOSE INSTALL           ====="
echo "===================================================="
sh ./scripts/docker_compose_install.sh

# set working directory in vagrant
if [ $USER == "vagrant" ]; then
    echo "You are in vagrant machine"
    echo "cd /vagrant" >> /home/vagrant/.profile
else
    echo "You are not in vagant machine"
fi

