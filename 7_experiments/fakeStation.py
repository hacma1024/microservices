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

while True:
        data = {'DEVICE_ID': "test_station",
                # 'TMP': round(random.uniform(0, 50), 2),
                # 'hum': round(random.uniform(0, 50), 2),
                # 'DUST': round(random.uniform(0, 50), 2),
                # 'uv': round(random.uniform(0, 50), 2),
                # 'PH': round(random.uniform(0, 50), 2),
                # 'do': round(random.uniform(0, 50), 2),
                # 'KH': round(random.uniform(0, 50), 2),
                '101': round(random.uniform(0, 50), 2),
                '102': round(random.uniform(0, 50), 2),
                '103': round(random.uniform(0, 50), 2)}
        stationData = json.dumps(data)
        topic = "jwclab/" + data['DEVICE_ID']
        client.publish(topic, stationData)

        time.sleep(5)

