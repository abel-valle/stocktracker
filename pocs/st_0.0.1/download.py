import investpy
import mysql.connector
from datetime import datetime
from mysql.connector import Error

# Global variables
folder = 'data/'
ini_date = '01/01/2019'
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
        print("Query executed successfully")
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
        df = investpy.get_stock_historical_data(stock=stock[col],
                                                country='mexico',
                                                from_date=ini_date,
                                                to_date=end_date)
        file_path = "{}{}_{}.csv".format(folder, stock[col], period)
        df.to_csv(file_path)
        print('Stock ', i, ':', stock[col], 'downloaded')
    except:
        print('Stock ', stock[col], ' not found')
    i += 1

connection.close()
print("MySQL connection is closed")
