import json
import configparser
from math import ceil
import paho.mqtt.client as mqtt
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

config = configparser.ConfigParser()
config.read('config.ini')

INFLUXDB_URL = config['influxdb']['URL'] or "http://localhost:8086"
INFLUXDB_TOKEN = config['influxdb']['TOKEN'] or "se4as_token"
INFLUXDB_ORG = config['influxdb']['ORG'] or "se4as"
INFLUXDB_BUCKET_PORTFOLIO = config['influxdb']['PORTFOLIO_BUCKET_NAME'] or "portfolio"
INFLUXDB_BUCKET_TRANSACTIONS = config['influxdb']['TRANSACTION_BUCKET_NAME'] or "transactions"

db_client = influxdb_client.InfluxDBClient(
    url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG
)

db_query_api = db_client.query_api()
db_write_api = db_client.write_api(write_options=SYNCHRONOUS)

MQTT_HOST = config['mqtt']['broker'] or "localhost"
MQTT_PORT = int(config['mqtt']['port']) or 1883
MQTT_TOPIC_ACTION = "executor/action"
MQTT_TOPIC_MONITOR = "monitor/completed"

INVESTMENT_INITIAL_VALUE = 1000

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT with result code "+str(rc))

    # NOTE: Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC_ACTION)

def parse_message(payload):
    match payload.split():
        case [("buy" | "sell") as action, stock_symbol, price]:
            price_numeric = float(price)
            return (action, stock_symbol, price_numeric)
        case _:
            raise ValueError(f"Invalid message received: {payload}")

def check_create_bucket(bucket_name):
    bucket_api = db_client.buckets_api()
    bucket_response = bucket_api.find_bucket_by_name(bucket_name)
    if not bucket_response:
        bucket_api.create_bucket(bucket_name=bucket_name, org=INFLUXDB_ORG)

def buy_stock(stock_symbol, price):
    print("Buying", stock_symbol, "stock at price", price)
    investment = get_investment()
    if price >= 100.0:
        quantity = 1
    else:
        quantity = ceil(100.0 / price)
    investment -= (quantity*price)
    update_investment(investment)
    update_stocks_owned(stock_symbol, quantity, price)

def sell_stock(stock_symbol, price):
    print("Selling", stock_symbol, "stock at price", price)
    investment = get_investment()
    quantity, buying_price = get_stocks_owned(stock_symbol)
    investment += (quantity * price)
    update_investment(investment)
    update_stocks_owned(stock_symbol, 0, 0.0)

    return quantity*(price-buying_price)

def get_investment():
    value = INVESTMENT_INITIAL_VALUE
    query = f'from(bucket:"{INFLUXDB_BUCKET_PORTFOLIO}")\
        |> range(start:-1h)\
        |> filter(fn:(r) => r._measurement == "investment")\
        |> filter(fn:(r) => r._field == "value")'
    result = db_query_api.query(org=INFLUXDB_ORG, query=query)
    if len(result) > 0 and len(result[0].records) > 0:
        value = result[0].records[-1].get_value()

    return value

def update_investment(value):
    point = {
        "measurement": "investment",
        "fields": {"value": value}
    }
    db_write_api.write(bucket=INFLUXDB_BUCKET_PORTFOLIO, record=point)

def get_stocks_owned(stock_symbol):
    query = f'from(bucket:"{INFLUXDB_BUCKET_PORTFOLIO}")\
        |> range(start:-1h)\
        |> filter(fn:(r) => r._measurement == "{stock_symbol}")'
    value, price = 0, 0
    tables = db_query_api.query(org=INFLUXDB_ORG, query=query)
    if len(tables) > 0 and len(tables[0].records) > 0:
        last_record = tables[0].records[-1]
        value, price = int(last_record["quantity"]), last_record.get_value()
    
    return value, price

def update_stocks_owned(stock_symbol, quantity, price):
    point = {
        "measurement": stock_symbol,
        "tags": {
            "quantity": quantity
        },
        "fields": {
            "price": price
        }
    }
    db_write_api.write(bucket=INFLUXDB_BUCKET_PORTFOLIO, record=point)

def log_transaction(action, stock_symbol, price, predicted_price, profit=0.0):
    check_create_bucket(INFLUXDB_BUCKET_TRANSACTIONS)

    point = {
        "measurement": stock_symbol,
        "tags": {
            "action": action,
            "price": price,
            "predicted_price": predicted_price
        },
        "fields": {
            "profit": profit
        }
    }
    db_write_api.write(bucket=INFLUXDB_BUCKET_TRANSACTIONS, record=point)

def on_message(client, userdata, msg):
    try:
        payload_dict = json.loads(msg.payload.decode())
        action = payload_dict["action"]
        stock = payload_dict["stock"]
        price = payload_dict["price"]
        predicted_price = payload_dict["predicted_price"]
    except Exception as e:
        print("error decoding received message:", e)
        return

    check_create_bucket(INFLUXDB_BUCKET_PORTFOLIO)
    if action == "buy":
        buy_stock(stock, price)
        profit = 0.0
    else:
        profit = sell_stock(stock, price)
    # stock symbol, action, price, profit, predicted price
    # if we already have a stock, don't buy it again
    log_transaction(action, stock, price, predicted_price, profit)
    client.publish(f"{MQTT_TOPIC_MONITOR}", stock)

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)

mqtt_client.loop_forever()