#!/usr/bin/env python
import random
from datetime import datetime

import paho.mqtt.client as mqtt
import time
import json

broker = "mqtt.jwclab.com"
port = 1883
client = mqtt.Client()
client.connect(broker, port)

tmp_std = [25, 26, 27, 28, 29, 30, 32, 33, 34, 35, 36, 38, 40, 38, 36, 35, 34, 33, 32, 30, 29, 28, 27, 26]
dust_std = [0.0, 0.01, 0.02, 0.03, 0.05, 0.08, 0.09, 0.10, 0.11, 0.10, 0.12, 0.11, 0.1, 0.1, 0.11, 0.12, 0.11, 0.1, 0.1,
            0.08, 0.07, 0.06, 0.03, 0.0]

type1_station = ["lienchieu", "haichau", "camle"]
type2_station = ["thanhkhe", "nguhanhson", "sontra"]
type3_station = ["hoavang", "hoangsa", "bachkhoa", "supham"]

while True:
    hour = datetime.now().hour
    tmp = tmp_std[hour]
    hum = 21.8
    dust = dust_std[hour]
    uv = 0.15
    ph = 7
    for k in range(0, 720):
        for i in range(0, len(type1_station)):
            data = {'DEVICE_ID': type1_station[i] + "_station",
                    'TMP': round(tmp + random.uniform(-0.3, 0.3), 2),
                    'HUM': round(hum + random.uniform(-0.3, 0.3), 2),
                    'DUST': round(dust + random.uniform(0, 0.02), 3),
                    'UV': round(uv + random.uniform(-0.003, 0.003), 3),
                    'PH': round(ph + random.uniform(-0.1, 0.1), 2)}
            stationData = json.dumps(data)
            topic = "jwclab/" + data['DEVICE_ID']
            client.publish(topic, stationData)

        for i in range(0, len(type2_station)):
            data = {'DEVICE_ID': type2_station[i] + "_station",
                    'PB': round(tmp + random.uniform(-0.3, 0.3), 2),
                    'FE': round(hum + random.uniform(-0.3, 0.3), 2),
                    'COD': round(dust + random.uniform(0, 0.02), 3),
                    'DO': round(uv + random.uniform(-0.003, 0.003), 3),
                    'ORP': round(ph + random.uniform(-0.1, 0.1), 2)}
            stationData = json.dumps(data)
            topic = "jwclab/" + data['DEVICE_ID']
            client.publish(topic, stationData)

        for i in range(0, len(type3_station)):
            data = {'DEVICE_ID': type3_station[i] + "_station",
                    'COD': round(dust + random.uniform(-0.3, 0.3), 2),
                    'BOD': round(hum + random.uniform(-0.3, 0.3), 2),
                    'NH4': round(dust + random.uniform(0, 0.02), 3),
                    'CLO': round(uv + random.uniform(-0.003, 0.003), 3),
                    'PH': round(ph + random.uniform(-0.1, 0.1), 2)}
            stationData = json.dumps(data)
            topic = "jwclab/" + data['DEVICE_ID']
            client.publish(topic, stationData)

        time.sleep(15)

