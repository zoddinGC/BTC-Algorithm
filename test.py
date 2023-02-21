from binance.client import Client
from time import sleep
from binance.cm_futures import CMFutures

# Local Imports
from operation_control.able_operation import check_lines
import functions.config as config

# Creating objects
client = Client(API_NEW, API_SECRET_NEW) # config.API_KEY, config.API_SECRET)

client.futures_change_leverage(symbol='BTCUSDT', leverage=20)

btc_balance = client.futures_account_balance(asset='BTC')[0]['balance']
print(btc_balance)

test = client.futures_create_order(
              symbol='BTCUSDT',
              side='BUY',
              type='MARKET',
              quantity=0.001)

sleep(2)

btc_balance = client.futures_account_balance(asset='BTCUSDT')
print(btc_balance)
