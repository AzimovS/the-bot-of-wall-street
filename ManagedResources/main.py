from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import paho.mqtt.client as mqtt
from portfolio import Portfolio
import json

app = FastAPI()
portfolio = Portfolio()
# MQTT Configuration
mqtt_broker_address = "localhost"
mqtt_broker_port = 1883
stock_added_topic = "monitor/stock-added"
stock_list_topic = "monitor/stock-list"

@app.post("/add-stock")
def buy_stock(stock: str):
    portfolio.buy_stock(stock.symbol)
    return {"message": f"Started tracking {stock.symbol}."}

@app.post("/remove-stock")
def sell_stock(stock: str):
    portfolio.sell_stock(stock.symbol)
    return {"message": f"Stopped tracking {stock.shares}."}


def add_stock(mqtt_client, stock, portfolio):
    portfolio.add_stock(stock)
    mqtt_client.publish(stock_added_topic, stock)
    

def main():
    # MQTT Client Setup
    mqtt_client = mqtt.Client(client_id="managed_resources")
    mqtt_client.connect(mqtt_broker_address, mqtt_broker_port)

    add_stock(mqtt_client, "AAPL", portfolio)
    json_stocks = json.dumps(list(portfolio.stocks))
    mqtt_client.publish(stock_list_topic, json_stocks)    

if __name__ == "__main__":
    main()