from fastapi import FastAPI
import paho.mqtt.client as mqtt
import json
from portfolio import Portfolio
import pandas as pd
from starlette.middleware.cors import CORSMiddleware


app = FastAPI()
origins = ['http://localhost:5000', 'http://localhost:5001']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

portfolio = Portfolio()
# MQTT Configuration
mqtt_broker_address = "localhost"
mqtt_broker_port = 1883
stock_added_topic = "monitor/stock-added"
stock_list_topic = "monitor/stock-list"


def add_stock1(mqtt_client, stock, portfolio):
    portfolio.add_stock(stock)
    mqtt_client.publish(stock_added_topic, stock)


# MQTT Client Setup
mqtt_client = mqtt.Client(client_id="managed_resources")
mqtt_client.connect(mqtt_broker_address, mqtt_broker_port)
add_stock1(mqtt_client, "AAPL", portfolio)
json_stocks = json.dumps(list(portfolio.stocks))
mqtt_client.publish(stock_list_topic, json_stocks)

stock_meta = pd.read_csv(f'stocks_meta.csv', header=0, usecols=[
                         "symbol", "securityName", "listingExchange", "marketCategory"])
stock_meta['tracking'] = False


@app.get("/stock-list")
def get_stock_list():
    result = stock_meta.to_json(orient="records")
    parsed = json.loads(result)
    return parsed


@app.post("/add-stock")
def add_stock(stock: str):
    # TODO: add validation
    portfolio.add_stock(stock)
    # mqtt_client.publish(stock_added_topic, stock_symbol)
    stock_meta.loc[stock_meta["symbol"] == stock, "tracking"] = True
    return {"message": f"Started tracking stock: {stock}"}


@app.post("/remove-stock")
def remove_stock(stock: str):
    # TODO: add validation
    portfolio.remove_stock(stock)
    stock_meta.loc[stock_meta["symbol"] == stock, "tracking"] = False
    return {"message": f"Stopped tracking stock: {stock}."}
