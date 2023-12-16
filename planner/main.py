import json
import paho.mqtt.client as mqtt
import influxdb_client

INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "se4as_token"
INFLUXDB_ORG = "se4as"
INFLUXDB_BUCKET = "portfolio"

db_client = influxdb_client.InfluxDBClient(
    url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG
)

db_query_api = db_client.query_api()

MQTT_HOST = "localhost"
MQTT_TOPIC_ANALYZER = "planner/prediction/#"
MQTT_TOPIC_EXECUTOR = "executor/action"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT with result code "+str(rc))

    # NOTE: Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC_ANALYZER)

def decide_action(predicted_price, latest_price, stock_symbol):
    quantity_stocks, _ = get_stocks_owned(stock_symbol)
    if latest_price < predicted_price:
        if quantity_stocks == 0:
            return 'buy'
    else:
        if quantity_stocks > 0:
            return 'sell'

def get_stocks_owned(stock_symbol):
    query = f'from(bucket:"{INFLUXDB_BUCKET}")\
        |> range(start:-1h)\
        |> filter(fn:(r) => r._measurement == "{stock_symbol}")'
    quantity, price = 0, 0
    tables = db_query_api.query(org=INFLUXDB_ORG, query=query)
    if len(tables) > 0 and len(tables[0].records > 0):
        quantity, price = tables[0].records[-1]["quantity"], tables[0].records[-1]["price"]

    return quantity, price

def on_message(client, userdata, msg):
    print(msg.topic+" "+msg.payload.decode())
    payload_dict = json.loads(msg.payload.decode())
    stock_symbol = payload_dict['stock_symbol']
    predicted_price = payload_dict['predicted_price']
    latest_price = payload_dict['current_price']
    action = decide_action(predicted_price, latest_price, stock_symbol)
    if action is not None:
        client.publish(MQTT_TOPIC_EXECUTOR, f"{action} {stock_symbol}")

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_HOST, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
mqtt_client.loop_forever()
