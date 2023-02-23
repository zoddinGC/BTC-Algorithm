from datetime import datetime
from keras.layers import LSTM, Dense
from keras.models import Sequential
from keras.models import load_model
import numpy as np
import pandas as pd


class NeuralNetwork():
    def __init__(self) -> None:
        pass

    def __split_for_neural(self, X_input:object, y_features:object, window_size:int):
        # Create a sliding window of * candles
        X = []
        y = []
        for i in range(X_input.shape[0] - window_size):
            X.append(X_input[i:i+window_size])
            y.append(y_features[i+window_size])
        

        # Separate the data - X, y
        X = np.array(X)
        X = X.reshape(-1, window_size, X_input.shape[1])
        y = np.array(y)
        y = y.reshape(-1, 1)
        size_split = int(len(X) * 0.7)

        return X, y, size_split

    def __get_model(self, model_name:str, timeframe:int, candles:int, start:str):
        import os

        lower = -1
        for file in os.listdir('resources/models'):
            if file.split('_')[0] == start:
                if file.split('_')[1:3] == model_name.split('_') and int(file.split('_')[-1][:file.split('_')[-1].find('.')]) == timeframe and int(file.split('_')[3][-2:]) == candles:
                    days = abs(int(file.split('_')[3][:2]) - int(datetime.now().strftime('%d')))
                    if lower == -1 or days < lower:
                        files = []
                        files.append(file)
                        lower = days

        return files[0]

    def neural_network_train(self, X_input:object, y_input:object, candles:int, timeframe:int, save_model:bool=False, split:bool=True) -> int:
        def __initialize_model():
            """
                Try Classification model
                Bullish
                Bearish

                Try Regression Model WITH Classification Model agreement
            """

            # Build the RNN model
            if not self.__initialized:                
                self.model = Sequential()
                self.model.add(LSTM(units=128, input_shape=(X.shape[1], X.shape[2]), return_sequences=True))     
                self.model.add(LSTM(units=64))
                self.model.add(Dense(units=64, activation='relu'))
                self.model.add(Dense(units=32, activation='relu'))
                self.model.add(Dense(units=1))
                self.model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mae'])

            self.__initialized = True

        SEED = 42
        np.random.seed(SEED)

        try: type(self.__initialized)
        except: self.__initialized = False

        column = y_input.columns[0]

        print('Train starting...', datetime.now())

        X, y, size_split = self.__split_for_neural(X_input, y_input[column], window_size=candles)

        size_split = size_split if split else y_input.shape[0]

        __initialize_model()

        self.model.fit(x=X[:size_split], y=y[:size_split], epochs=25, batch_size=64, verbose=0)

        if save_model: self.save_neural_network(models_name=column, candles=candles, timeframe=timeframe)

        print('Train completed...')


    def neural_predict_test(self, model_name:str, X_input:object, y_input:object, timeframe:int, candles:int, start:str, split:bool=False, cut_data:bool=True) -> list:

        self.pre_load_model(model_name=model_name, timeframe=timeframe, candles=candles, start=start)

        X, y, size_split = self.__split_for_neural(X_input, y_input, window_size=candles)

        if not cut_data: size_split = 0

        # Use the trained model to make predictions on the test data
        predictions = self.model.predict(X[size_split:], verbose=0)
        predictions = np.array(predictions).reshape(1, predictions.shape[0])

        if split:
            return list(y[size_split:].T)[0], list(predictions)[0], size_split 
        else:
            return list(y[size_split:].T)[0], list(predictions)[0]

    
    def pre_load_model(self, model_name:str, timeframe:int, candles:int, start:str):
        file = self.__get_model(model_name=model_name, timeframe=timeframe, candles=candles, start=start)
        path = f'resources/models/{file}'
        print(file)
        self.model = load_model(path)


    def neural_predict(self, X_input:object) -> float:
        return self.model.predict(X_input, verbose=0)

    
    def save_neural_network(self, models_name:str, candles:int, timeframe:int) -> None:
        print('Saving the model...', datetime.now())
        path = f'resources/models/{datetime.now().strftime("%H%M")}_NN_{models_name}_{datetime.now().strftime("%d%m")}{candles:02d}_{timeframe}.h5'
        self.model.save(path)
