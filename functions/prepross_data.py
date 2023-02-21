from sklearn.preprocessing import StandardScaler
import joblib
import pandas as pd
import numpy as np

# Local imports
from functions.create_features import CreateFeatures
from functions.neural_network import NeuralNetwork


class PreProssData():
    def __init__(self, timeframe:int=15, candles:int=20) -> None:
        self.scaler = self.get_scaler()
        self.candles = candles
        self.timeframe = timeframe

        """self.__high_above = NeuralNetwork()
        self.__high_above.pre_load_model(model_name='next_high', timeframe=timeframe, candles=candles, start='AA')

        self.__low_above = NeuralNetwork()
        self.__low_above.pre_load_model(model_name='next_low', timeframe=timeframe, candles=candles, start='AA')"""

        self.__change_above = NeuralNetwork()
        self.__change_above.pre_load_model(model_name='next_change', timeframe=timeframe, candles=candles, start='AA')

        """self.__low_below = NeuralNetwork()
        self.__low_below.pre_load_model(model_name='next_low', timeframe=timeframe, candles=candles, start='BA')"""

        self.__change_below = NeuralNetwork()
        self.__change_below.pre_load_model(model_name='next_change', timeframe=timeframe, candles=candles, start='BA')


    def get_scaler(self):
        scaler = joblib.load('resources/scaler/scaler.save')
        return scaler

    
    def get_scaled_data(self, previous:bool=False, return_data:bool=True):
        df = pd.read_csv('resources/dataset/daily_15min.csv')
        df.columns = ['open_time', 'open_price', 'high_price', 'low_price', 'close_price', 'volume',
                      'close_time', 'quote_asset_volume', 'trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
        
        data = CreateFeatures(dataset=df, timeframe=self.timeframe, keep_time=False)
        df = data.get_dataframe()

        adjust = -1 if previous else 0

        scaled_data = self.scaler.transform(df[-self.candles-3+adjust:-3+adjust])
        scaled_data = scaled_data.reshape(-1, self.candles, scaled_data.shape[1])

        if return_data:
            return scaled_data, df
        else:
            return scaled_data


    def predict_all_values(self):
        scaled_data, df = self.get_scaled_data()
        scaled_data, df = self.get_scaled_data()
        change1 = df['open_price'][-2] * self.__change_above.neural_predict(X_input=scaled_data)[0][0] / 50 + df['open_price'][-2]
        change2 = df['open_price'][-2] * self.__change_below.neural_predict(X_input=scaled_data)[0][0] / 50 + df['open_price'][-2]

        """high = self.__high_above.neural_predict(X_input=scaled_data)[0][0]

        low1 = self.__low_above.neural_predict(X_input=scaled_data)[0][0]
        low2 = self.__low_below.neural_predict(X_input=scaled_data)[0][0]

        low_mean = ((low1 + low2) / 2 + high) / 2

        scaled_data = self.get_scaled_data(previous=True, return_data=False)
        high_previous = self.__high_above.neural_predict(X_input=scaled_data)[0][0]
        low1_previous = self.__low_above.neural_predict(X_input=scaled_data)[0][0]
        low2_previous = self.__low_below.neural_predict(X_input=scaled_data)[0][0]

        low_mean_previous = ((low1_previous + low2_previous) / 2 + high_previous) / 2"""
        
        return change1, change2, df[-30:]
        

