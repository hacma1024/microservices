import hashlib
import json
import os
import time
from datetime import datetime, timedelta
from configparser import ConfigParser

import requests
from influxdb import InfluxDBClient


def get_list_db(client):
    db_list = client.get_list_database()
    databases = set()
    for k in range(0, len(db_list)):
        if db_list[k]['name'][-7:] == "station":
            databases.add(db_list[k]['name'])
    return databases


def getTimeBackup(influxdb_client, trigger_db, datetimeDefault, station_id, time_now):
    databases = influxdb_client.get_list_database()
    isExistDB = False
    for k in range(0, len(databases)):
        if databases[k]['name'] == trigger_db:
            isExistDB = True
            break
    json_body = [
        {
            "measurement": trigger_db,
            "fields": {
                "%s_backup" % station_id: time_now
            }
        }
    ]
    if isExistDB:
        influxdb_client.switch_database(trigger_db)
        result = influxdb_client.query('select "%s_backup" from %s' % (station_id, trigger_db))
        influxdb_client.write_points(json_body)
        if len(result) == 0:
            return datetimeDefault
        else:
            backup_time = list(result.get_points(measurement=trigger_db))[-1]
            return backup_time['%s_backup' % station_id]
    else:
        influxdb_client.create_database(trigger_db)
        influxdb_client.switch_database(trigger_db)
        influxdb_client.write_points(json_body)
        return datetimeDefault


def get_token(urlLogin, user, pass_word):
    headers = {
        'Content-Type': 'application/json'
    }
    data = json.dumps({"id": user, "password": pass_word}, indent=4)
    response = requests.post(url=urlLogin, data=data, headers=headers)

    if response.status_code == 200:
        access_token = json.loads(response.content.decode('utf-8'))
        return access_token['accessToken']
    else:
        return response.status_code


def getHashBlockchain(url_HistoryByTime, acc_token, station_id, start_time, end_time):
    headers = {
        'Content-Type': 'application/json',
        'x-access-token': acc_token
    }
    data = json.dumps({
        "id": station_id,
        "start": start_time,
        "end": end_time
    }, indent=4)
    response = requests.post(url=url_HistoryByTime, data=data, headers=headers)

    if response.status_code == 200:
        hash_arr = json.loads(response.content.decode('utf-8'))
        return hash_arr
    else:
        return response.status_code


def hashDataInfluxdb(client, station_id, start_time, end_time):
    client.switch_database(station_id)
    # print(start_time, end_time)
    results = client.query('select * from %s where'
                           ' time >= \'%s\' and time < \'%s\'' % (station_id, start_time, end_time))
    data_list = list(results.get_points(measurement=station_id))
    # print(data_list[0]['time'], data_list[-1]['time'])
    md5_hash = hashlib.md5()
    for k in range(0, len(data_list)):
        # print(data_list[k])
        data_encoded = json.dumps(data_list[k]).encode()
        md5_hash.update(data_encoded)
    # print(start_time, end_time, md5_hash.hexdigest())
    return md5_hash.hexdigest()


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


def pushNotificationFirebase(title_push, message, station_id):
    tokens = getTokensFcm(influx_client)
    for access_token in tokens:
        data = {
            "notification": {
                "title": title_push,
                "body": message
            },
            "to": access_token
        }
        data_json = json.dumps(data)
        headers = {
            'Content-type': 'application/json',
            'Authorization': auth
        }
        url = 'https://fcm.googleapis.com/fcm/send'
        response = requests.post(url, data=data_json, headers=headers)
        if response.status_code == 200:
            print("Push notification from %s station successful!" % station_id)
        else:
            print("Push notification from %s station failure!" % station_id)


def backupDataToText(client, access_token, urlHisByTime, databaseTrigger, datetimeDefault, backupDir):
    databases = get_list_db(client)
    for station_id in databases:
        client.switch_database(station_id)
        now = str(datetime.strptime(str(datetime.utcnow())[:10] + 'T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')).replace(" ", "T") + "Z"
        start_time = getTimeBackup(client, databaseTrigger, datetimeDefault, station_id, now)

        isValidHash = False
        hash_arr = getHashBlockchain(urlHisByTime, access_token, station_id, start_time, now)
        if hash_arr == 500:
            print("Error when connect to blockchain api")
            break

        for k in range(0, len(hash_arr['response'])):
            time_range = str(hash_arr['response'][k]['range']).split("--")
            start = time_range[0][:-8] + 'Z'
            end = datetime.strptime(time_range[1][:-8] + 'Z', '%Y-%m-%dT%H:%M:%SZ') + timedelta(seconds=1)
            blockchain_hash = hash_arr['response'][k]['hash']
            influx_hash = hashDataInfluxdb(client, station_id, start, end)
            if blockchain_hash != influx_hash:
                isValidHash = False
                title_notification = "Data is not synchronized in %s" % station_id
                message = "From " + str(start) + " to " + str(end)
                pushNotificationFirebase(title_notification, message, station_id)
                break
            else:
                isValidHash = True

        if isValidHash:
            results = client.query('select * '
                                   'from %s '
                                   'where time >= \'%s\' and time <= \'%s\'' % (station_id, start_time, now))
            data_list = list(results.get_points(measurement=station_id))
            if len(data_list) > 0:
                try:
                    os.mkdir(backupDir)
                    file_dir = backupDir + station_id + "/"
                    os.mkdir(file_dir)
                except FileExistsError:
                    pass
                file_dir = backupDir + station_id + "/"
                try:
                    os.mkdir(file_dir)
                except FileExistsError:
                    pass
                date = str(datetime.strptime(str(datetime.utcnow())[:10] + 'T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
                           - timedelta(days=1)).replace(" ", "T") + "Z"
                dir_path = file_dir + date[:10] + ".txt"
                file = open(dir_path, "w")
                for k in range(0, len(data_list)):
                    file.write(str(data_list[k]).replace("{", "").replace("}", "").replace("'", "") + "\n")
                print("Backup successfull! \n", dir_path)
                file.close()
        else:
            print("Invalid when compare hash!")


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
    user_identity = config_info["user_identity"]
    password_identity = config_info["password_identity"]

    config_info = config_object["invoke_hash"]
    datetime_default = config_info["dateTime_default"]
    database_trigger = config_info["databaseName"]

    config_info = config_object["api"]
    urlHistoryByTime = config_info["url_historybytime"]

    config_info = config_object["backup"]
    backupTime = int(config_info["backuptime_hours"])
    backupDirectory = config_info["backup_directory"]

    config_info = config_object["firebase"]
    auth = config_info["auth"]
    tokensFcmDatabase = config_info["tokensFcmDatabase"]

    influx_client = InfluxDBClient(host=host, port=port, username=username, password=password)

    token = get_token(url_login, user_identity, password_identity)

    while True:
        backupDataToText(influx_client, token, urlHistoryByTime, database_trigger, datetime_default, backupDirectory)
        time.sleep(backupTime * 86400)
