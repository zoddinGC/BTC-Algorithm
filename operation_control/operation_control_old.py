from binance.client import Client
import requests
from datetime import datetime
import csv

# Local Imports
from operation_control.able_operation import check_lines
import functions.config as config


# CHECK BINANCE API FOR TRADING BTC/USD

# Creating objects
client = Client(config.API_KEY, config.API_SECRET)

class OperationControl():
    def __init__(self) -> None:
        self.status = 'nope'
        self.check_status()
        
    
    def check_status(self, return_value:bool=False):
        if self.status in ['buy', 'sell']: self.__check_operation()

        else:
            path = 'operation_control/status.csv'
            with open(path, 'r') as file:
                info = list(csv.reader(file))[0]
                self.status = info[0]
                self.stop = float(info[1])
                self.target = float(info[2])
                print(datetime.now())

            if self.status in ['buy', 'sell']: self.__check_operation()

        if return_value:
            if self.status in ['buy', 'sell']:
                return 0.3
            else:
                return 0.7


    def __check_operation(self):
        price = self.__getting_price()
        if self.status == 'sell':

            if price >= self.stop:
                self.status = 'nope'
                self.target = 0
                self.stop = 0
                self.__write_status()
                self.__write_log(operation_price=price, next_operation='STOP', stop=0, target=0)

            elif price <= self.target:
                self.status = 'nope'
                self.target = 0
                self.stop = 0
                self.__write_status()
                self.__write_log(operation_price=price, next_operation='GAIN', stop=0, target=0)

        elif self.status == 'buy':
            if price <= self.stop:
                self.status = 'nope'
                self.target = 0
                self.stop = 0
                self.__write_status()
                self.__write_log(operation_price=price, next_operation='STOP', stop=0, target=0)

            elif price >= self.target:
                self.status = 'nope'
                self.target = 0
                self.stop = 0
                self.__write_status()
                self.__write_log(operation_price=price, next_operation='GAIN', stop=0, target=0)
        print(price, datetime.now())
                
    
    def check_condition(self, change_value1:int or float, change_value2:int or float):
        next_operation, stop, target = check_lines(change_value1=change_value1, change_value2=change_value2)

        if self.status == 'nope' and next_operation == 'buy':
            self.status = 'buy'
            buy_price = self.__getting_price()

            self.__write_log(operation_price=buy_price, next_operation=self.status, stop=stop, target=target)

            self.stop = stop
            self.target = target
        
        elif self.status == 'nope' and next_operation == 'sell':
            self.status = 'sell'
            sell_price = self.__getting_price()

            self.__write_log(operation_price=sell_price, next_operation=self.status, stop=stop, target=target)

            self.stop = stop
            self.target = target
        
        elif self.status != 'sell' and next_operation != 'buy' and next_operation != 'nope':
            self.status = 'nope'
            current_price = self.__getting_price()
            self.stop = 0
            self.target = 0

            self.__write_log(operation_price=current_price, next_operation='trailling', stop=stop, target=target)
        
        else:
            self.__write_log(operation_price=0, next_operation=self.status, stop=stop, target=target)

        self.__write_status()
        self.check_status()


    def __write_log(self, operation_price, next_operation, stop, target):
        with open('log.txt', 'a') as file:
            file.write(f'\n{datetime.now()}, B/S PRICE:{operation_price}, TYPE: {next_operation}, STOP: {stop}, TARGET: {target}')
    
    def __write_status(self):
        path = 'operation_control/status.csv'
        with open(path, 'w') as file:
            file.write(f'{self.status},{self.stop},{self.target}')


    def __getting_price(self):
        # defining key/request url
        key = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"

        # requesting data from url
        data = requests.get(key)  
        data = data.json()

        return float(data['price'])
