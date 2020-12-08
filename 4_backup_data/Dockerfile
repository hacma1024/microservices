FROM ubuntu
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip3 install paho-mqtt python-etcd influxdb
COPY ./4_backup_data/backupData.py /home/python/backupData.py
COPY ./envVar/config.ini /home/python/config.ini
CMD ["/home/python/backupData.py"]
ENTRYPOINT ["python3"]

