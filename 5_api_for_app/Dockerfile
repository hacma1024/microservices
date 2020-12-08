FROM ubuntu
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip3 install paho-mqtt python-etcd influxdb virtualenv flask Flask
COPY ./5_api_for_app/getDataForApi.py /home/python/getDataForApi.py
COPY ./envVar/config.ini /home/python/config.ini
CMD ["/home/python/getDataForApi.py"]
ENTRYPOINT ["python3"]

