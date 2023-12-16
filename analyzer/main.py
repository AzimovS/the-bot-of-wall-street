import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime as dt
from river import time_series
import pickle
from os.path import exists
import paho.mqtt.client as mqtt
import json

# mqtt
broker = 'localhost'
port = 1883
analyze_stock_topic = "analyzer/predict/stock"
plan_stock_topic = "planner/prediction/stock"
# influxdb
bucket = "stocks"
org = "se4as"
token = "se4as_token"
url="http://localhost:8086"

client = influxdb_client.InfluxDBClient(
   url=url,
   token=token,
   org=org
)

def on_connect(mqtt_client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    mqtt_client.subscribe(analyze_stock_topic)

def on_message(mqtt_client, userdata, message):
    if message.topic == analyze_stock_topic:
        stock_symbol = message.payload.decode()
        print("new stock", stock_symbol)
        try:
           result = query_influxdb(bucket, stock_symbol, "Open")
           parsed_results, last_day, last_price = parse_db_results(result)
           predicted_price = call_model(stock_symbol, parsed_results, last_day, last_price)
        except:
           print("An error has occurred while querying the database. Please check stock symbol is a valid measurement")
        payload = {'stock_symbol': stock_symbol, 'current_price': last_price, 'predicted_price': predicted_price}
        mqtt_client.publish(plan_stock_topic, json.dumps(payload))

def query_influxdb(bucket, measurement, field):
   query = f'from(bucket:"{bucket}")\
|> range(start: 1900-01-01T00:00:00Z)\
|> filter(fn:(r) => r._measurement == "{measurement}")\
|> filter(fn:(r) => r._field == "{field}")'
   query_api = client.query_api()
   result = query_api.query(org=org, query=query)
   return result

def parse_db_results(result):
   parsed_results = []
   for table in result:
    for record in table.records:
       parsed_results.append((record.get_time(), record.get_value()))
   last_day = parsed_results[-1][0]
   last_price = parsed_results[-1][1]
   return parsed_results, last_day, last_price

def model_exists(stock_symbol):
   file_exists = exists(f"models/{stock_symbol}.pkl")  
   return file_exists

def train_model(results):
   print("training model")
   model = time_series.SNARIMAX(
      p=10,
      d=1,
      q=0
      )
   
   for (_, y) in results:
      model.learn_one(y)

   return model

def save_model(stock_symbol, model):
   with open(f'models/{stock_symbol}.pkl', 'wb') as f:
      pickle.dump(model, f)

def retrieve_model(stock_symbol):
   print("retreiving model")
   with open(f'models/{stock_symbol}.pkl', 'rb') as f:
      model = pickle.load(f)
   return model

def update_model(stock_symbol, model, new_entry):
   model.learn_one(new_entry)
   save_model(stock_symbol, model)

def predict_stock_price(model, last_day):
   horizon = 1
   next_day = last_day + dt.timedelta(days=1)
   future = [{'next_day': dt.date(year=next_day.year, month=next_day.month, day=next_day.day)}]
   forecast = model.forecast(horizon=horizon)
   predicted_price = 0
   for x, y_pred in zip(future, forecast):
      print(x["next_day"], f'{y_pred:.3f}')
      predicted_price = y_pred
   return predicted_price

def call_model(stock_symbol, parsed_results, last_day, last_price):
   if(model_exists(stock_symbol)):
      model = retrieve_model(stock_symbol)
      update_model(stock_symbol, model, last_price)
      predicted_price = predict_stock_price(model, last_day)
   else:
      model = train_model(parsed_results)
      predicted_price = predict_stock_price(model, last_day)
      save_model(stock_symbol, model)
   return predicted_price

def main():
   mqtt_client = mqtt.Client(client_id="analyzer")
   print(broker, port)
   mqtt_client.connect(broker, port)
   mqtt_client.on_connect = on_connect
   mqtt_client.on_message = on_message
   mqtt_client.loop_forever()


if __name__ == '__main__':
    main()