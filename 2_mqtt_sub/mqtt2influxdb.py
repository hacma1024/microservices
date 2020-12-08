#!/usr/bin/env python
import os

import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
import json
import requests
from configparser import ConfigParser
from datetime import datetime
import time


def get_token(urlLogin, user, pwd):
    headers = {
        'Content-Type': 'application/json'
    }
    data = json.dumps({"id": user, "password": pwd}, indent=4)
    response = requests.post(url=urlLogin, data=data, headers=headers)
    if response.status_code == 200:
        access_token = json.loads(response.content.decode('utf-8'))
        return access_token['accessToken']
    else:
        return response.status_code


def check_station(url_GetRecord, acc_token, station):
    headers = {
        'Content-Type': 'application/json',
        'x-access-token': acc_token
    }
    station = "INFO_" + station
    data = json.dumps({"id": station}, indent=4)
    try:
        response = requests.post(url=url_GetRecord, data=data, headers=headers)
        return response.status_code
    except Exception as e:
        print("Error!", e)
        time.sleep(1)


def get_set_db(inf_client):
    db_list = inf_client.get_list_database()
    db_set = set()
    for k in range(0, len(db_list)):
        if db_list[k]['name'][-7:] == "station":
            db_set.add(db_list[k]['name'])
    return db_set


def on_connect(mqtt_client, userdata, flags, rc):
    mqtt_client.subscribe(mqtt_topic)


def on_message(client, userdata, msg):
    dict_data = json.loads(msg.payload.decode("utf-8"))
    station_id = str(msg.topic).split("/")[1]
    json_body = [
        {
            "measurement": station_id,
            "fields": dict_data
        }
    ]
    if station_id in databases:
        influx_client.switch_database(station_id)
        influx_client.write_points(json_body)
    else:
        if check_station(urlGetRecord, token, station_id) == 200:
            databases.add(station_id)
            influx_client.create_database(station_id)
            influx_client.switch_database(station_id)
            influx_client.write_points(json_body)


if __name__ == '__main__':
    config_object = ConfigParser()
    path = '/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-1])
    config_object.read(os.path.join(path, 'config.ini'))

    config_info = config_object["mqtt_pub"]
    broker = config_info["broker"]
    port_mqtt = int(config_info["port"])

    config_info = config_object["mqtt_sub"]
    mqtt_topic = config_info["topic"]
    host = config_info["host_influxdb"]
    port = int(config_info["port_influxdb"])
    username = config_info["user_influxdb"]
    password = config_info["pass_influxdb"]
    url_login = config_info["url_login"]
    urlGetRecord = config_info["url_getrecord"]
    user_identity = config_info["user_identity"]
    password_identity = config_info["password_identity"]

    token = str(get_token(url_login, user_identity, password_identity))
    # print(token)

    client = mqtt.Client()
    client.connect(broker, port_mqtt)
    print("Connected to mqtt broker!")

    influx_client = InfluxDBClient(host=host, port=port, username=username, password=password)
    print("Connected to Influxdb!")

    databases = get_set_db(influx_client)

    print("Processing...")
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()
