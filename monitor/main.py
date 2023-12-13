import paho.mqtt.client as mqtt
import influxdb_client
import pandas as pd
from influxdb_client.client.write_api import SYNCHRONOUS

# mqtt
broker = 'localhost'
port = 1883
stock_added_topic = "monitor/stock-added"
stock_list_topic = "monitor/stock-list"
# influxdb
bucket = "stocks"
org = "se4as"
token = "se4as_token"
url = "http://localhost:8086"
time_sleep = 1

db_client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

stock_to_row_id = dict()

def on_connect(mqtt_client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    mqtt_client.subscribe(stock_added_topic)
    mqtt_client.subscribe(stock_list_topic)


def save_entries_to_db(stock_symbol, start_row, end_row):
    stock_data = pd.read_csv(f'./stocks/{stock_symbol}.csv', header=0)
    stock_data = stock_data.loc[start_row:end_row]
    write_api = db_client.write_api(write_options=SYNCHRONOUS)
    for index, row in stock_data.iterrows():
        data_point = {
            "measurement": stock_symbol,
            "tags": {},
            "time": row['Date'],
            "fields": {col: row[col] for col in stock_data.columns if col != 'Date'}
        }
        write_api.write(bucket=bucket, org=org, record=data_point)
        stock_to_row_id[stock_symbol] = index


def on_message(mqtt_client, userdata, message):
    if message.topic == stock_added_topic:
        stock_symbol = message.payload.decode()
        print("data added")
        save_entries_to_db(stock_symbol, start_row=0, end_row=50)
    elif message.topic == stock_list_topic:
        print(message.payload.decode())
        stock_symbol = message.payload.decode()
        start_row = stock_to_row_id[stock_symbol]
        save_entries_to_db(stock_symbol, start_row, start_row + 1)


def main():
    mqtt_client = mqtt.Client(client_id="monitor")
    mqtt_client.connect(broker, port)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.loop_forever()


if __name__ == '__main__':
    main()
