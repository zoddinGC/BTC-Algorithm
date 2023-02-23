# Import libraries
from binance.client import Client
import functions.config as config
from csv import writer
from datetime import datetime
from time import sleep

# Creating objects
client = Client(config.API_KEY, config.API_SECRET)
interval = Client.KLINE_INTERVAL_15MINUTE

def update_db(first_load_data:bool=False):
    print('Collecting Data...')
    while True:
        candles = client.get_historical_klines(symbol='BTCUSDT', interval=interval, limit=101)
        last_minute = datetime.fromtimestamp(int(candles[-1][0])/1000).minute

        if last_minute == datetime.now().minute or first_load_data: break

        print(f'Time different! {last_minute}, {datetime.now().minute}')
        sleep(0.05)

    print('Writting...')
    
    csvfile = open(f'resources/dataset/daily_15min.csv', 'w', newline='')
    save_csv = writer(csvfile, delimiter=',')

    for candlestick in candles:
        save_csv.writerow(candlestick)

    csvfile.close()

    print('Finished. Size:', len(candles))
