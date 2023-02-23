"""
              BTC TRADE V3.2
    =======  TESTING  FEATURES  ======
    ✓ Move to (G) 1.75 v 1 (L) after prices hits 2 dollars (or 0.015%) close to target (trailling)
    ✓ Fix Gain to 4 dol and Loss to 2 dol (ammount_usd)

    ========  FUTURE UPDATES  ======
    • Copy real graph style to speed up the operation system
    • Send email or alert when operation is unsuccessful
    • Create a new model to predict max and min variation (%) for the next 10 candles
    • Create a new model to predict a new feature searching within the next 10 candles if the
        max/top is 2 times higher than entrance - stop
    • Create a new feature for traditional top and bottom, and add a new feature if the next
        top/bottom change by time or price
    • Test RandomForest, XGBoost, and LGBM models before new neural network model
    • Derivate (triangle) of Price x Time
    • Improve Neural Network get_model module
"""

# Python libraries import
from threading import Thread
from time import sleep
from datetime import datetime
from warnings import filterwarnings

# Local imports
from data_processing.update_database import update_database
from features.prepross_data import PreProssData
from features.operation_control_center import OperationControl


filterwarnings('ignore')


def check_api(first_load_data:bool=False):
    """
        first_load_data -> True if this is the first time the program is running

        This module will update the database from Binance API and
        check inside the machine learning model if the market
        condition starts an operation (trigger)
    """

    update_database(first_load_data)

    change_value1, change_value2, ma100 = predict.predict_all_values()

    operation_control.check_condition(
        ammount_usd=2,
        change_value1=change_value1,
        change_value2=change_value2,
        ma100=ma100
    )


def schedule_api(timeframe=15):
    """
        This module Schedule the database update from Binance API
        for every 15 minutes. When the the trigger starts an
        operation, it will check the API 2 or 3 times per second.
    """

    check_api(first_load_data = True)
    while True:
        if (datetime.now().minute % timeframe == 0) and (datetime.now().second <= 5):
            check_api()
            sleep(5)
        time = operation_control.check_status(return_value = True)
        sleep(time)


predict = PreProssData(candles=20)
operation_control = OperationControl()
thread = Thread(target=schedule_api)
thread.start()
