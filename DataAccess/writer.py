import random
import time
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

bucket = "stocks"
org = "se4as"
token = "se4as_token"
url="http://localhost:8086"
time_sleep = 1

client = influxdb_client.InfluxDBClient(
   url=url,
   token=token,
   org=org
)

write_api = client.write_api(write_options=SYNCHRONOUS)

i = 1
while i <= 30:
    current_price = round(random.uniform(170.0, 200.0), 2)
    stock_point = influxdb_client.Point("stock_price").tag("stock", "aapl").field("current_price", current_price)
    write_api.write(bucket=bucket, org=org, record=stock_point)
    print("Writing price to influxdb: ", current_price)
    time.sleep(time_sleep)
    i = i + 1

