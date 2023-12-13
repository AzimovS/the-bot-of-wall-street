from fastapi import FastAPI, HTTPException
import paho.mqtt.client as mqtt
import json
from portfolio import Portfolio
from starlette.middleware.cors import CORSMiddleware


app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

portfolio = Portfolio()
# MQTT Configuration
mqtt_broker_address = "173.30.0.100"
mqtt_broker_port = 1883
stock_added_topic = "monitor/stock-added"
stock_list_topic = "monitor/stock-list"

# MQTT Client Setup
mqtt_client = mqtt.Client(client_id="managed_resources")
mqtt_client.connect(mqtt_broker_address, mqtt_broker_port)

@app.get("/stock-list")
def get_stock_list():
    return json.loads(portfolio.get_stock_list())


@app.post("/add-stock")
def add_stock(stock: str):
    is_added = portfolio.add_stock(stock)
    if not is_added:
        raise HTTPException(status_code=404, detail="Item not found")
    mqtt_client.publish(stock_added_topic, stock)
    return {"message": f"Started tracking stock: {stock}"}


@app.post("/remove-stock")
def remove_stock(stock: str):
    is_removed = portfolio.remove_stock(stock)
    if not is_removed:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": f"Stopped tracking stock: {stock}"}
