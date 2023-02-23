import pandas as pd
from numpy import where
from joblib import dump
from sklearn.preprocessing import StandardScaler


class CreateFeatures():
    def __init__(self, keep_time:bool=True, timeframe:int=15, dataset:object or str='Empty') -> None:
        self.keep_time = keep_time
        self.__clean_dataset(timeframe=timeframe, dataset=dataset)


    def __clean_dataset(self, timeframe:int, dataset:object):
        def change_timeframe(data:object, timeframe:int):
            new_df = data.groupby(pd.Grouper(freq=f'{timeframe}min', origin='start', label='right')).agg({'close_price':'last', 'high_price':'max', 'low_price':'min',
                                                                                            'open_price':'first', 'taker_buy_base_asset_volume':'sum',
                                                                                            'open_time':'first', 'volume':'sum', 'close_time':'last', 'trades':'sum'})
            new_df.dropna(inplace=True)        
            return new_df
        
        def remove_columns(data:object):
            return data[['close_price', 'high_price', 'low_price', 'open_price', 'taker_buy_base_asset_volume', 'open_time', 'volume', 'close_time', 'trades']]


        # MA, OBV, Stochastic

        # Loading the data
        if isinstance(dataset, str):
            df = pd.read_csv('resources/dataset/2018-2022_1min.csv')
            more_columns = True
        else:
            df = dataset
            more_columns = False

        # Creating and Converting columns
        df = pd.concat([df[['close_price', 'high_price', 'low_price']], df.drop(['close_price', 'high_price', 'low_price'], axis=1)], axis=1)
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df.set_index('open_time', inplace=True, drop=False)

        # Making * minutes timeframe data
        df = change_timeframe(data=df, timeframe=timeframe) if isinstance(dataset, str) else remove_columns(data=df)

        # Separate Timestamp column in numerics columns by minute, hour and day of week
        if self.keep_time:
            df['minute'] = df['open_time'].dt.strftime('%M').astype('int64')
            df['hour'] = df['open_time'].dt.strftime('%H').astype('int64')
            df['day_of_week'] = df['open_time'].dt.dayofweek.astype('int64')

        # Some corrections
        df['taker_buy_base_asset_volume'] = df['taker_buy_base_asset_volume'] / df['volume']

        # Set bullish or bearish
        df['Bull'] = where(df['high_price'] > df['high_price'].shift(1), 1, 0).astype('int64')

        # Calculate OBV indicator
        df['OBV'] = where(df['close_price'] > df['close_price'].shift(1), df['volume'], -df['volume'])

        # Calculate the candle change  and candle volatility
        df['Volatility'] = (df['high_price'] - df['low_price']) / df['open_price'] * 100
        df['Change'] = (df['close_price'] - df['open_price']) / df['open_price'] * 100

        # Calculate Stochastic
        # Calculate the 21-day rolling window for the low and high prices
        df['21-day low'] = df['low_price'].rolling(window=21).min()
        df['21-day high'] = df['high_price'].rolling(window=21).max()

        # Calculate the stochastic oscillator
        df['Stochastic'] = 100 * ((df['close_price'] - df['21-day low']) / (df['21-day high'] - df['21-day low']))

        # Calculate the last deep for each stock
        df['last_deep'] = df.rolling(window=10)['low_price'].min()
        df['last_deep'] = df['last_deep'].shift(1)

        # Calculate the last top for each stock
        df['last_top'] = df.rolling(window=10)['high_price'].max()
        df['last_top'] = df['last_top'].shift(1)

        # Calculate MACD
        # Calculate the 12-period and 26-period EMAs
        df['Ema12'] = df['close_price'].ewm(span=12).mean()
        df['Ema26'] = df['close_price'].ewm(span=26).mean()

        # Calculate the MACD line
        df['MACD'] = df['Ema12'] - df['Ema26']

        # Calculate the signal line
        df['Signal'] = df['MACD'].ewm(span=9).mean()

        # Calculate the MACD histogram
        df['Hist'] = df['MACD'] - df['Signal']

        # Removing unused columns
        df.drop(['open_time', 'close_time', '21-day low', '21-day high', 'Ema12', 'Ema26', 'MACD', 'Signal'],
                axis=1, inplace=True)

        if more_columns:
            # Creating columns to predict
            df['next_high'] = df['high_price'].shift(-1)
            df['next_low'] = df['low_price'].shift(-1)
            df['next_change'] = df['Change'].shift(-1)
            self.y_columns = ['next_change', 'next_high', 'next_low']

        # Removing NaN data
        df.dropna(inplace=True)

        # Saving on memory
        self.df = df

    
    def __get_X_train_y_train(self, scaler):
        size_split = int(self.df.shape[0]*0.8)

        X_train, y_train = scaler[:size_split], self.df[self.y_columns][:size_split]
        X_test, y_test = scaler[size_split:], self.df[['high_price', 'low_price', 'close_price', 'open_price'] + self.y_columns][size_split:]

        return X_train, X_test, y_train, y_test


    def get_X_scaled(self, split_train_test:bool=True, save:bool=False) -> object:
        useless_columns = ['minute', 'hour', 'day_of_week'] if self.keep_time else []  

        scaler = StandardScaler().fit(self.df.drop(useless_columns + self.y_columns, axis=1))
        if save: dump(scaler, 'resources/scaler/scaler.save')

        scaler = scaler.transform(self.df.drop(useless_columns + self.y_columns, axis=1))

        if split_train_test:
            return self.__get_X_train_y_train(scaler)

        else:
            return scaler


    def get_y_data(self, columns:list or str=[]) -> object:
        return self.df[self.y_columns] if len(columns) == 0 else self.df[columns]
        
    def get_y_columns(self) -> list:
        return self.y_columns

    def get_dataframe(self) -> object:
        return self.df
