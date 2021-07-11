# Imports
import pandas as pd
from pymongo import MongoClient

# Connect to MongoDB
MONGO_URI = 'mongodb://localhost'
client = MongoClient(MONGO_URI)

db = client['stockhistdb']
db.drop_collection(name_or_collection='stock')

collection = db['stock']

# Load csv dataset
df = pd.read_csv('data/AAPL_1.csv')
df.reset_index(inplace=True)
del df['index']
df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'currency']
df.insert(1, 'symbol', 'AAPL')
df_dict = df.to_dict('records')
collection.insert_many(df_dict)

