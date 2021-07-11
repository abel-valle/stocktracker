import pandas as pd
import numpy as np
import talib
import time

from pymongo import MongoClient

MONGO_URI = 'mongodb://localhost'
client = MongoClient(MONGO_URI)
db = client['stockdb']

stocks = db['stock']
history = db['history']


# Crossing MACD the Signal
def cross(signal, macd, cci, close):
    buy = []
    sell = []
    for i in range(len(signal)):
        if (
                not (np.isnan(macd[i - 1]))
                and not (np.isnan(signal[i - 1]))
                and (macd[i] > signal[i]) != (macd[i - 1] > signal[i - 1])
        ):
            if macd[i] > signal[i] and not (macd[i - 1] > signal[i - 1]):
                buy.append(close[i])
                sell.append(np.nan)
            else:
                sell.append(close[i])
                buy.append(np.nan)
        else:
            buy.append(np.nan)
            sell.append(np.nan)
    return buy, sell


def calculate_profit(buy, sell):
    capital = 10000.0
    profit = 0
    bought = False
    buy_price = 0
    n = 0

    for i in range(len(buy)):
        if not (np.isnan(buy[i])):
            n = capital // buy[i]
            buy_price = buy[i]
            capital -= n * buy_price
            # print('buy : ', buy[i])
            bought = True

        if bought and not (np.isnan(sell[i])):
            capital += n * sell[i]
            # print('sell: ', sell[i])
            # print('prof: ', profit)
            # print('---------------')
            buy_price = 0
            bought = False

    return capital


def stock_analysis():
    stock_list = stocks.find()
    print(type(stock_list))
    counter = 1
    start_time = time.time()
    end_time = None

    for stock_info in stock_list:
        symbol = stock_info['symbol']
        # Make a query to the specific DB and Collection
        cursor = history.find({'symbol': symbol})

        # Expand the cursor and construct the DataFrame
        df = pd.DataFrame(list(cursor))
        del df['_id']

        # Set the date to be the index
        df = df.set_index(pd.DatetimeIndex(df['date'].values))

        # Calculate MACD and MACD-Signal
        df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['close'])
        df['cci'] = talib.CCI(df['high'], df['low'], df['close'], timeperiod=20)

        buy, sell = cross(df['macd_signal'], df['macd'], df['cci'], df['close'])

        # Add buy and sell columns
        df['buy'] = buy
        df['sell'] = sell

        profit = calculate_profit(buy, sell)

        for index, row in df.iterrows():
            # print(row['date'], row['close'])
            result = history.find_one({'date': row['date'], 'symbol': row['symbol']})
            result = history.update_one(
                {'date': row['date'], 'symbol': row['symbol']},
                {
                    '$set': {
                        'macd': row['macd'],
                        'macd_signal': row['macd_signal'],
                        'macd_hist': row['macd_hist'],
                        'cci': row['cci'],
                        'buy': row['buy'],
                        'sell': row['sell']
                    }
                }
            )

        print("{} {} processed.".format(counter, symbol))
        counter += 1


stock_analysis()
