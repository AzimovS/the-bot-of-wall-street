import re
import paho.mqtt.client as mqtt
import influxdb_client

INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "se4as_token"
INFLUXDB_ORG = "se4as"
INFLUXDB_BUCKET = "stocks"

db_client = influxdb_client.InfluxDBClient(
    url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG
)

db_query_api = db_client.query_api()

MQTT_HOST = "localhost"
MQTT_TOPIC_ANALYZER = "analyzer/prediction/#"
MQTT_TOPIC_EXECUTOR = "executor/action"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT with result code "+str(rc))

    # NOTE: Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC_ANALYZER)

timestamp_pattern = re.compile(r'\d+|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z')
def parse_message(payload):
    price_str, timestamp_str = payload.split()
    try:
        predicted_price = float(price_str)
    except ValueError:
        raise ValueError("Incorrect value for price")
    if timestamp_pattern.fullmatch(timestamp_str) is None:
        raise ValueError("Incorrect value for timestamp")
    return (predicted_price, timestamp_str)

def decide_action(predicted_price, latest_price):
    if latest_price < predicted_price:
        return 'buy'
    else:
        return 'sell'

def on_message(client, userdata, msg):
    print(msg.topic+" "+msg.payload.decode())
    stock_symbol = msg.topic.split("/")[-1]
    try:
        predicted_price, timestamp = parse_message(msg.payload.decode())
    except Exception as e:
        print("error decoding message from analyzer:", e)
        return

    query = f'from(bucket:"{INFLUXDB_BUCKET}")\
        |> range(start: 0, stop: {timestamp})\
        |> filter(fn:(r) => r._measurement == "{stock_symbol}")\
        |> filter(fn:(r) => r._field == "Close")'
    result = db_query_api.query(org=INFLUXDB_ORG, query=query)
    if len(result) > 0:
        if len(result[0].records) > 0:
            latest_price = result[0].records[-1].get_value()
            print(stock_symbol, "-", latest_price, "-", result[0].records[-1].get_time())
            action = decide_action(predicted_price, latest_price)
            client.publish(MQTT_TOPIC_EXECUTOR, f"{action} {stock_symbol}")
        else:
            print("No stock prices found for stock", stock_symbol)
    else:
        print("query without results :(")

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_HOST, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
mqtt_client.loop_forever()