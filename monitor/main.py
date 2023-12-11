import paho.mqtt.client as mqtt
import influxdb_client
import random
import pandas as pd
import time
from influxdb_client.client.write_api import SYNCHRONOUS
import os

# mqtt
broker = 'localhost'
port = 1883
stock_added_topic = "monitor/stock-added"
stock_list_topic = "monitor/stock-list"
# influxdb
bucket = "stocks"
org = "se4as"
token = "se4as_token"
url="http://localhost:8086"
time_sleep = 1

db_client = influxdb_client.InfluxDBClient(
   url=url,
   token=token,
   org=org
)


def on_connect(mqtt_client, userdata, flags, rc):
  print("Connected with result code " + str(rc))
  mqtt_client.subscribe(stock_added_topic)
  mqtt_client.subscribe(stock_list_topic)


def on_message(mqtt_client, userdata, message):
  if message.topic == stock_added_topic:
    stock_symbol = message.payload.decode()
    df = pd.read_csv(f'./stocks/{stock_symbol}.csv', header=0)
    json_body = []
    write_api = db_client.write_api(write_options=SYNCHRONOUS)
    for index, row in df.iterrows():
        if index == 100:
            break
        data_point = {
            "measurement": 'stock_price',
            "tags": {},
            "time": row['Date'],  # Assuming you have a 'timestamp' column
            "fields": {col: row[col] for col in df.columns if col != 'Date'}
        }
        print(data_point)
        write_api.write(bucket=bucket, org=org, record=data_point)
    print("data added")

  elif message.topic == stock_list_topic:
    print(message.payload.decode())


def main():
    mqtt_client = mqtt.Client()
    mqtt_client.connect(broker, port)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.loop_forever()


if __name__ == '__main__':
    main()
