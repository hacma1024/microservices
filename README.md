Project: Advance Environment Monitoring Solution

************* Back-end + container *************

ip cloud: 178.128.107.247

*********************************

The structure of the directory:

***

1_demo_station: include a dockerfile -> build mqtt_pub image + a python script -> publish random data.

***

2_mqtt_sub : include a dockerfile -> build mqtt_sub image + a python script -> subcribe data from mqtt broker -> write in influxdb.

authentication influxdb: user = jwclab, password = jwclabjwclab

***

3_invoke_hash_blockchain: include a dockerfile -> build invoke_hash image + a python script -> query data from influxdb, query data blockchain --> compare hash --> invoke blockchain use api

***

4_backup_data_everyday: include a dockerfile -> build backupdata image + a python script -> compare hash -> backup .txt file in /tmp/backup/<station_id>/

***

5_api_for_app: include a dockerfile -> build api image + a python script -> receive requets, get data and return data.

- get now data: <url>:5000/<station_id>
- get history data: <url>:5000/<station_id> <start> <end>

**********************************

Build container:

1. Build mqtt_pub container: 
docker build -t jwclabacr/mqtt_pub:1.1 .
docker push/pull jwclabacr/mqtt_pub:1.1
docker run --name mqtt_pub jwclabacr/mqtt_pub:1.1

2. Build influxdb container:
docker pull influxdb:latest
docker run --name influxdb --env INFLUXDB_ADMIN_USER=jwclab --env INFLUXDB_ADMIN_PASSWORD=jwclabjwclab --env INFLUXDB_HTTP_AUTH_ENABLED=true -p 8086:8086 -v /etc/influxdb/influxdb.conf:/etc/influxdb/influxdb.conf influxdb

3. Build mqtt_sub container:
docker build -t jwclabacr/mqtt_sub:1.1 .
docker push/pull jwclabacr/mqtt_sub:1.1
docker run --name mqtt_pub jwclabacr/mqtt_sub:1.1

4. Build invoke_hash container:
docker build -t jwclabacr/invokehash:1.1 .
docker push/pull jwclabacr/invokehash:1.1
docker run --name invokehash jwclabacr/invokehash:1.1

5. Build backup data container:
docker build -t jwclabacr/backupdata:1.1 .
docker push/pull jwclabacr/backupdata:1.1
docker run --name invokehash jwclabacr/invokehash:1.1

6. Build api container:
docker build -t jwclabacr/api:1.1 .
docker push/pull jwclabacr/api:1.1
docker run --name api -p 5000:5000 jwclabacr/api:1.1

7. Build grafana container:
docker pull grafana:latest
docker run --name grafana grafana

********************************

Config grafana dashboard

1. add source database

2. create dashboard

3. config dashboard -> save





