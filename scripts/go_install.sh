#!/bin/bash

echo
echo "----> STEP 1"
wget -O ${PWD}/go1.15.linux-amd64.tar.gz "https://golang.org/dl/go1.15.linux-amd64.tar.gz"

echo
echo "----> STEP 2"
sudo tar -C /usr/local -xzf ${PWD}/go1.15.linux-amd64.tar.gz

echo
echo "----> STEP 3"
rm -f ${PWD}/go1.15.linux-amd64.tar.gz
echo "export PATH=$PATH:/usr/local/go/bin" >> $HOME/.profile

echo
echo "----> logout and then login, command 'Go version' to check the install! <-----"