import investpy
import json
from datetime import datetime
from enum import Enum


class Period(Enum):
    DAY = 1
    WEEK = 2
    MONTH = 3


INI_DATE = '01/01/2018'
END_DATE = '02/07/2021'
# END_DATE = datetime.today().strftime('%d/%m/%Y')
COUNTRY = 'mexico'
DATA_PATH = 'data/'

stock_list = investpy.stocks.get_stocks_dict(COUNTRY)
counter = 1
for stock in stock_list:
    symbol = stock['symbol']
    try:
        df = investpy.get_stock_historical_data(stock=symbol,
                                                country=COUNTRY,
                                                from_date=INI_DATE,
                                                to_date=END_DATE)
        file_path = "{}{}_{}.csv".format(DATA_PATH, symbol, Period.DAY.value)
        df.to_csv(file_path)
        print('Stock ', counter, ':', symbol, 'downloaded')
    except:
        print('Stock ', symbol, ' not found')
    counter += 1
