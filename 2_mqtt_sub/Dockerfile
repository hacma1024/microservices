FROM ubuntu
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip3 install paho-mqtt python-etcd influxdb
COPY ./2_mqtt_sub/mqtt2influxdb.py /home/python/mqtt2influxdb.py
COPY ./envVar/config.ini /home/python/config.ini
CMD ["/home/python/mqtt2influxdb.py"]
ENTRYPOINT ["python3"]

