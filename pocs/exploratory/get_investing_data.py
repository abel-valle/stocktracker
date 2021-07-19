import investpy
from datetime import datetime
from pymongo import MongoClient

DATA_FOLDER = 'data/'
INI_DATE = '01/01/2018'
END_DATE = datetime.today().strftime('%d/%m/%Y')
COUNTRY = 'mexico'

MONGO_URI = 'mongodb://localhost'
client = MongoClient(MONGO_URI)
db = client['stockdb']
stocks_tech_ind = db['stock_tech_ind']

symbol_list = investpy.stocks.get_stocks_list('mexico')

profile = investpy.stocks.get_stocks_dict('mexico')
print(profile)

# for symbol in symbol_list:
#    print(symbol)

# df = investpy.get_stock_historical_data(stock='ICA',
#                                         country='mexico',
#                                         from_date=INI_DATE,
#                                         to_date=END_DATE)
# df.reset_index(inplace=True)
# for index, row in df.iterrows():
#     print('{}, {}'.format(row['Date'], row['Close']))

# df = investpy.technical_indicators(name='BTC/MXN', country='mexico', product_type='stock')


def get_cryptos():
    dict = investpy.crypto.get_cryptos()
    data = investpy.get_crypto_historical_data(crypto='bitcoin', from_date=INI_DATE, to_date=END_DATE)
    print(data.head())


def get_stocks():
    stock_dict = investpy.stocks.get_stocks_dict(COUNTRY)
    return stock_dict


def get_tech_indicators():
    stock_dict = get_stocks()
    counter = 1
    for stock_info in stock_dict:
        symbol = stock_info['symbol']
        try:
            df = investpy.technical_indicators(name=symbol, country='mexico', product_type='stock')

            print('{} {} Success.'.format(counter, symbol))
        except Exception as e:
            print('{} {} Exception.'.format(counter, symbol))
            print(type(e))
            print(e.args)
        counter += 1


def create_stock_tech_indicators():
    stock_dict = investpy.stocks.get_stocks_dict(COUNTRY)
    counter = 1
    for stock_info in stock_dict:
        symbol = stock_info['symbol']
        name = stock_info['name']
        try:
            df = investpy.technical_indicators(name=symbol, country='mexico', product_type='stock')
            df.insert(1, 'symbol', symbol)
            df.insert(2, 'name', name)
            df_dict = df.to_dict('records')
            stocks_tech_ind.insert_many(df_dict)
            print('{} {} Success.'.format(counter, symbol))
        except Exception as e:
            print('{} {} Exception.'.format(counter, symbol))
            print(type(e))
            print(e.args)
        counter += 1
    print('Stock tech indicators saved.')


# function execution.
get_tech_indicators()
