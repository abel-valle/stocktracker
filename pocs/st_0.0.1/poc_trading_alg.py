# Import libraries
import pandas as pd
import numpy as np
import yfinance as yf
import investpy
import talib
import matplotlib.pyplot as plt
from datetime import datetime

plt.style.use('seaborn-notebook')

# Load data into dataframe
today = datetime.today().strftime('%d/%m/%Y')
# df = yf.download('NFLX', start='2020-01-01', end=today)
df = investpy.get_stock_historical_data(stock='NFLX',
                                        country='United States',
                                        from_date='01/01/2020',
                                        to_date=today)
df.reset_index(inplace=True)

# Set the date to be the index
df = df.set_index(pd.DatetimeIndex(df['Date'].values))

# Show the data
df

# Calculate MACD and MACD-Signal
df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['Close'])
df['cci'] = talib.CCI(df['High'], df['Low'], df['Close'], timeperiod=20)

# Plot the stock price, macd and cci
# plt.figure(figsize=(15, 14))
fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(15, 15))

# Precios
ax1.plot(df['Close'], label='Precio USD')
ax1.set_title('Histórico de precios')
ax1.set_xlabel('Fecha')
ax1.legend(loc='upper left')

# MACD
ax2.plot(df.index, df['macd'], label='MACD')
ax2.plot(df.index, df['macd_signal'], label='Signal', color='red')
ax2.legend(loc='upper left')
ax2.set_xlabel('Fecha')

# CCI
ax3.plot(df.index, df['cci'], label='CCI')
ax2.legend(loc='upper left')
ax2.set_xlabel('Fecha')


# Crossing MACD the Signal
def cross(signal, macd, close):
    buy = []
    sell = []
    for i in range(len(signal)):
        if (
                not (np.isnan(macd[i - 1]))
                and not (np.isnan(signal[i - 1]))
                and (macd[i] > signal[i]) != (macd[i - 1] > signal[i - 1])
        ):
            if ((macd[i] > signal[i]), (macd[i - 1] > signal[i - 1])) == (True, False):
                buy.append(close[i])
                sell.append(np.nan)
            else:
                sell.append(close[i])
                buy.append(np.nan)
        else:
            buy.append(np.nan)
            sell.append(np.nan)
    return buy, sell


# In[169]:


# Get MACD-Signal intersections
buy, sell = cross(df['macd_signal'], df['macd'], df['Close'])
# Add buy and sell columns
df['buy'] = buy
df['sell'] = sell

# Plot buy and sell signals
plt.figure(figsize=(15, 4.5))
plt.plot(df.index, df['buy'], label='Buy', color='green', marker='^', alpha=1)
plt.plot(df.index, df['sell'], label='Sell', color='red', marker='v', alpha=1)
plt.plot(df['Close'], label='Close Price', alpha=0.5)

plt.title('Close Price Buy & Sell Signals')
plt.xlabel('Date')
plt.xlabel('Close Price USD')
plt.legend(loc='upper left')
plt.show()

buy = df['buy']
sell = df['sell']
profit = 0
bought = False
buy_price = 0

for i in range(len(df['Close'])):

    if not (np.isnan(buy[i])):
        buy_price = buy[i]
        print('buy : ', buy[i])
        bought = True

    if bought and not (np.isnan(sell[i])):
        profit += sell[i] - buy_price
        print('sell: ', sell[i])
        print('prof: ', profit)
        print('---------------')
        buy_price = 0
        bought = False

print('Profit: ', profit)

df.to_csv('data/nflx_analysis.csv')
