from fastapi import FastAPI, HTTPException
from fastapi_mqtt import FastMQTT, MQTTConfig
import json
from portfolio import Portfolio
from starlette.middleware.cors import CORSMiddleware


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
stock_added_topic = "monitor/stock-added"
stock_list_topic = "monitor/stock-list"

# MQTT Client Setup
mqtt_config = MQTTConfig(host="173.30.0.100", port=1883)

fast_mqtt = FastMQTT(
    config=mqtt_config,
    client_id="managed_resources"
)
fast_mqtt.init_app(app)


@app.get("/stock-list")
def get_stock_list():
    return json.loads(portfolio.get_stock_list())


@app.post("/add-stock")
def add_stock(stock: str):
    is_added = portfolio.add_stock(stock)
    if not is_added:
        raise HTTPException(status_code=404, detail="Item not found")
    fast_mqtt.publish(stock_added_topic, stock)
    return {"message": f"Started tracking stock: {stock}"}


@app.post("/remove-stock")
def remove_stock(stock: str):
    is_removed = portfolio.remove_stock(stock)
    if not is_removed:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": f"Stopped tracking stock: {stock}"}
