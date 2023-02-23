import csv
from binance.client import Client
import config


def download_data(start_str:str='2023-01-30', end_str:str='2023-01-31') -> None:
    # config.API_KEY is your Binance Key from your API (create one if you don't have it)
    # config.API_SECRET is your Binance Secret Key from your API (create one if you don't have it)
    client = Client(config.API_KEY, config.API_SECRET)
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
    with open('BTC/data/raw/new_BTC_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(candles)


if __name__ == '__main__':
    download_data()