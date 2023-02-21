# Import libraries
from binance.client import Client
import functions.config as config
import csv
from datetime import datetime
from time import sleep

""" Create a module to write stock prices data and get real time info """

# Creating objects
client = Client(config.API_KEY, config.API_SECRET)

#candles = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1MINUTE)

interval = [Client.KLINE_INTERVAL_15MINUTE, '15min']

def update_db(test:bool=False):

    print('Collecting Data...')
    while True:
        candles = client.get_historical_klines(symbol='BTCUSDT', interval=interval[0], limit=101)
        last_minute = datetime.fromtimestamp(int(candles[-1][0])/1000).minute

        if last_minute == datetime.now().minute or test: break

        print(f'Time different! {last_minute}, {datetime.now().minute}')
        sleep(0.1)

    print('Writting...')
    csvfile = open(f'resources/dataset/daily_{interval[1]}.csv', 'w', newline='')
    save_csv = csv.writer(csvfile, delimiter=',')

    for candlestick in candles:
        save_csv.writerow(candlestick)

    csvfile.close()
    print('Finished. Size:', len(candles))

"""
from binance.spot import Spot
import requests

# defining key/request url
key = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
  
# requesting data from url
data = requests.get(key)  
data = data.json()
print(f"{data['symbol']} price is {data['price']}")
"""
