import json
import configparser
import paho.mqtt.client as mqtt
import influxdb_client

config = configparser.ConfigParser()
config.read('config.ini')

# using the or operator is considered an antipattern (b/c it works with any 'falsy' values)
# but I think it can be used here for conciseness
INFLUXDB_URL = config['influxdb']['URL'] or "http://localhost:8086"
INFLUXDB_TOKEN = config['influxdb']['TOKEN'] or "se4as_token"
INFLUXDB_ORG = config['influxdb']['ORG'] or "se4as"
INFLUXDB_BUCKET = config['influxdb']['BUCKET_NAME'] or "portfolio"

db_client = influxdb_client.InfluxDBClient(
    url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG
)

db_query_api = db_client.query_api()

MQTT_HOST = config['mqtt']['broker'] or "localhost"
MQTT_PORT = int(config['mqtt']['port']) or 1883
MQTT_TOPIC_ANALYZER = "planner/prediction/stock"
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
    return 'continue'


def get_stocks_owned(stock_symbol):
    quantity, price = 0, 0
    if bucket_exists():
        query = f'from(bucket: "{INFLUXDB_BUCKET}")\
                        |> range(start: -12h)\
                        |> filter(fn: (r) => r["_measurement"] == "{stock_symbol}")\
                        |> group()\
                        |> sort(columns: ["_time"], desc: false)\
                        |> last()'
        tables = db_query_api.query(org=INFLUXDB_ORG, query=query)
        if len(tables) > 0 and len(tables[0].records) > 0:
            last_record = tables[-1].records[-1]
            quantity, price = int(
                last_record['quantity']), last_record['_value']
    return quantity, price


def bucket_exists():
    bucket_api = db_client.buckets_api()
    return bucket_api.find_bucket_by_name(INFLUXDB_BUCKET)


def on_message(client, userdata, msg):
    print(msg.topic+" "+msg.payload.decode())
    try:
        payload_dict = json.loads(msg.payload.decode())
    except Exception as e:
        print("error decoding received message:", e)
        return

    stock_symbol = payload_dict['stock_symbol']
    predicted_price = payload_dict['predicted_price']
    latest_price = payload_dict['current_price']
    action = decide_action(predicted_price, latest_price, stock_symbol)

    executor_payload = {
        "action": action,
        "stock": stock_symbol,
        "price": latest_price,
        "predicted_price": predicted_price
    }
    client.publish(MQTT_TOPIC_EXECUTOR, json.dumps(
        executor_payload, indent=None))


mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
mqtt_client.loop_forever()
