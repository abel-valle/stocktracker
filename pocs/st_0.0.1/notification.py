import boto3
import mysql.connector
from datetime import datetime
from mysql.connector import Error

# Global variables
end_date = datetime.today().strftime('%Y-%m-%d')
end_date = '2021-05-20'

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

connection = create_connection("localhost", "root", "admin", "stockdb")

# Create an SNS client
client = boto3.client(
    "sns",
    aws_access_key_id="",
    aws_secret_access_key="",
    region_name=""
)


query = """
select u.iduser,
    u.name as uname,
    u.email,
    u.phone,
    u.country_code,
    s.idstock,
    s.symbol,
    s.name as sname,
    s.price,
    s.status,
    s.date
from users u, stocks s, user_stocks us
where u.iduser = us.iduser
and s.idstock = us.idstock
and s.status <> 0
and s.date = '{}'
""".format(end_date)

try:
    notifications = execute_read_query(connection, query)

    # Send sms message
    for notification in notifications:
        uname = notification[1]
        phone = notification[3]
        code = notification[4]
        symbol = notification[6]
        sname = notification[7]
        price = notification[8]
        status = notification[9]

        phone_num = "+" + code + phone
        action = ""

        if status == 1:
            action = 'COMPRA'
        elif status == -1:
            action = 'VENDE'

        message = "StockTracker te sugiere: {} [{}] {}, al precio ${}".format(action, symbol, sname, price)

        client.publish(
            PhoneNumber=phone_num,
            Message=message
        )
except Error as e:
    print(f"The error '{e}' occurred")

connection.close()
print("MySQL connection is closed")
