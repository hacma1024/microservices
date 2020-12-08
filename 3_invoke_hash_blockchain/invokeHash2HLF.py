#!/usr/bin/env python
import hashlib
import json
import time
import os
from configparser import ConfigParser

import requests
from influxdb import InfluxDBClient


def get_token(urlLogin, user, pass_word):
    headers = {
        'Content-Type': 'application/json'
    }
    data = json.dumps({
        "id": user,
        "password": pass_word
    }, indent=4)
    response = requests.post(url=urlLogin, data=data, headers=headers)
    if response.status_code == 200:
        access_token = json.loads(response.content.decode('utf-8'))
        return access_token['accessToken']
    else:
        return response.status_code


def getHashTimeline(device_id):
    databases = client.get_list_database()
    isExistTriggerDB = False
    for k in range(0, len(databases)):
        if databases[k]['name'] == databaseName:
            isExistTriggerDB = True
            break
    if isExistTriggerDB:
        client.switch_database(databaseName)
        result = client.query('select "%s_hash" from %s' % (device_id, databaseName))
        if len(result) == 0:
            result = dateTime_default
        else:
            trigger_time = list(result.get_points(measurement=databaseName))[-1]
            result = trigger_time["%s_hash" % device_id]
        return result
    else:
        client.create_database(databaseName)
        client.switch_database(databaseName)
        result = dateTime_default
        return result


def hashNoFilter(host_influx, port_influx, username_influx, password_influx):
    influx_client = InfluxDBClient(host=host_influx, port=port_influx, username=username_influx,
                                   password=password_influx)
    db_list = influx_client.get_list_database()
    databases = []
    for k in range(0, len(db_list)):
        if db_list[k]['name'][-7:] == "station":
            databases.append(db_list[k]['name'])
    hash_arr = []
    for station_id in databases:
        # get hash timeline
        influx_client.switch_database(station_id)
        hash_timeline = getHashTimeline(station_id)

        # query data
        result = influx_client.query('select * from %s where '
                                     'time >= \'%s\'' % (station_id, hash_timeline))
        data_list = list(result.get_points(measurement=station_id))

        # print(data_list)
        if len(data_list) > 0:
            start_time = data_list[0]['time']
            end_time = data_list[-1]['time']
            dateTime = str(start_time) + str("--") + str(end_time)
            station_id = data_list[0]['DEVICE_ID']

            json_body = [
                {
                    "measurement": databaseName,
                    "fields": {
                        "%s_hash" % station_id: end_time
                    }
                }
            ]

            influx_client.switch_database(databaseName)
            influx_client.write_points(json_body)

            md5_hash = hashlib.md5()
            for k in range(0, len(data_list)):
                # print(data_list[k])
                data_encoded = json.dumps(data_list[k]).encode()
                md5_hash.update(data_encoded)
            hash_json = {'id': station_id, 'dateTime': start_time, 'range': dateTime, 'hash': md5_hash.hexdigest()}
            hash_arr.append(hash_json)

    return hash_arr


def invokeHash(host_influx, port_influx, username_influx, password_influx, url_Add, access_token):
    headers = {
        'Content-Type': 'application/json',
        'x-access-token': access_token
    }
    hash_arr = hashNoFilter(host_influx, port_influx, username_influx, password_influx)
    for data in hash_arr:
        data = json.dumps(data, indent=4)
        try:
            response = requests.post(url=url_Add, data=data, headers=headers)
            if response.status_code != 200:
                print(response.status_code)
        except Exception as e:
            print("Error!", e)
            time.sleep(1.5)


if __name__ == '__main__':
    config_object = ConfigParser()
    path = '/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-1])
    config_object.read(os.path.join(path, 'config.ini'))

    config_info = config_object["mqtt_sub"]
    host = config_info["host_influxdb"]
    port = int(config_info["port_influxdb"])
    username = config_info["user_influxdb"]
    password = config_info["pass_influxdb"]
    url_login = config_info["url_login"]
    url_getrecord = config_info["url_getrecord"]
    user_identity = config_info["user_identity"]
    password_identity = config_info["password_identity"]

    config_info = config_object["invoke_hash"]
    url_add = config_info["url_add"]
    dateTime_default = config_info["dateTime_default"]
    databaseName = config_info["databaseName"]
    hash_time = int(config_info["hashtime_minutes"])

    client = InfluxDBClient(host=host, port=port, username=username, password=password)

    token = get_token(url_login, user_identity, password_identity)

    print("Invoking hash to Hyperledger Fabric...")

    while True:
        invokeHash(host, port, username, password, url_add, token)
        time.sleep(hash_time*60)
