import paho.mqtt.client as mqtt
import influxdb_client
import pandas as pd
import configparser
from influxdb_client.client.write_api import SYNCHRONOUS

config = configparser.ConfigParser()
config.read('config.ini')

STARTTIME = config['influxdb']['STARTTIME']
# mqtt
stock_added_topic = "monitor/stock/added"
stock_removed_topic = "monitor/stock/removed"
topic_for_monitoring = "monitor/completed"
topic_notify_anlyzer = "analyzer/predict/stock"

# influxdb
org = config['influxdb']['ORG']
bucket_name = config['influxdb']['BUCKET_NAME']

db_client = influxdb_client.InfluxDBClient(
    url=config['influxdb']['URL'],
    token=config['influxdb']['TOKEN'],
    org=org
)

stock_to_row_id = dict()
stock_to_monitor = dict()


def on_connect(mqtt_client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    mqtt_client.subscribe(stock_added_topic)
    mqtt_client.subscribe(topic_for_monitoring)


def save_entries_to_db(stock_symbol, start_row, end_row):
    if end_row <= start_row:
        return
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
        write_api.write(bucket=bucket_name, org=org, record=data_point)
        stock_to_row_id[stock_symbol] = index


def is_stock_in_db(stock_symbol):
    query = f'from(bucket:"{bucket_name}")\
    |> range(start: {STARTTIME})\
    |> filter(fn:(r) => r._measurement == "{stock_symbol}")'
    result = db_client.query_api().query(org="se4as", query=query)
    if not result:
        return False
    return True


def on_message(mqtt_client, userdata, message):
    stock_symbol = message.payload.decode()
    if message.topic == stock_removed_topic:
        stock_to_monitor[stock_symbol] = False
        return
    elif message.topic == topic_for_monitoring and not stock_to_monitor[stock_symbol]:
        return

    start_row, end_row = None, None
    if message.topic == stock_added_topic:
        stock_to_monitor[stock_symbol] = True
        if is_stock_in_db(stock_symbol):
            start_row = stock_to_row_id[stock_symbol]
            end_row = start_row + 1
        else:
            start_row = 0
            end_row = 50
    elif message.topic == topic_for_monitoring:
        start_row = stock_to_row_id[stock_symbol]
        end_row = start_row + 1
    save_entries_to_db(stock_symbol, start_row, end_row)
    mqtt_client.publish(topic_notify_anlyzer, stock_symbol)


def main():
    mqtt_client = mqtt.Client(client_id="monitor")
    mqtt_client.connect(config['mqtt']['broker'], int(config['mqtt']['port']))
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.loop_forever()


if __name__ == '__main__':
    main()
