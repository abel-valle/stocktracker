import pandas as pd
import numpy as np
import talib
import mysql.connector
from datetime import datetime
from mysql.connector import Error

# Global variables
input_folder = 'data/'
output_folder = 'data_proc/'
end_date = datetime.today().strftime('%d/%m/%Y')


# Function definitions
def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        # print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        if connection.is_connected():
            cursor.close()


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        if connection.is_connected():
            cursor.close()


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


# Update stock data from last record
def update_stock_data(symbol, record, profit, connection):
    price = record.iloc[0]['Close']
    date = record.iloc[0]['Date']
    buy = record.iloc[0]['buy']
    sell = record.iloc[0]['sell']
    status = 0

    if not (np.isnan(buy)):
        status = 1
    elif not (np.isnan(sell)):
        status = -1

    query = "update stocks set price={}, status={}, date='{}', profit_10k={} where symbol='{}'".format(price, status, date,
                                                                                                   profit, symbol)
    execute_query(connection, query)


# Calculate the profit of 1 stock
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


# Process script -------------------------------------------------------------------------------------------------------
'''
stock table columns
0: idstock
1: symbol
2: name
3: price
4: status
5: date
6: currency
7: profit
'''

connection = create_connection("localhost", "root", "admin", "stockdb")

query = "select * from stocks"
stocks = execute_read_query(connection, query)

col = 1
period = 1

i = 1
for stock in stocks:
    try:
        file_path = "{}{}_{}.csv".format(input_folder, stock[col], period)
        df = pd.read_csv(file_path)

        df.reset_index(inplace=True)

        # Set the date to be the index
        df = df.set_index(pd.DatetimeIndex(df['Date'].values))

        # Calculate MACD and MACD-Signal
        df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['Close'])
        df['cci'] = talib.CCI(df['High'], df['Low'], df['Close'], timeperiod=20)

        buy, sell = cross(df['macd_signal'], df['macd'], df['cci'], df['Close'])

        # Add buy and sell columns
        df['buy'] = buy
        df['sell'] = sell

        profit = calculate_profit(buy, sell)

        update_stock_data(stock[col], df[-1:], profit, connection)

        analyzed_file = "{}{}_proc_{}.csv".format(output_folder, stock[col], period)
        df.to_csv(analyzed_file)
        print("{}:{} processed".format(stock[0], stock[1]))
    except Exception as e:
        print(e)
    i += 1

connection.close()
print("MySQL connection is closed")
