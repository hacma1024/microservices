import os
import time
from configparser import ConfigParser
from influxdb import InfluxDBClient


def insertData(influxdb_client, measurement):
    json_body = [
        {
            "measurement": measurement,
            "fields": {
                'time': 1602476126057783337,
                'TMP': 1.0,
                'HUM': 1.0,
                'DUST': 1.0,
                'UV': 1.0,
                'PH': 1.0
            }
        }
    ]

    influxdb_client.switch_database(measurement)
    influxdb_client.write_points(json_body)


if __name__ == '__main__':
    config_object = ConfigParser()
    path = '/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-1])
    config_object.read(os.path.join(path, 'config.ini'))

    config_info = config_object["mqtt_sub"]
    host = config_info["host_influxdb"]
    port = int(config_info["port_influxdb"])
    username = config_info["user_influxdb"]
    password = config_info["pass_influxdb"]

    influx_client = InfluxDBClient(host=host, port=port, username=username, password=password)

    station = 'haichau_station'


    insertData(influx_client, station)
    # time.sleep(2)
