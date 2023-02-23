from datetime import datetime
from keras.models import load_model
import numpy as np
import pandas as pd


class NeuralNetwork():
    def __init__(self) -> None:
        pass

    def __get_model(self, start:str):
        import os

        files = os.listdir('src/resources/models')

        return files[0] if start == 'AA' else files[1]

    
    def pre_load_model(self, start:str):
        file = self.__get_model(start)
        path = f'src/resources/models/{file}'
        self.model = load_model(path)


    def neural_predict(self, X_input:object) -> float:
        return self.model.predict(X_input, verbose=0)
