from fastapi import FastAPI, HTTPException
from fastapi_mqtt import FastMQTT, MQTTConfig
from starlette.middleware.cors import CORSMiddleware
import json
import configparser
from portfolio import Portfolio

config = configparser.ConfigParser()
config.read('config.ini')

app = FastAPI()
portfolio = Portfolio()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MQTT Configuration
stock_added_data = "monitor/stock/added"
stock_removed_data = "monitor/stock/removed"
stock_list_topic = "monitor/completed"

# MQTT Client Setup
mqtt_config = MQTTConfig(
    host=config['mqtt']['broker'], port=config['mqtt']['port'])

fast_mqtt = FastMQTT(
    config=mqtt_config,
    client_id="managed_resources"
)
fast_mqtt.init_app(app)


@app.get("/stock-list")
def get_stock_list():
    return json.loads(portfolio.get_stock_list())


@app.get("/portfolio")
def get_stock_list():
    return portfolio.get_portfolio()


@app.get("/transactions")
def get_stock_list():
    return json.loads(portfolio.get_transactions())


@app.post("/add-stock")
def add_stock(stock: str):
    is_added = portfolio.add_stock(stock)
    if not is_added:
        raise HTTPException(status_code=404, detail="Item not found")
    fast_mqtt.publish(stock_added_data, stock)
    return {"message": f"Started tracking stock: {stock}"}


@app.post("/remove-stock")
def remove_stock(stock: str):
    is_removed = portfolio.remove_stock(stock)
    if not is_removed:
        raise HTTPException(status_code=404, detail="Item not found")
    fast_mqtt.publish(stock_removed_data, stock)
    return {"message": f"Stopped tracking stock: {stock}"}
