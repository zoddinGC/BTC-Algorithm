from threading import Thread
from time import sleep
from datetime import datetime

from warnings import filterwarnings
filterwarnings('ignore')

# Local imports
from functions.update_db import update_db
from functions.prepross_data import PreProssData
from operation_control.control_center import OperationControl

def check_api(test:bool=False):
    update_db(test)
 
    change_value1, change_value2, ma100 = predict.predict_all_values()
    operation_control.check_condition(change_value1=change_value1, change_value2=change_value2, ma100=ma100)

"""
    ========== IMPORTANT ========
    • Move to (G) 1.75 v 1 (L) after prices hits 2 dollars (or 0.015%) close to target (trailling)
    • Fix Gain and Loss to 2 dol
    • Copy real graph style for speed up operation
"""


def schedule_api(timeframe=15):
    check_api(test=True)
    while True:
        if datetime.now().minute % timeframe == 0 and datetime.now().second <= 5:
            check_api()
            sleep(5)
        time = operation_control.check_status(return_value=True)
        sleep(time)

predict = PreProssData(candles=20)
operation_control = OperationControl()
thread = Thread(target=schedule_api)
thread.start()
