#docker run --name <name> <image:tag>
FROM jwclab/ubuntu1804-ssh-private-git:1.2

#update ubuntu
RUN apt-get update

#install the build-essential package
RUN apt-get install -y python3 python3-pip
RUN pip3 install paho-mqtt python-etcd influxdb

#copy script
COPY ./1_demo_station/demo_station_mqtt_pub.py /home/python/demo_station_mqtt_pub.py

#The CMD specifies arguments that will be fed to the ENTRYPOINT.
CMD ["/home/python/demo_station_mqtt_pub.py"]
ENTRYPOINT ["python3"]

