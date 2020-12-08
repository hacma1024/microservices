#!/bin/bash
# prefix: jwclab
# version: 1.0
# Example run: ./1_build_images.sh jwclab 1.0

function build_image(){
    pref_org=$1
    ver=$2

    echo
    echo "===================================================="
    echo "=====         MQTT_PUB CONTAINER BUILD         ====="
    echo "===================================================="
    docker build -t $pref_org/mqtt_pub:$ver . -f ./1_demo_station/Dockerfile

    echo
    echo "===================================================="
    echo "=====         MQTT_SUB CONTAINER BUILD         ====="
    echo "===================================================="
    docker build -t $pref_org/mqtt_sub:$ver . -f ./2_mqtt_sub/Dockerfile

    echo
    echo "===================================================="
    echo "=====       INVOKE HASH CONTAINER BUILD        ====="
    echo "===================================================="
    docker build -t $pref_org/invokehash:$ver . -f ./3_invoke_hash_blockchain/Dockerfile

    echo
    echo "===================================================="
    echo "=====       BACKUP DATA CONTAINER BUILD        ====="
    echo "===================================================="
    docker build -t $pref_org/backupdata:$ver . -f ./4_backup_data/Dockerfile

    echo
    echo "===================================================="
    echo "=====       BACKUP DATA CONTAINER BUILD        ====="
    echo "===================================================="
    docker build -t $pref_org/api:$ver . -f ./5_api_for_app/Dockerfile

    echo
    echo "===================================================="
    echo "=====        FIREBASE CONTAINER BUILD          ====="
    echo "===================================================="
    docker build -t $pref_org/firebase:$ver . -f ./8_firebase/Dockerfile
}

prefix_org=$1
version=$2

if [ "$prefix_org" != "" ];then
    if [ "$version" != "" ];then
        build_image $prefix_org $version
    else
        echo 
        echo "build image requires exactly version argument."
        echo "Example: ./1_build_images.sh <prefix_org> <version of images>"
        echo
    fi
else  
    echo 
    echo "To build image requires exactly 2 argument."
    echo "Example: ./1_build_images.sh <prefix_org> <version of images>"
    echo
fi