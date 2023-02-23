"""
    This module has the purpose of store in memory the variables to
    used to predict some values. It initialize:
    • Scaler - from sklearm.preprocessing import StandardScaler
    • 2 Neural Network models from Keras
"""

from joblib import load
import pandas as pd

# Local imports
from data_processing.create_features import clean_dataset
from features.neural_network import NeuralNetwork


class PreProssData():
    """
        candles -> ammount of candles used as input features in the model

        This class will instantiate the Scaler to scale the input features
        and the neural netowrk models.
    """

    def __init__(self, candles:int=20) -> None:
        self.scaler = self.get_scaler()
        self.candles = candles

        self.__change_above = NeuralNetwork()
        self.__change_above.pre_load_model(start='AA')

        self.__change_below = NeuralNetwork()
        self.__change_below.pre_load_model(start='BA')


    def get_scaler(self):
        """
            This module loads the Scaler stored in this script using the
            module 'load' from Joblib library.
        """

        scaler = load('src/resources/scaler/scaler.save')
        return scaler


    def get_scaled_data(self):
        """
            This module will load the dataset in a Pandas DataFrame, and
            clean it using the local function 'clean_dataset'.
            After doing it, it will use the Scaler loaded previously, and
            reshape using Numpy, then will return the DataFrame for plot,
            the Scaled Data to use in the model and the value of the Moving
            Avarage of 100 periods.
        """

        dataset = pd.read_csv('src/resources/dataset/live_data_15min.csv')        
        df, ma100 = clean_dataset(dataset=dataset)

        scaled_data = self.scaler.transform(df[-self.candles-3:-3])
        scaled_data = scaled_data.reshape(-1, self.candles, scaled_data.shape[1])

        return scaled_data, df, ma100


    def predict_all_values(self):
        """
            This module calls this other class module get_scaled_data, and
            use the returned values to predict the features using the Keras
            Neural Network model built for this project.
        """

        scaled_data, df, ma100 = self.get_scaled_data()

        change1 = (
            df['open_price'][-2] *
            self.__change_above.neural_predict(X_input=scaled_data)[0][0] / 50 +
            df['open_price'][-2]
        )

        change2 = (
            df['open_price'][-2] *
            self.__change_below.neural_predict(X_input=scaled_data)[0][0] / 50 +
            df['open_price'][-2]
        )

        return change1, change2, ma100
