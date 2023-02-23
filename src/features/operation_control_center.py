"""
    This class is responsible to control when to enter, exit or do
    nothing in the Bitcoin. It will send orders to the Binance
    Account and save logs of what is being done.
"""

from datetime import datetime
from os import SEEK_END, SEEK_CUR
from os import getenv
from requests import get
from dotenv import load_dotenv
from binance.client import Client

# Local Imports
from features.check_condition import check_lines


# Creating objects
load_dotenv()
API_KEY = getenv('API_KEY')
API_SECRET = getenv('API_SECRET')

client = Client(API_KEY, API_SECRET)

class OperationControl():
    """
        This class takes no arguments and instantiates the 'status'
        to 'nope' when first called.
    """

    def __init__(self):
        self.status =    'nope'  # 'buy', 'sell' or 'nope'
        self.stop =      0       # price to set the stop loss
        self.target =    0       # price to set the gain target
        self.trailling = 0       # price to stop gain
        self.new_stop =  0       # price of the new stop gain
        self.quantity =  0       # quantity of bitcoin to buy/sell
        self.check_status()


    def check_status(self, return_value:bool=False) -> None or float:
        """
            return_value -> False bool: if True, it will return 0 for the
                delay between updates if you're in an operation and it will
                return 0.5 if you're not.

            This module is responsible to check the status of the operation.
            If you're in an operation, it will save the 'status' as buy/sell.
            If you're NOT in an operaetion, it will save as nope.
        """

        if self.status in ['buy', 'sell']:
            self.__check_operation()

        else:
            path = 'src/features/status.txt'
            with open(path, 'r', encoding='utf-8') as file:
                info = file.readline().split(',')

                self.status =    info[0]        # 'buy', 'sell' or 'nope'
                self.stop =      float(info[1]) # price to set the stop loss
                self.target =    float(info[2]) # price to set the gain target
                self.trailling = float(info[3]) # price to stop gain
                self.new_stop =  float(info[4]) # price of the new stop gain
                self.quantity =  float(info[5]) # quantity of Bitcoin

                print(datetime.now())

            if self.status in ['buy', 'sell']:
                self.__check_operation()
            # else:
                # self.__check_liquidity()

        if return_value:
            if self.status in ['buy', 'sell']:
                return 0
            return 0.5


    def __check_operation(self) -> None:
        price = self.__getting_price()

        try:
            type(self.time)
        except:
            self.__get_time()

        if self.status == 'sell':
            # New feature
            if price <= self.trailling:
                self.stop = self.new_stop

            if price >= self.stop:
                self.__buy_order('stop', quantity=self.quantity)
                self.__close_operation_status()

            elif price <= self.target:
                self.__buy_order('gain', quantity=self.quantity)
                self.__close_operation_status()

        elif self.status == 'buy':
            # New Feature
            if price >= self.trailling:
                self.stop = self.new_stop

            if price <= self.stop:
                self.__sell_order('stop', quantity=self.quantity)
                self.__close_operation_status()

            elif price >= self.target:
                self.__sell_order('gain', quantity=self.quantity)
                self.__close_operation_status()

        print(price, datetime.now())


    def check_condition(
        self,
        change_value1:int or float,
        change_value2:int or float,
        ma100:float,
        ammount_usd:float=2
    ) -> None:

        """
            change_value1 -> is the first predicted value of the neural network
            change_value1 -> is the second predicted value of the neural network
            ma100 -> is the moving avarage of the last 100 close price candles
            ammount_usd -> the max ammount of the stop loss

            This module is responsible to check if the condition to sell/buy is met
            and then send orders to the Binance Account.
        """

        next_operation, stop, target, open_price = check_lines(
            change_value1=change_value1,
            change_value2=change_value2,
            ma100=ma100
        )

        quantity = round(ammount_usd / abs(open_price - stop), 3) if stop != 0 else 0

        if self.status == 'nope' and next_operation == 'buy' and datetime.now().minute % 15 == 0:
            self.__buy_order(' buy', stop, target, quantity=quantity)
            self.time = datetime.now()
            self.status = 'buy'

            self.stop, self.target, self.quantity = stop, target, quantity
            self.trailling = target - (target - open_price) * 0.04
            self.new_stop =  (target - open_price) * 0.75 + open_price

            self.__write_status()

        elif self.status == 'nope' and next_operation == 'sell' and datetime.now().minute % 15 == 0:
            self.__sell_order('sell', stop, target, quantity=quantity)
            self.time = datetime.now()
            self.status = 'sell'

            self.stop, self.target, self.quantity = stop, target, quantity
            self.trailling = target + (open_price - target) * 0.04
            self.new_stop = open_price - (open_price - target) * 0.75

            self.__write_status()

        elif (self.status != 'nope' and int((datetime.now() - self.time).total_seconds()) >= 21_600) or \
             (self.status != 'nope'and next_operation != 'nope' and next_operation != self.status):

            if self.status == 'sell':
                self.__buy_order('trai', quantity=self.quantity)
            else:
                self.__sell_order('trai', quantity=self.quantity)

            self.__close_operation_status()

        else:
            self.__logging(operation_price=0, next_operation=self.status, stop=stop, target=target)

        self.check_status()


    def __logging(self, operation_price, next_operation, stop, target):
        with open('src/logs/log.txt', 'a', encoding='utf-8') as file:
            file.write(
                f"""\n{datetime.now()}, 
                price: {operation_price:10.3f}, 
                type: {next_operation.upper()}, 
                stop: {stop:10.3f}, 
                target: {target:10.3f}"""
            )


    def __write_status(self):
        path = 'src/features/status.txt'
        with open(path, 'w', encoding='utf-8') as file:
            file.write(
                f"""{self.status},
                {self.stop},
                {self.target},
                {self.trailling},
                {self.new_stop},
                {self.quantity}"""
            )


    def __buy_order(self, order_type:str, stop:float=0, target:float=0, quantity:float=0.01):
        try:
            print('BUYING...', order_type.upper())
            buy_order = client.create_test_order(
                                symbol='BTCUSDT',
                                side='BUY',
                                type='MARKET',
                                quantity=quantity
                                )

            self.__logging(operation_price=self.__getting_price(), next_operation=order_type, stop=stop, target=target)           

            with open('src/logs/operation_log.txt', 'a', encoding='utf-8') as file:
                file.write(f'\n{datetime.now()}, Buy, {quantity}')

            print('BOUGHT.')

        except Exception as e:
            with open('src/logs/error.txt', 'a', encoding='utf-8') as file:
                file.write(f'\n{datetime.now()}, Exception occurred: {e}')


    def __sell_order(self, order_type:str, stop:float=0, target:float=0, quantity:float=0.01):
        try:
            print('SELLING...', order_type.upper())
            sell_order = client.create_test_order(
                                symbol='BTCUSDT',
                                side='SELL',
                                type='MARKET',
                                quantity=quantity
                                )

            self.__logging(operation_price=self.__getting_price(), next_operation=order_type, stop=stop, target=target)

            with open('src/logs/operation_log.txt', 'a', encoding='utf-8') as file:
                file.write(f'\n{datetime.now()}, Sell, {quantity}')

            print('SOLD.')

        except Exception as e:
            with open('src/logs/error.txt', 'a', encoding='utf-8') as file:
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
            except:
                continue

        return float(data.json()['price'])


    def __get_time(self):
        with open('src/logs/operation_log.txt', 'rb') as f:
            try:  # catch OSError in case of a one line file 
                f.seek(-2, SEEK_END)
                while f.read(1) != b'\n':
                    f.seek(-2, SEEK_CUR)
            except OSError:
                f.seek(0)
            last_line = f.readline().decode()

            last_line = last_line[:last_line.find('.')]
            self.time = datetime.strptime(last_line, '%Y-%m-%d %H:%M:%S')
