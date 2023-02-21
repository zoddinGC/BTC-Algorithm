from binance.client import Client
import requests
from datetime import datetime
import csv
import os

# Local Imports
from operation_control.able_operation import check_lines
import functions.config as config

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
            # else: self.__check_liquidity()

        if return_value:
            if self.status in ['buy', 'sell']:
                return 0.3
            else:
                return 0.7


    def __check_operation(self):
        price = self.__getting_price()

        try:
            type(self.time)
        except:
            self.__get_time()

        if self.status == 'sell':

            if price >= self.stop:
                self.__buy_order()
                self.status = 'nope'
                self.target = 0
                self.stop = 0
                self.__write_status()
                self.__logging(operation_price=price, next_operation='STOP', stop=0, target=0)

            elif price <= self.target:
                self.__buy_order()
                self.status = 'nope'
                self.target = 0
                self.stop = 0
                self.__write_status()
                self.__logging(operation_price=price, next_operation='GAIN', stop=0, target=0)

        elif self.status == 'buy':
            if price <= self.stop:
                self.__sell_order()
                self.status = 'nope'
                self.target = 0
                self.stop = 0
                self.__write_status()
                self.__logging(operation_price=price, next_operation='STOP', stop=0, target=0)

            elif price >= self.target:
                self.__sell_order()
                self.status = 'nope'
                self.target = 0
                self.stop = 0
                self.__write_status()
                self.__logging(operation_price=price, next_operation='GAIN', stop=0, target=0)

        print(price, datetime.now())
                
    
    def check_condition(self,change_value1:int or float, change_value2:int or float):
        next_operation, stop, target = check_lines(change_value1=change_value1, change_value2=change_value2)

        if self.status == 'nope' and next_operation == 'buy':
            self.__buy_order()
            self.time = datetime.now()
            self.status = 'buy'
            buy_price = self.__getting_price()

            self.__logging(operation_price=buy_price, next_operation=self.status, stop=stop, target=target)

            self.stop = stop
            self.target = target
        
        elif self.status == 'nope' and next_operation == 'sell':
            self.__sell_order()
            self.time = datetime.now()
            self.status = 'sell'
            sell_price = self.__getting_price()

            self.__logging(operation_price=sell_price, next_operation=self.status, stop=stop, target=target)

            self.stop = stop
            self.target = target
        
        elif self.status != 'nope' and int((datetime.now() - self.time).total_seconds()) >= 36_000:
            self.__buy_order() if self.status == 'sell' else self.__sell_order()
            self.status = 'nope'
            current_price = self.__getting_price()
            self.stop = 0
            self.target = 0

            self.__logging(operation_price=current_price, next_operation='trailling', stop=stop, target=target)
        
        else:
            self.__logging(operation_price=0, next_operation=self.status, stop=stop, target=target)

        self.__write_status()
        self.check_status()


    def __logging(self, operation_price, next_operation, stop, target):
        with open('log.txt', 'a') as file:
            file.write(f'\n{datetime.now()}, B/S PRICE:{operation_price}, TYPE: {next_operation}, STOP: {stop}, TARGET: {target}')
    
    def __write_status(self):
        path = 'operation_control/status.csv'
        with open(path, 'w') as file:
            file.write(f'{self.status},{self.stop},{self.target}')

    def __buy_order(self, quantity:float=0.01):
        try:
            print('BUYING...')
            buy_order = client.create_test_order(
                                symbol='BTCUSDT',
                                side='BUY',
                                type='MARKET',
                                quantity=quantity)
            with open('operation_log.txt', 'a') as file:
                file.write(f'\n{datetime.now()}, Buy {quantity}')

            print('BOUGHT.')

        except Exception as e:
            with open('error.txt', 'a') as file:
                file.write(f'\n{datetime.now()}, Exception occurred: {e}')

    def __sell_order(self, quantity:float=0.01):
        try:
            print('SELLING...')
            sell_order = client.create_test_order(
                                symbol='BTCUSDT',
                                side='SELL',
                                type='MARKET',
                                quantity=quantity)
            with open('operation_log.txt', 'a') as file:
                file.write(f'\n{datetime.now()}, Sell {quantity}')

            print('SOLD.')
            
        except Exception as e:
            with open('error.txt', 'a') as file:
                file.write(f'\n{datetime.now()}, Exception occurred: {e}')


    def __check_liquidity(self):
        btc_balance = float(client.futures_account_balance(asset='BTC')[0]['balance'])
        if btc_balance < 0:
            self.__buy_order(btc_balance)
        elif btc_balance > 0:
            self.__sell_order(btc_balance)


    def __getting_price(self):
        # defining key/request url
        key = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"

        # requesting data from url
        data = requests.get(key)  
        data = data.json()

        return float(data['price'])

    
    def __get_time(self):
        with open('operation_log.txt', 'rb') as f:
            try:  # catch OSError in case of a one line file 
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b'\n':
                    f.seek(-2, os.SEEK_CUR)
            except OSError:
                f.seek(0)
            last_line = f.readline().decode()

            last_line = last_line[:last_line.find('.')]
            self.time = datetime.strptime(last_line, '%Y-%m-%d %H:%M:%S')
