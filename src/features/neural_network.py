"""
    This class is responsible to locate where the Neural Network
    models are stored, load them, and use them to predict the
    Bitcoin's features.
"""

from os import listdir
from keras.models import load_model


class NeuralNetwork():
    """
        This class instances one variable called 'model' and
        takes no arguments on the first call.
    """

    def __init__(self):
        self.model = None

    def __get_model(self, start:str):
        """
            This module will locate all the Neural Network models
            stored in the script.

            ~It will be improved in future updates
        """

        files = listdir('src/resources/models')

        return files[0] if start == 'AA' else files[1]


    def pre_load_model(self, start:str) -> None:
        """
            This module is responsible to load the Keras Neural
            Network model.
        """

        file = self.__get_model(start)
        path = f'src/resources/models/{file}'
        self.model = load_model(path)


    def neural_predict(self, X_input:object) -> float:
        """
            This module will use the loaded model and the input
            features to predict the target feature.
        """

        return self.model.predict(X_input, verbose=0)
