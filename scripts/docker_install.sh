#!/bin/bash

echo
echo "----> STEP 1"
sudo apt-get remove docker docker-engine docker.io containerd runc

echo
echo "----> STEP 2"
sudo apt-get update

echo
echo "----> STEP 3"
sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common -y

echo
echo "----> STEP 4"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

echo
echo "----> STEP 5"
sudo apt-key fingerprint 0EBFCD88

echo
echo "----> STEP 6"
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

echo
echo "----> STEP 7"
sudo apt-get update

echo
echo "----> STEP 8"
sudo apt-get install docker-ce docker-ce-cli containerd.io -y

echo
echo "----> STEP 9"
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker $USER

echo
echo "----> logout and then login, command 'docker version' to check the install! <-----"