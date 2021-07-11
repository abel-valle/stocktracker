import time
import investpy

from datetime import datetime
from pymongo import MongoClient

UPDATE_DATE = '01/01/2018'
COUNTRY = 'mexico'

MONGO_URI = 'mongodb://localhost'
client = MongoClient(MONGO_URI)

db = client['stockdb']

stocks = db['stock']
history = db['history']

def update_stock_history():
    stock_list = stocks.find()
    print(type(stock_list))
    counter = 1
    start_time = time.time()
    end_time = None

    for stock_info in stock_list:
        symbol = stock_info['symbol']
        try:
            df = investpy.get_stock_historical_data(stock=symbol, country=COUNTRY, from_date=UPDATE_DATE, to_date=UPDATE_DATE)
            df.reset_index(inplace=True)
            df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'currency']
            df.insert(1, 'symbol', symbol)
            df_dict = df.to_dict('records')
            history.insert_many(df_dict)
            print('{} Symbol {} history updated.'.format(counter, symbol))
        except Exception as exception:
            print("{} {} symbol history not found.".format(counter, symbol))
            print(type(exception))
        counter += 1

    end_time = time.time()
    print("Execution time: {}".format(end_time - start_time))