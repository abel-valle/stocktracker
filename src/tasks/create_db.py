import time
import investpy

from datetime import datetime

import numpy as np
from pymongo import MongoClient

INI_DATE = '01/01/2018'
# END_DATE = '02/07/2021'
END_DATE = datetime.today().strftime('%d/%m/%Y')
COUNTRY = 'mexico'

MONGO_URI = 'mongodb://localhost'
client = MongoClient(MONGO_URI)
db = client['stockdb']

db.drop_collection(name_or_collection='stock')
db.drop_collection(name_or_collection='history')
stocks = db['stock']
history = db['history']


def create_stock_info():
    stock_list = investpy.stocks.get_stocks_dict(COUNTRY)
    stocks.insert_many(stock_list)
    print('{} stock symbols saved.'.format(len(stock_list)))
    updated = stocks.update_many({}, {'$set': {
        'history': False,
        'macd_profit_d': np.nan,
        'macd_profit_w': np.nan,
        'macd_profit_m': np.nan
    }})
    print('{} documents updated.'.format(updated.modified_count))


def create_stock_history():
    stock_list = stocks.find()
    print(type(stock_list))
    counter = 1
    start_time = time.time()
    end_time = None

    for stock_info in stock_list:
        symbol = stock_info['symbol']
        try:
            df = investpy.get_stock_historical_data(stock=symbol, country=COUNTRY, from_date=INI_DATE, to_date=END_DATE)
            df.reset_index(inplace=True)
            # Rename columns.
            df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'currency']
            # Add columns.
            df.insert(1, 'symbol', symbol)
            df['macd'] = np.nan
            df['macd_signal'] = np.nan
            df['macd_hist'] = np.nan
            df['cci'] = np.nan
            df['buy'] = np.nan
            df['sell'] = np.nan
            df_dict = df.to_dict('records')
            history.insert_many(df_dict)
            stocks.update_one({'symbol': symbol}, {'$set': {
                'history': True
            }})
            print('{} Symbol {} history saved.'.format(counter, symbol))
        except Exception as e:
            print("{} Symbol {} history not found.".format(counter, symbol))
            print(type(e))
        counter += 1

    end_time = time.time()
    print("Execution time: {}".format(end_time - start_time))


create_stock_info()
create_stock_history()
