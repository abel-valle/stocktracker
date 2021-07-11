import time
import model
import investpy

from datetime import datetime
from flask import Flask
from flask_mongoengine import MongoEngine

INI_DATE = '01/01/2018'
END_DATE = datetime.today().strftime('%d/%m/%Y')
COUNTRY = 'mexico'

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost/stocksdb'
}

db = MongoEngine(app)


def create_data():
    stock_list = investpy.stocks.get_stocks_dict(COUNTRY)
    counter = 1
    start_time = time.time()
    end_time = None
    for stock_info in stock_list:
        stock = model.Stock(**stock_info)
        print('Processing {}'.format(stock.symbol))
        try:
            df = investpy.get_stock_historical_data(stock=stock.symbol,
                                                    country=COUNTRY,
                                                    from_date=INI_DATE,
                                                    to_date=END_DATE)
            df.reset_index(inplace=True)
            for index, row in df.iterrows():
                sample = model.Sample()
                sample.date = row['Date']
                sample.open = row['Open']
                sample.high = row['High']
                sample.low = row['Low']
                sample.close = row['Close']
                stock.history.append(sample)

            stock.date = stock.history[-1].date
            stock.close = stock.history[-1].close
            print('Saving {}:{}'.format(counter, stock.symbol))
            stock.save()
        except Exception:
            print("Stock {}:{} history not found.".format(counter, stock.symbol))
        counter += 1
    end_time = time.time()
    print("Execution time: {}".format(end_time - start_time))


create_data()
