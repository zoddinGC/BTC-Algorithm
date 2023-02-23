from threading import Thread
from time import sleep
from datetime import datetime

import warnings
warnings.filterwarnings('ignore')

# Graphs
import plotly.graph_objects as go
import numpy as np

# Local imports
from functions.update_db import update_db
from functions.prepross_data import PreProssData
from operation_control.control_center import OperationControl

def check_api(test:bool=False, graph:bool=False):
    def show_graph():
        fig = go.Figure(data=[
                        go.Line(x=df.index,
                            y=[change_value1 for x in range(30)],
                            line_color='black',
                            name='Change1'),
                        go.Line(x=df.index,
                            y=[change_value2 for x in range(30)],
                            line_color='brown',
                            name='Change2'),
                        go.Candlestick(x=df.index,
                                     open=df['open_price'],
                                     high=df['high_price'],
                                     low=df['low_price'],
                                     close=df['close_price'],
                                     name='Candlestick')]).update_layout(xaxis_rangeslider_visible=False)

        fig.show()

    update_db(test)
 
    change_value1, change_value2, df = predict.predict_all_values()
    print(change_value1, change_value2)
    operation_control.check_condition(change_value1=change_value1, change_value2=change_value2)

    if graph: show_graph()

"""
    ========== IMPORTANT ========
    • Move to (G) 1.5 v 1 (L) after prices hits 2 dollars (or 0.01%) close to target (trailling)
    • Increse speed of the algorithm
"""


def schedule_api(timeframe=15):
    check_api(test=True)
    while True:
        if datetime.now().minute % timeframe == 0 and datetime.now().second <= 5:
            check_api()
            sleep(5)
        time = operation_control.check_status(return_value=True)
        sleep(time)

predict = PreProssData(timeframe=15, candles=20)
operation_control = OperationControl()
thread = Thread(target=schedule_api)
thread.start()
