import json
from math import ceil
import paho.mqtt.client as mqtt
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "se4as_token"
INFLUXDB_ORG = "se4as"
INFLUXDB_BUCKET_PORTFOLIO = "portfolio"
INFLUXDB_BUCKET_TRANSACTIONS = "transactions"

db_client = influxdb_client.InfluxDBClient(
    url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG
)

db_query_api = db_client.query_api()
db_write_api = db_client.write_api(write_options=SYNCHRONOUS)

MQTT_HOST = "localhost"
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

    log_transaction("buy", stock_symbol, price)

def sell_stock(stock_symbol, price):
    print("Selling", stock_symbol, "stock at price", price)
    investment = get_investment()
    quantity, buying_price = get_stocks_owned(stock_symbol)
    investment += (quantity * price)
    update_investment(investment)
    update_stocks_owned(stock_symbol, 0, 0)
    log_transaction("sell", stock_symbol, price, profit=quantity*(price-buying_price))

def get_investment():
    query = f'from(bucket:"{INFLUXDB_BUCKET_PORTFOLIO}")\
        |> range(start:-1h)\
        |> filter(fn:(r) => r._measurement == "investment")\
        |> filter(fn:(r) => r._field == "value")'
    value = INVESTMENT_INITIAL_VALUE
    result = db_query_api.query(org=INFLUXDB_ORG, query=query)
    if len(result) > 0 and len(result[0].records > 0):
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
    if len(tables) > 0 and len(tables[0].records > 0):
        value, price = tables[0].records[-1]["quantity"], tables[0].records[-1]["price"]
    
    return value, price

def update_stocks_owned(stock_symbol, quantity, price):
    point = {
        "measurement": stock_symbol,
        "fields": {
            "quantity": quantity,
            "price": price
        }
    }
    db_write_api.write(bucket=INFLUXDB_BUCKET_PORTFOLIO, record=point)

def log_transaction(action, stock_symbol, price, profit=None):
    fields = {
        "action": action,
        "price": price # TODO add predicted price
    }
    if profit is not None:
        fields["profit"] = profit

    point = {
        "measurement": stock_symbol,
        "fields": fields
    }
    db_write_api.write(bucket=INFLUXDB_BUCKET_TRANSACTIONS, record=point)

def on_message(client, userdata, msg):
    try:
        payload_dict = json.loads(msg.payload.decode())
        action = payload_dict["action"]
        stock = payload_dict["stock"]
        price = payload_dict["price"]
    except Exception as e:
        print("error decoding received message:", e)
        return

    if action == "buy":
        buy_stock(stock, price)
    else:
        sell_stock(stock, price)
    # stock symbol, action, price, profit, predicted price
    # if we already have a stock, don't buy it again

    client.publish(f"{MQTT_TOPIC_MONITOR}", stock)

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_HOST, 1883, 60)

mqtt_client.loop_forever()