from influxdb import InfluxDBClient
from datetime import datetime, timedelta
from configparser import ConfigParser
import hashlib
import json
from flask import Flask
import requests
import os

app = Flask(__name__)


def get_token(urllogin, user, pw):
    headers = {
        'Content-Type': 'application/json'
    }
    data = json.dumps({
        "id": user,
        "password": pw
    }, indent=4)

    response = requests.post(url=urllogin, data=data, headers=headers)

    if response.status_code == 200:
        access_token = json.loads(response.content.decode('utf-8'))
        return access_token['accessToken']
    else:
        return []


def getHashBlockchain(access_token, url_hbt, station_id, start_time, end_time):
    header = {
        "Content-Type": "application/json",
        "x-access-token": access_token
    }
    data = json.dumps({
        "id": station_id,
        "start": start_time,
        "end": end_time
    }, indent=4)

    response = requests.post(url=url_hbt, data=data, headers=header)

    if response.status_code == 200:
        hash_arr = json.loads(response.content.decode('utf-8'))
        return hash_arr
    else:
        return []


def hashDataInfluxdb(influx_client, station_id, start_time, end_time):
    influx_client.switch_database(station_id)
    results = influx_client.query('select * from %s where'
                                  ' time > \'%s\' and time < \'%s\'' % (station_id, start_time, end_time))
    data_list = list(results.get_points(measurement=station_id))

    md5_hash = hashlib.md5()
    for k in range(0, len(data_list)):
        # print(data_list[k])
        data_encoded = json.dumps(data_list[k]).encode()
        md5_hash.update(data_encoded)
    return md5_hash.hexdigest()


def readDataFromTxt(backup_directory, station_name, date, start, end):
    path = backup_directory + station_name + "/" + date + ".txt"
    target_file = open(path, "r")
    # start = "2020-10-24T07:08:17.898955Z"
    # end = "2020-10-24T07:15:03.255985Z"
    data = target_file.read().split("\n")
    data_dict = {}
    for sub_data in data:
        sub_data_list = sub_data.split(", ")
        sub_data_dict = {}
        for data in sub_data_list:
            key_value = data.split(": ")
            try:
                sub_data_dict[key_value[0]] = key_value[1]
            except Exception:
                pass
        try:
            key = sub_data_list[0].split(": ")[1]
            value = sub_data_dict
        except Exception:
            pass
        data_dict[key] = value

    res = ''
    for key in data_dict:
        if start <= key <= end:
            res += str(data_dict[key])
    return res


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
    tokens = getTokensFcm(client)
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
        response = requests.post(url, data=data_json, headers=headers)
        if response.status_code == 200:
            print("Push notification from %s station successful!" % station_id)
        else:
            print("Push notification from %s station failure!" % station_id)


def getHistoryDataForApi(influx_client, access_token, urlhisbytime, station_id, start_time, end_time):
    influx_client.switch_database(station_id)
    start_query_time = start_time
    end_query_time = end_time
    start_time = str(datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%SZ') - timedelta(minutes=10)) \
                     .replace(" ", "T") + "Z"
    end_time = str(datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%SZ') + timedelta(minutes=10)).replace(" ", "T") + "Z"
    hash_arr = getHashBlockchain(access_token, urlhisbytime, station_id, start_time, end_time)
    if len(hash_arr['response']) > 0:
        isValid = False
        for k in range(0, len(hash_arr['response'])):
            time_range = str(hash_arr['response'][k]['range']).split("--")
            start = time_range[0][:-8] + 'Z'
            end = str(datetime.strptime(time_range[1][:-8] + 'Z', '%Y-%m-%dT%H:%M:%SZ') + timedelta(seconds=1)) \
                      .replace(" ", "T") + "Z"
            blockchain_hash = hash_arr['response'][k]['hash']
            influx_hash = hashDataInfluxdb(influx_client, station_id, start, end)
            if blockchain_hash != influx_hash:
                isValid = False
                title_notification = "Data is not synchronized"
                message = "From " + start + " to " + end
                pushNotificationFirebase(title_notification, message)
                break
            else:
                isValid = True

        if isValid:
            results = influx_client.query('select * from %s '
                                          'where time >= \'%s\' '
                                          'and time <= \'%s\'' % (station_id, start_query_time, end_query_time))
            data_list = list(results.get_points(measurement=station_id))
            return str(data_list).replace("[", "").replace("]", "").replace("\'", "\""), 200
        else:
            print("Restore data from txt file!\n")
            date = start_time.split("T")[0]
            res = readDataFromTxt(backup_directory, station_id, date, start, end)
            return res.replace("\'", "\""), 200
    else:
        print("Restore data from txt file!\n")
        start_time = str(datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%SZ') + timedelta(minutes=10)) \
                         .replace(" ", "T") + "Z"
        end_time = str(datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%SZ') - timedelta(minutes=10)) \
                       .replace(" ", "T") + "Z"
        date = start_time.split("T")[0]
        res = readDataFromTxt(backup_directory, station_id, date, start_time, end_time)
        return res.replace("\'", "\""), 200


def getNowDataForStation(influx_client, station_id):
    influx_client.switch_database(station_id)
    end_time = str(datetime.utcnow()).replace(" ", "T") + "Z"
    result = influx_client.query('select * from %s '
                                 'where time >= \'%s\' - 1m order by time desc limit 1' % (station_id, end_time))
    now_data = list(result.get_points(measurement=station_id))
    return now_data[0], 200


def getNowDataForStations(influx_client):
    db_list = influx_client.get_list_database()
    databases = set()
    for k in range(0, len(db_list)):
        if db_list[k]['name'][-7:] == "station":
            databases.add(db_list[k]['name'])
    nowData = []
    for station_id in databases:
        influx_client.switch_database(station_id)
        end_time = str(datetime.utcnow()).replace(" ", "T") + "Z"
        result = influx_client.query('select * from %s '
                                     'where time >= \'%s\' - 1m order by time desc limit 1' % (station_id, end_time))
        dataStation = list(result.get_points(measurement=station_id))
        print(dataStation)
        keys = set()
        try:
            for key, value in dataStation[0].items():
                if value is None:
                    keys.add(key)
        except:
            pass
        if len(keys) > 0:
            for key in keys:
                del dataStation[0][key]
        if len(dataStation) > 0:
            nowData.append(dataStation)
    return str(nowData).replace("[", "").replace("]", "").replace("\'", "\""), 200


def storeTokensFCM(influxdb_client, tokenfcm):
    tokensFCMDatabase = 'tokenfcm'
    databases = influxdb_client.get_list_database()
    token_dict = {
        'token': tokenfcm
    }

    token_json = [
        {
            "measurement": tokensFCMDatabase,
            "fields": token_dict
        }
    ]
    # print(token_json)

    isExistDB = False
    for k in range(0, len(databases)):
        if databases[k]['name'] == tokensFCMDatabase:
            isExistDB = True
            break
    if isExistDB:
        try:
            influxdb_client.switch_database(tokensFCMDatabase)
            influxdb_client.write_points(token_json)
            return "Successful token storage into existed database!", 200
        except Exception as e:
            print(e)

    else:
        try:
            influxdb_client.create_database(tokensFCMDatabase)
            influxdb_client.switch_database(tokensFCMDatabase)
            influxdb_client.write_points(token_json)
            return "Successful token storage into new database!", 200
        except Exception as e:
            print(e)
    return "Failure token storage!", 500


def deleteTokensFCM(influxdb_client, tokenfcm):
    databases = influxdb_client.get_list_database()
    print(databases)

    isExistDB = False
    for k in range(0, len(databases)):
        if databases[k]['name'] == tokensFcmDatabase:
            isExistDB = True
            break
    if isExistDB:
        try:
            influxdb_client.switch_database(tokensFcmDatabase)
            result = influxdb_client.query('select * from %s' % tokensFcmDatabase)
            token_list = list(result.get_points(measurement=tokensFcmDatabase))
            print(token_list, tokenfcm)
            for token in token_list:
                if token['token'] == tokenfcm:
                    # print(token['time'])
                    result = influxdb_client.query('delete from %s where time > \'%s\' - 1ms and time <  \'%s\' + 1ms'
                                                   % (tokensFcmDatabase, token['time'], token['time']))
                    return "Delete token successful!", 200
        except Exception as e:
            print(e)

    return "Delete token failure!", 500


@app.route('/storetoken/<tokenfcm>', methods=['POST'])
def storeTokensFcm(tokenfcm):
    result = storeTokensFCM(client, tokenfcm)
    return result


@app.route('/deletetoken/<tokenfcm>', methods=['POST'])
def deleteTokensFcm(tokenfcm):
    result = deleteTokensFCM(client, tokenfcm)
    return result


@app.route('/nowData/')
def dataForAll():
    result = getNowDataForStations(client)
    return result


@app.route('/nowData/<station_id>')
def dataForOne(station_id):
    result = getNowDataForStation(client, station_id)
    return result


@app.route('/historyData/<station_id>/<start_time>--<end_time>')
def history(station_id, start_time, end_time):
    result = getHistoryDataForApi(client, token, urlHistoryByTime, station_id, start_time, end_time)
    return result


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

    config_info = config_object["api"]
    urlHistoryByTime = config_info["url_historybytime"]

    config_info = config_object["invoke_hash"]
    hashtime_minutes = config_info["hashtime_minutes"]

    config_info = config_object["backup"]
    backup_directory = config_info["backup_directory"]

    config_info = config_object["firebase"]
    auth = config_info["auth"]
    tokensFcmDatabase = config_info["tokensFcmDatabase"]

    token = get_token(url_login, user_identity, password_identity)
    client = InfluxDBClient(host=host, port=port, username=username, password=password)
    app.run(host="0.0.0.0", port=5000)
