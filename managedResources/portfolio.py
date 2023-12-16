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
