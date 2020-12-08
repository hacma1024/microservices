#!/usr/bin/env python
import os
import sys

import paho.mqtt.client as mqtt
import json
import requests
from configparser import ConfigParser
from influxdb import InfluxDBClient


def getTokensFcm(influxdb_client):
    databases = influxdb_client.get_list_database()
    token_devices = set()
    isExistDB = False
    for k in range(0, len(databases)):
        if databases[k]['name'] == tokensFcmDatabase:
            isExistDB = True
            break
    if isExistDB:
        influxdb_client.switch_database(tokensFcmDatabase)
        result = influxdb_client.query('select * from %s' % tokensFcmDatabase)
        tokens = list(result.get_points(measurement=tokensFcmDatabase))
        for token in tokens:
            token_devices.add(token['token'])
    else:
        print("No exist FCM Database!\n")

    return token_devices


def pushNotificationFirebase(title_push, message):
    tokens = getTokensFcm(influx_client)

    for token in tokens:
        data = {
            "notification": {
                "title": title_push,
                "body": message
            },
            "to": token
        }

        data_json = json.dumps(data)

        headers = {
            'Content-type': 'application/json',
            'Authorization': auth
        }
        url = 'https://fcm.googleapis.com/fcm/send'

        # print(data_json, headers)

        response = requests.post(url, data=data_json, headers=headers)

        if response.status_code == 200:
            print("Push notification from %s station successful!" % str(title_push).split(" ")[2])
        else:
            print("Push notification from %s station failure!" % str(title_push).split(" ")[2])


def on_connect(mqtt_client, userdata, flags, rc):
    mqtt_client.subscribe(mqtt_topic)


def on_message(client, userdata, msg):
    dict_data = json.loads(msg.payload.decode("utf-8"))
    station_id = str(msg.topic).split("/")[1]
    fields = list(dict_data.keys())
    fields.remove('DEVICE_ID')
    messages = []
    title_notification = 'Warning from %s station' % str(station_id).split("_")[0]
    for field in fields:
        field_thresh_hold = '%s_thresh_hold' % field
        try:
            thresh_hold_value = thresh_hold[field_thresh_hold]
        except:
            thresh_hold_value = sys.float_info.max
        if dict_data[field] > thresh_hold_value:
            message = field + '(value = ' + str(dict_data[field]) + ') exceeded ' + \
                      str(round(dict_data[field] - thresh_hold_value, 3))
            messages.append(message)

    message_push = str(messages).replace('[', '').replace(']', '').replace('\'', '')
    if len(messages) > 0:
        pushNotificationFirebase(title_notification, message_push)


if __name__ == '__main__':
    config_object = ConfigParser()
    path = '/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-1])
    config_object.read(os.path.join(path, 'config.ini'))

    config_info = config_object["mqtt_pub"]
    broker = config_info["broker"]
    port_mqtt = int(config_info["port"])

    config_info = config_object["mqtt_sub"]
    mqtt_topic = config_info["topic"]

    config_info = config_object["firebase"]
    auth = config_info["auth"]
    tokensFcmDatabase = config_info["tokensFcmDatabase"]

    config_info = config_object["thresh_hold"]
    thresh_hold = {
        "TMP_thresh_hold": float(config_info["tmp"]),
        "HUM_thresh_hold": float(config_info["hum"]),
        "DUST_thresh_hold": float(config_info["dust"]),
        "UV_thresh_hold": float(config_info["uv"]),
        "PH_thresh_hold": float(config_info["ph"]),
        "PB_thresh_hold": float(config_info["pb"]),
        "FE_thresh_hold": float(config_info["fe"]),
        "COD_thresh_hold": float(config_info["cod"]),
        "DO_thresh_hold": float(config_info["do"]),
        "ORP_thresh_hold": float(config_info["orp"]),
        "BOD_thresh_hold": float(config_info["bod"]),
        "NH4_thresh_hold": float(config_info["nh4"]),
        "CLO_thresh_hold": float(config_info["clo"]),
    }

    config_info = config_object["mqtt_sub"]
    host = config_info["host_influxdb"]
    port = int(config_info["port_influxdb"])
    username = config_info["user_influxdb"]
    password = config_info["pass_influxdb"]

    influx_client = InfluxDBClient(host=host, port=port, username=username, password=password)

    client = mqtt.Client()
    client.connect(broker, port_mqtt)
    print("Connected to mqtt broker!")

    print("Processing...")
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()
