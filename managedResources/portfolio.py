import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd
import configparser
from datetime import datetime

config = configparser.ConfigParser()
config.read('config.ini')

URL = config['influxdb']['URL']
TOKEN = config['influxdb']['TOKEN']
ORG = config['influxdb']['ORG']
TRACKING_BUCKET_NAME = config['influxdb']['TRACKING_BUCKET_NAME']
CSV_COLS = config['influxdb']['CSV_COLS'].split('|')
STARTTIME = config['influxdb']['STARTTIME']
INFLUXDB_BUCKET_PORTFOLIO = "portfolio"
INFLUXDB_BUCKET_TRANSACTIONS = "transactions"


class Portfolio:
    def __init__(self):
        self.db_client = influxdb_client.InfluxDBClient(
            url=URL,
            token=TOKEN,
            org=ORG
        )
        self.create_fill_bucket()

    def create_fill_bucket(self):
        bucket_api = self.db_client.buckets_api()
        bucket_response = bucket_api.find_bucket_by_name(TRACKING_BUCKET_NAME)
        if not bucket_response:
            stock_meta = pd.read_csv(
                f'stocks_meta.csv', header=0, usecols=CSV_COLS)
            bucket_api.create_bucket(bucket_name=TRACKING_BUCKET_NAME, org=ORG)
            write_api = self.db_client.write_api(write_options=SYNCHRONOUS)
            for _, row in stock_meta.iterrows():
                data_point = {
                    "measurement": row["symbol"],
                    "tags": {col: row[col] for col in stock_meta.columns},
                    "fields": {"tracking": False}
                }
                write_api.write(bucket=TRACKING_BUCKET_NAME,
                                org=ORG, record=data_point)

    def get_stock_list(self):
        query = f'from(bucket:"tracking_stocks")\
        |> range(start: {STARTTIME})'
        result = self.db_client.query_api().query(org="se4as", query=query)
        return result.to_json()

    def update_db(self, stock: str, new_tracking: bool) -> bool:
        query = f'from(bucket:"tracking_stocks")\
        |> range(start: {STARTTIME})\
        |> filter(fn:(r) => r._measurement == "{stock}")'
        result = self.db_client.query_api().query(org="se4as", query=query)
        if not result:
            return False
        dct = result[0].records[0].values
        data_point = {
            "measurement": dct["symbol"],
            "tags": {col: dct[col] for col in CSV_COLS},
            "time": dct["_time"],
            "fields": {"tracking": new_tracking}
        }
        stop = datetime.now()
        delete_api = self.db_client.delete_api()
        delete_api.delete(
            STARTTIME, stop, f'_measurement="{stock}"', bucket=TRACKING_BUCKET_NAME, org=ORG)

        write_api = self.db_client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket=TRACKING_BUCKET_NAME,
                        org=ORG, record=data_point)
        return True

    def add_stock(self, stock: str) -> bool:
        is_updated = self.update_db(stock, True)
        return is_updated

    def remove_stock(self, stock: str) -> bool:
        is_updated = self.update_db(stock, False)
        return is_updated

    def get_portfolio(self):
        q = f'import "influxdata/influxdb/schema"\n\nschema.measurements(bucket: "{INFLUXDB_BUCKET_PORTFOLIO}")'
        result = self.db_client.query_api().query(org=ORG, query=q)
        check_stocks = [record['_value']
                        for record in result[0].records if record['_value'] != 'investment']

        portfolio = []
        for check_stock in check_stocks:
            query = f'from(bucket: "{INFLUXDB_BUCKET_PORTFOLIO}")\
                        |> range(start: {STARTTIME})\
                        |> filter(fn: (r) => r["_measurement"] == "{check_stock}")\
                        |> group()\
                        |> sort(columns: ["_time"], desc: false)\
                        |> last()'
            value, price = 0, 0
            tables = self.db_client.query_api().query(org=ORG, query=query)
            if len(tables) > 0 and len(tables[0].records) > 0:
                last_record = tables[0].records[-1]
                value, price = int(
                    last_record["quantity"]), last_record.get_value()
                if value > 0:
                    stock_entry = {"symbol": check_stock,
                                   "shares": value, "price": price}
                    portfolio.append(stock_entry)
        return portfolio

    def get_transactions(self):
        query = f'from(bucket:"{INFLUXDB_BUCKET_TRANSACTIONS}")\
            |> range(start: {STARTTIME})\
            |> group()\
            |> sort(columns: ["_time"], desc: true)'
        result = self.db_client.query_api().query(org="se4as", query=query)
        return result.to_json()
