#!/bin/bash

echo
echo "----> STEP 1"
sudo curl -L "https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

echo
echo "----> STEP 2"
sudo chmod +x /usr/local/bin/docker-compose

echo
echo "----> logout and then login, command 'docker-compose version' to check the install! <-----"