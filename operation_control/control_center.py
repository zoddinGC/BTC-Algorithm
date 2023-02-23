from binance.client import Client
from requests import get
from datetime import datetime
from os import SEEK_END, SEEK_CUR

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
            path = 'operation_control/status.txt'
            with open(path, 'r') as file:
                info = file.readline().split(',')
                self.status = info[0]
                self.stop, self.target = float(info[1]), float(info[2])
                # New feature
                self.trailling, self.new_stop, self.quantity = float(info[3]), float(info[4]), float(info[5])

                print(datetime.now())

            if self.status in ['buy', 'sell']: self.__check_operation()
            # else: self.__check_liquidity()

        if return_value:
            if self.status in ['buy', 'sell']:
                return 0
            else:
                return 0.5


    def __check_operation(self):
        price = self.__getting_price()

        try: type(self.time)
        except: self.__get_time()

        if self.status == 'sell':
            # New feature
            if price <= self.trailling: self.stop = self.new_stop

            if price >= self.stop:
                self.__buy_order('stop', quantity=self.quantity)
                self.__close_operation_status()

            elif price <= self.target:
                self.__buy_order('gain', quantity=self.quantity)
                self.__close_operation_status()

        elif self.status == 'buy':
            # New Feature
            if price >= self.trailling: self.stop = self.new_stop

            if price <= self.stop:
                self.__sell_order('stop', quantity=self.quantity)
                self.__close_operation_status()

            elif price >= self.target:
                self.__sell_order('gain', quantity=self.quantity)
                self.__close_operation_status()

        print(price, datetime.now())
                
    
    def check_condition(self, change_value1:int or float, change_value2:int or float, ma100:float, ammount_usd:float=2):

        #                            New Feature
        next_operation, stop, target, open_price = check_lines(change_value1=change_value1, change_value2=change_value2, ma100=ma100)
        quantity = round(ammount_usd / abs(open_price - stop), 3) if stop != 0 else 0

        if self.status == 'nope' and next_operation == 'buy' and datetime.now().minute % 15 == 0:
            self.__buy_order(' buy', stop, target, quantity=quantity)
            self.time = datetime.now()
            self.status = 'buy'

            self.stop, self.target, self.quantity = stop, target, quantity # New feature
            # New feature
            self.trailling, self.new_stop = target - (target - open_price) * 0.04, (target - open_price) * 0.75 + open_price

            self.__write_status()
        
        elif self.status == 'nope' and next_operation == 'sell' and datetime.now().minute % 15 == 0:
            self.__sell_order('sell', stop, target, quantity=quantity)
            self.time = datetime.now()
            self.status = 'sell'

            self.stop, self.target, self.quantity = stop, target, quantity # New feature
            # New feature
            self.trailling, self.new_stop = target + (open_price - target) * 0.04, open_price - (open_price - target) * 0.75

            self.__write_status()
        
        elif (self.status != 'nope' and int((datetime.now() - self.time).total_seconds()) >= 21_600) or \
             (self.status != 'nope'and next_operation != 'nope' and next_operation != self.status):
            self.__buy_order('trai', quantity=self.quantity) if self.status == 'sell' else self.__sell_order('trai', quantity=self.quantity)
            self.__close_operation_status()
        
        else:
            self.__logging(operation_price=0, next_operation=self.status, stop=stop, target=target)
            
        self.check_status()


    def __logging(self, operation_price, next_operation, stop, target):
        with open('log.txt', 'a') as file:
            file.write(f'\n{datetime.now()}, price: {operation_price:10.3f}, type: {next_operation.upper()}, stop: {stop:10.3f}, target: {target:10.3f}')
    
    def __write_status(self):
        path = 'operation_control/status.txt'
        with open(path, 'w') as file:
            file.write(f'{self.status},{self.stop},{self.target},{self.trailling},{self.new_stop},{self.quantity}')

    def __buy_order(self, order_type:str, stop:float=0, target:float=0, quantity:float=0.01):
        try:
            print('BUYING...', order_type.upper())
            buy_order = client.create_test_order(
                                symbol='BTCUSDT',
                                side='BUY',
                                type='MARKET',
                                quantity=quantity)
            
            self.__logging(operation_price=self.__getting_price(), next_operation=order_type, stop=stop, target=target)           

            with open('operation_log.txt', 'a') as file:
                file.write(f'\n{datetime.now()}, Buy, {quantity}')

            print('BOUGHT.')

        except Exception as e:
            with open('error.txt', 'a') as file:
                file.write(f'\n{datetime.now()}, Exception occurred: {e}')

    def __sell_order(self, order_type:str, stop:float=0, target:float=0, quantity:float=0.01):
        try:
            print('SELLING...', order_type.upper())
            sell_order = client.create_test_order(
                                symbol='BTCUSDT',
                                side='SELL',
                                type='MARKET',
                                quantity=quantity)

            self.__logging(operation_price=self.__getting_price(), next_operation=order_type, stop=stop, target=target)

            with open('operation_log.txt', 'a') as file:
                file.write(f'\n{datetime.now()}, Sell, {quantity}')

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

    
    def __close_operation_status(self):
        self.status = 'nope'
        self.target, self.stop, self.trailling, self.new_stop, self.quantity = 0, 0, 0, 0, 0
        self.__write_status()


    def __getting_price(self):
        # Defining key/request url
        key = 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'

        # Requesting data from url
        while True:
            try:
                # Get from requests
                data = get(key)  
                break
            except: continue
            
        return float(data.json()['price'])

    
    def __get_time(self):
        with open('operation_log.txt', 'rb') as f:
            try:  # catch OSError in case of a one line file 
                f.seek(-2, SEEK_END)
                while f.read(1) != b'\n':
                    f.seek(-2, SEEK_CUR)
            except OSError:
                f.seek(0)
            last_line = f.readline().decode()

            last_line = last_line[:last_line.find('.')]
            self.time = datetime.strptime(last_line, '%Y-%m-%d %H:%M:%S')
