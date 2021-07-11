import investpy
from datetime import datetime

DATA_FOLDER = 'data/'
INI_DATE = '01/01/2018'
END_DATE = datetime.today().strftime('%d/%m/%Y')

symbol_list = investpy.stocks.get_stocks_list('mexico')

profile = investpy.stocks.get_stocks_dict('mexico')
print(profile)

# for symbol in symbol_list:
#    print(symbol)

df = investpy.get_stock_historical_data(stock='ICA',
                                        country='mexico',
                                        from_date=INI_DATE,
                                        to_date=END_DATE)
df.reset_index(inplace=True)
for index, row in df.iterrows():
    print('{}, {}'.format(row['Date'], row['Close']))
