import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime

bucket = "stocks"
org = "se4as"
token = "se4as_token"
url="http://localhost:8086"

client = influxdb_client.InfluxDBClient(
   url=url,
   token=token,
   org=org
)

query_api = client.query_api()

query = 'from(bucket:"stocks")\
|> range(start: -30m)\
|> filter(fn:(r) => r._measurement == "stock_price")\
|> filter(fn:(r) => r.stock == "aapl")\
|> filter(fn:(r) => r._field == "current_price")'

result = query_api.query(org=org, query=query)

results = []
for table in result:
  for record in table.records:
    date_time = record.get_time().strftime("%d/%m/%Y-%H:%M:%S")
    results.append((date_time, record.get_value(), record.get_field()))

print(results)