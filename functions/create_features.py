import pandas as pd
from numpy import where

def clean_dataset(dataset:object):
    # Naming columns
    dataset.columns = ['open_time', 'open_price', 'high_price', 'low_price', 'close_price', 'volume',
                    'close_time', 'quote_asset_volume', 'trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']

    # Changing columns order
    dataset = dataset[['close_price', 'high_price', 'low_price', 'open_price', 'taker_buy_base_asset_volume', 'open_time', 'volume', 'close_time', 'trades']]

    dataset['open_time'] = pd.to_datetime(dataset['open_time'], unit='ms')
    dataset.set_index('open_time', inplace=True, drop=False)

    # Some corrections
    dataset['taker_buy_base_asset_volume'] = dataset['taker_buy_base_asset_volume'] / dataset['volume']

    # Set bullish or bearish
    dataset['Bull'] = where(dataset['high_price'] > dataset['high_price'].shift(1), 1, 0).astype('int64')

    # Calculate OBV indicator
    dataset['OBV'] = where(dataset['close_price'] > dataset['close_price'].shift(1), dataset['volume'], -dataset['volume'])

    # Calculate the candle change  and candle volatility
    dataset['Volatility'] = (dataset['high_price'] - dataset['low_price']) / dataset['open_price'] * 100
    dataset['Change'] = (dataset['close_price'] - dataset['open_price']) / dataset['open_price'] * 100

    # Calculate Stochastic
    # Calculate the 21-day rolling window for the low and high prices
    dataset['21-day low'] = dataset['low_price'].rolling(window=21).min()
    dataset['21-day high'] = dataset['high_price'].rolling(window=21).max()

    # Calculate the stochastic oscillator
    dataset['Stochastic'] = 100 * ((dataset['close_price'] - dataset['21-day low']) / (dataset['21-day high'] - dataset['21-day low']))

    # Calculate the last deep for each stock
    dataset['last_deep'] = dataset.rolling(window=10)['low_price'].min().shift(1)

    # Calculate the last top for each stock
    dataset['last_top'] = dataset.rolling(window=10)['high_price'].max().shift(1)

    # Calculate MACD
    # Calculate the 12-period and 26-period EMAs
    dataset['MACD'] = dataset['close_price'].ewm(span=12).mean() - dataset['close_price'].ewm(span=26).mean()

    # Calculate the MACD histogram
    dataset['Hist'] = dataset['MACD'] - dataset['MACD'].ewm(span=9).mean()

    ma100 = dataset['close_price'].rolling(100).mean()[-1]

    # Removing unused columns
    dataset.drop(['open_time', 'close_time', '21-day low', '21-day high', 'MACD'], axis=1, inplace=True)

    # Removing NaN data
    dataset.dropna(inplace=True)

    # Saving on memory
    return dataset, ma100
