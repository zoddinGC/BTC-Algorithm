from joblib import load
import pandas as pd

# Local imports
from data_processing.create_features import clean_dataset
from features.neural_network import NeuralNetwork


class PreProssData():
    def __init__(self, candles:int=20) -> None:
        self.scaler = self.get_scaler()
        self.candles = candles

        self.__change_above = NeuralNetwork()
        self.__change_above.pre_load_model(start='AA')

        self.__change_below = NeuralNetwork()
        self.__change_below.pre_load_model(start='BA')


    def get_scaler(self):
        # Joblib
        scaler = load('src/resources/scaler/scaler.save')
        return scaler

    
    def get_scaled_data(self):
        dataset = pd.read_csv('src/resources/dataset/live_data_15min.csv')        
        df, ma100 = clean_dataset(dataset=dataset)

        scaled_data = self.scaler.transform(df[-self.candles-3:-3])
        scaled_data = scaled_data.reshape(-1, self.candles, scaled_data.shape[1])

        return scaled_data, df, ma100


    def predict_all_values(self):
        scaled_data, df, ma100 = self.get_scaled_data()
        change1 = df['open_price'][-2] * self.__change_above.neural_predict(X_input=scaled_data)[0][0] / 50 + df['open_price'][-2]
        change2 = df['open_price'][-2] * self.__change_below.neural_predict(X_input=scaled_data)[0][0] / 50 + df['open_price'][-2]
        
        return change1, change2, ma100
        

