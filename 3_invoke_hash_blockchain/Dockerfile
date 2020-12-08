FROM ubuntu
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip3 install paho-mqtt python-etcd influxdb
COPY ./3_invoke_hash_blockchain/invokeHash2HLF.py /home/python/invokeHash2HLF.py
COPY ./envVar/config.ini home/python/config.ini
CMD ["/home/python/invokeHash2HLF.py"]
ENTRYPOINT ["python3"]

