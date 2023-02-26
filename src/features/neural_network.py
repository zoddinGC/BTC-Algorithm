"""
    This class is responsible to locate where the Neural Network
    models are stored, load them, and use them to predict the
    Bitcoin's features.
"""

from os import listdir
from keras.models import load_model


class NeuralNetwork():
    """
        This Class will load the neural network model by a given
        name such as 'AA' or 'BA'.

        *model_name: str -> 'AA' or 'BA'
    """

    def __init__(self, model_name:str):
        self._model = self.__set_model(model_name)


    def __set_model(self, model_name:str) -> object:
        """
            This module will locate all the Neural Network models
            stored in the script.

            ~It will be improved in future updates
        """

        path = 'src/resources/models'
        files = listdir(path)
        file = files[0] if model_name == 'AA' else files[1]

        return load_model(path + '/' + file)


    def neural_predict(self, X_input:object) -> float:
        """
            This module will use the loaded model and the input
            features to predict the target feature.
        """

        return self._model.predict(X_input, verbose=0)
