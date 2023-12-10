from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import paho.mqtt.client as mqtt
from portfolio import Stock, Portfolio

app = FastAPI()
portfolio = Portfolio()

@app.post("/add-stock")
def buy_stock(stock: Stock):
    portfolio.buy_stock(stock.symbol, stock.name)
    return {"message": f"Started tracking {stock.symbol}."}

@app.post("/remove-stock")
def sell_stock(stock: Stock):
    portfolio.sell_stock(stock.symbol, stock.name)
    return {"message": f"Stopped tracking {stock.shares}."}

def main():
    # MQTT Configuration
    mqtt_broker_address = "localhost"
    mqtt_broker_port = 1883
    mqtt_topic = "portfolio"

    # MQTT Client Setup
    mqtt_client = mqtt.Client(client_id="managed_resources")
    mqtt_client.connect(mqtt_broker_address, mqtt_broker_port)
    mqtt_client.publish(mqtt_topic, "hello")
    mqtt_client.loop_start()

if __name__ == "__main__":
    main()