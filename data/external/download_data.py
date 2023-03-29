"""
    This module download the Bitcoin data from Binance API
"""

import csv
from os import getenv
from binance.client import Client
from dotenv import load_dotenv


def download_data(
    start_str:str='2023-01-30',
    end_str:str='2023-01-31',
    file_name:str='new_BTC_data'
) -> None:

    """
        start_str -> YYYY-MM-DD string: date to start the download
        end_str   -> YYYY-MM-DD string: date to end the download
        file_name -> string: name of the file to save the downloaded data
    """

    client = Client(API_KEY, API_SECRET)
    interval = Client.KLINE_INTERVAL_1MINUTE

    # Module to download the data
    candles = client.get_historical_klines(
        symbol='BTCUSDT',
        interval=interval,
        start_str=start_str,
        end_str=end_str,
        limit=1_000
    )

    # Columns name of the downloaded data
    columns = [
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume',
        'ignore'
    ]

    # Write/Save the data in a csv file
    with open(f'data/raw/{file_name}.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(candles)


# API_KEY is your Binance Key from your API (create one if you don't have it)
# API_SECRET is your Binance Secret Key from your API (create one if you don't have it)
load_dotenv()
API_KEY = getenv('API_KEY')
API_SECRET = getenv('API_SECRET')

if __name__ == '__main__':
    download_data()
