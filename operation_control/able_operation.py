from csv import reader


path = 'resources/dataset/daily_15min.csv'

def __last_candles(ma100:float):
    """
    Dict keys:

    Kline open time     0
    Open price          1
    High price          2
    Low price           3
    Close price         4
    Volume              5
    Kline Close time    6
    Quote asset volume  7
    Number of trades    8
    Taker buy base asset volume     9
    Taker buy quote asset volume   10
    Unused field, ignore.          11
    """

    with open(path, 'r') as file:
        files = reader(file)
        files = list(files)[-3:]

    # 2nd Last Candle = 0, Last Candle = 1, Actual Candle = 0
    last_candle = True if float(files[1][4]) - float(files[1][1]) > 0 else False
    last_second_candle = True if float(files[0][4]) - float(files[0][1]) > 0 else False

    last_max, last_min, open_price, last_open_price = float(files[1][2]), float(files[1][3]), float(files[2][1]), float(files[1][1])

    if last_candle:              # Range <= 200 USD                # 0.10% far from MA100
        range_ok = True if abs(open_price - last_min) <= 200 and abs(open_price - ma100) / ma100 >= 0.10/100 else False
    else:
        range_ok = True if abs(open_price - last_max) <= 200 and abs(open_price - ma100) / ma100 >= 0.10/100 else False

    #     True = green,    True = green,  True: <= 200
    return last_candle, last_second_candle, range_ok, open_price, last_open_price, last_max, last_min


def check_lines(change_value1:int or float, change_value2:int or float, ma100:float):
    last_candle, last_second_candle, range_ok, open_price, last_open_price, last_max, last_min = __last_candles(ma100=ma100)

    if last_candle and range_ok and not last_second_candle:
        if last_open_price > change_value1 and last_open_price > change_value2:
            buy_stop = last_min - 10
            buy_target = open_price + 2 * (open_price - buy_stop)

            return 'buy', buy_stop, buy_target, open_price

    elif not last_candle and last_second_candle and range_ok:
        if last_open_price < change_value1 and last_open_price < change_value2:
            sell_stop = last_max + 10
            sell_target = open_price + 2 * (open_price - sell_stop)

            return 'sell', sell_stop, sell_target, open_price
    
    return 'nope', 0, 0, 0