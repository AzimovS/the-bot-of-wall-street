FROM python:3.11-slim as build
WORKDIR ./
COPY . .
RUN pip3 install influxdb-client
RUN pip3 install paho-mqtt
RUN pip3 install pandas

CMD ["python3", "main.py"]