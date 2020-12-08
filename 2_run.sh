#!/bin/bash

function run_image(){
    pref_org=$1
    ver=$2

    echo
    echo "===================================================="
    echo "=====         MQTT_PUB CONTAINER RUN          ====="
    echo "===================================================="
    docker run -d --name mqtt_pub $pref_org/mqtt_pub:$ver

    echo
    echo "===================================================="
    echo "=====         INFLUXDB CONTAINER RUN           ====="
    echo "===================================================="
    cd ./influxdb_config/
    docker run -d --name influxdb --env INFLUXDB_ADMIN_USER=jwclab \
        --env INFLUXDB_ADMIN_PASSWORD=jwclabjwclab --env INFLUXDB_HTTP_AUTH_ENABLED=true \
        -p 8086:8086 -v $PWD/influxdb.conf:/etc/influxdb/influxdb.conf influxdb

    echo
    echo "===================================================="
    echo "=====         MQTT_SUB CONTAINER RUN         ====="
    echo "===================================================="
    docker run -d --name mqtt_sub --restart always $pref_org/mqtt_sub:$ver

    sleep 16

    echo
    echo "===================================================="
    echo "=====       INVOKE HASH CONTAINER RUN        ====="
    echo "===================================================="
    docker run -d --name hash_invoke --restart always $pref_org/invokehash:$ver

    echo
    echo "===================================================="
    echo "=====       BACKUP DATA CONTAINER RUN        ====="
    echo "===================================================="
    docker run -d --name backupdata -v /backup/:/tmp/backup/ $pref_org/backupdata:$ver

    echo
    echo "===================================================="
    echo "=====           API CONTAINER RUN              ====="
    echo "===================================================="
    docker run -d --name api -p 5000:5000 --restart always $pref_org/api:$ver

    echo
    echo "===================================================="
    echo "=====    FIREBASE NOTIFICATION CONTAINER RUN   ====="
    echo "===================================================="
    docker run -d --name firebase --restart always $pref_org/firebase:$ver
}

prefix_org=$1
version=$2

if [ "$prefix_org" != "" ];then
    if [ "$version" != "" ];then
        run_image $prefix_org $version
    else
        echo 
        echo "run image requires exactly version argument."
        echo "Example: ./1_run_images.sh <prefix_org> <version of images>"
        echo
    fi
else  
    echo 
    echo "To run image requires exactly 2 argument."
    echo "Example: ./1_run_images.sh <prefix_org> <version of images>"
    echo
fi
