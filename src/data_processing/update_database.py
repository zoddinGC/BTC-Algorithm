"""
    This module is responsible to update the dataset 'actual_15minutes.csv' with
    the last 101 candles (last 25.3 hours).
"""

from csv import writer
from datetime import datetime
from time import sleep
from os import getenv
from dotenv import load_dotenv
from binance.client import Client


def update_database(first_load_data:bool=False):
    """
        first_load_data -> if True, it will load the data regardless
            if the time is % 15 minutes and break the update loop
    """

    print('Collecting Data...')
    while True:
        candles = client.get_historical_klines(symbol='BTCUSDT', interval=interval, limit=101)
        last_minute = datetime.fromtimestamp(int(candles[-1][0])/1000).minute

        if last_minute == datetime.now().minute or first_load_data:
            break

        print(f'Time different! {last_minute}, {datetime.now().minute}')
        sleep(0.05)

    print('Writting...')

    with open('src/resources/dataset/live_data_15min.csv', 'w', encoding='utf-8', newline='') as file:
        save_csv = writer(file, delimiter=',')
        for candlestick in candles:
            save_csv.writerow(candlestick)

    print('Finished. Size:', len(candles))


# Creating objects
load_dotenv()
API_KEY = getenv('API_KEY')
API_SECRET = getenv('API_SECRET')

client = Client(API_KEY, API_SECRET)
interval = Client.KLINE_INTERVAL_15MINUTE

if __name__ == '__main__':
    update_database()
