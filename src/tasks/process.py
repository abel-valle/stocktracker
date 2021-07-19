import time
import investpy
import talib
import numpy as np
import pandas as pd
import operator

from datetime import datetime
from pymongo import MongoClient

INI_DATE = '01/01/2020'
# END_DATE = '02/07/2021'
END_DATE = datetime.today().strftime('%d/%m/%Y')
COUNTRY = 'mexico'

MONGO_URI = 'mongodb://localhost'
client = MongoClient(MONGO_URI)
db = client['stockdb']

db.drop_collection(name_or_collection='stock')
db.drop_collection(name_or_collection='history')
stocks = db['stock']
history = db['history']


# Crossing MACD the Signal
def cross_macd(macd, signal, close):
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


# Crossing MACD the Signal MOD
def cross_macd_mod(macd, signal, cci, close):
    buy = []
    sell = []
    last_status = None
    for i in range(len(signal)):
        if (
                not (np.isnan(macd[i - 1]))
                and not (np.isnan(signal[i - 1]))
                and (macd[i] > signal[i]) != (macd[i - 1] > signal[i - 1])
        ):
            if macd[i] > signal[i] and not (macd[i - 1] > signal[i - 1]) and cci[i] < -50 and last_status != 'buy':
                buy.append(close[i])
                sell.append(np.nan)
                last_status = 'buy'
            elif last_status != 'sell':
                sell.append(close[i])
                buy.append(np.nan)
                last_status = 'sell'
            else:
                buy.append(np.nan)
                sell.append(np.nan)
        else:
            buy.append(np.nan)
            sell.append(np.nan)
    return buy, sell


# Crossing CCI
def cross_cci(cci, low, max, close):
    buy = []
    sell = []
    last_status = None
    for i in range(len(cci)):
        if not (np.isnan(cci[i - 1])):
            if cci[i - 1] < low < cci[i] and last_status != 'buy':
                buy.append(close[i])
                sell.append(np.nan)
                last_status = 'buy'
            elif cci[i - 1] > max > cci[i] and last_status != 'sell':
                sell.append(close[i])
                buy.append(np.nan)
                last_status = 'sell'
            else:
                buy.append(np.nan)
                sell.append(np.nan)
        else:
            buy.append(np.nan)
            sell.append(np.nan)
    return buy, sell


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


def create_stock_info():
    stock_list = investpy.stocks.get_stocks_dict(COUNTRY)
    stocks.insert_many(stock_list)
    print('{} stock symbols saved.'.format(len(stock_list)))
    updated = stocks.update_many({}, {'$set': {
        'history': False,
        'date': None,
        'price': np.nan
    }})
    print('{} documents updated.'.format(updated.modified_count))


def create_stock_tech_indicators():
    stock_list = investpy.stocks.get_stocks_dict(COUNTRY)
    stocks.insert_many(stock_list)
    print('{} stock symbols saved.'.format(len(stock_list)))
    updated = stocks.update_many({}, {'$set': {
        'history': False,
        'date': None,
        'price': np.nan
    }})
    print('{} documents updated.'.format(updated.modified_count))


def create_stock_history():
    stock_list = stocks.find()
    print(type(stock_list))
    counter = 1
    start_time = time.time()
    end_time = None

    for stock_info in stock_list:
        symbol = stock_info['symbol']
        try:
            df = investpy.get_stock_historical_data(stock=symbol, country=COUNTRY, from_date=INI_DATE,
                                                    to_date=END_DATE, interval='Daily')
            df.reset_index(inplace=True)
            # Rename columns.
            df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'currency']
            # Add columns.
            df.insert(1, 'symbol', symbol)

            # Set the date to be the index
            df = df.set_index(pd.DatetimeIndex(df['date'].values))

            # Calculate MACD and MACD-Signal
            df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['close'])
            df['cci'] = talib.CCI(df['high'], df['low'], df['close'], timeperiod=20)

            buy_macd, sell_macd = cross_macd(df['macd'], df['macd_signal'], df['close'])
            buy_macdmod, sell_macdmod = cross_macd_mod(df['macd'], df['macd_signal'], df['cci'], df['close'])
            buy_cci, sell_cci = cross_cci(df['cci'], -100, 100, df['close'])
            buy_cci90, sell_cci90 = cross_cci(df['cci'], -90, 100, df['close'])

            # Add buy and sell columns
            df['buy_macd'] = buy_macd
            df['sell_macd'] = sell_macd
            df['buy_macdmod'] = buy_macdmod
            df['sell_macdmod'] = sell_macdmod
            df['buy_cci'] = buy_cci
            df['sell_cci'] = sell_cci
            df['buy_cci90'] = buy_cci90
            df['sell_cci90'] = sell_cci90

            macd_profit = calculate_profit(buy_macd, sell_macd)
            macdmod_profit = calculate_profit(buy_macdmod, sell_macdmod)
            cci_profit = calculate_profit(buy_cci, sell_cci)
            cci90_profit = calculate_profit(buy_cci90, sell_cci90)

            df_dict = df.to_dict('records')
            history.insert_many(df_dict)

            price = df[-1:].iloc[0]['close']
            date = df[-1:].iloc[0]['date']

            macd_is_buy = df[-1:].iloc[0]['buy_macd']
            macd_is_sell = df[-1:].iloc[0]['sell_macd']
            macdmod_is_buy = df[-1:].iloc[0]['buy_macdmod']
            macdmod_is_sell = df[-1:].iloc[0]['sell_macdmod']
            cci_is_buy = df[-1:].iloc[0]['buy_cci']
            cci_is_sell = df[-1:].iloc[0]['sell_cci']
            cci90_is_buy = df[-1:].iloc[0]['buy_cci90']
            cci90_is_sell = df[-1:].iloc[0]['sell_cci90']

            macd_trade = 'none'
            macdmod_trade = 'none'
            cci_trade = 'none'
            cci90_trade = 'none'

            if not (np.isnan(macd_is_buy)):
                macd_trade = 'buy'
            elif not (np.isnan(macd_is_sell)):
                macd_trade = 'sell'

            if not (np.isnan(macdmod_is_buy)):
                macdmod_trade = 'buy'
            elif not (np.isnan(macdmod_is_sell)):
                macdmod_trade = 'sell'

            if not (np.isnan(cci_is_buy)):
                cci_trade = 'buy'
            elif not (np.isnan(cci_is_sell)):
                cci_trade = 'sell'

            if not (np.isnan(cci90_is_buy)):
                cci90_trade = 'buy'
            elif not (np.isnan(cci90_is_sell)):
                cci90_trade = 'sell'

            profit_list = [macd_profit, macdmod_profit, cci_profit, cci90_profit]
            index, value = max(enumerate(profit_list), key=operator.itemgetter(1))

            if index == 0:
                win_strategy = 'macd'
            if index == 1:
                win_strategy = 'macdmod'
            if index == 2:
                win_strategy = 'cci'
            if index == 3:
                win_strategy = 'cci90'

            # To get the technical indicators.
            df_tech = investpy.technical_indicators(name=symbol, country='mexico', product_type='stock',
                                                    interval='daily')
            rsi_14 = None
            stoch_9_6 = None
            stochrsi_14 = None
            macd_12_26 = None
            adx_14 = None
            williams_r = None
            cci_14 = None
            atr_14 = None
            highs_lows_14 = None
            ult_oscillator = None
            roc = None
            bull_bear_pow_13 = None

            for i in df_tech.index:
                technical_indicator = df_tech['technical_indicator'][i]
                value = df_tech['value'][i]
                signal = df_tech['signal'][i]
                if technical_indicator == 'RSI(14)':
                    rsi_14 = signal
                if technical_indicator == 'STOCH(9,6)':
                    stoch_9_6 = signal
                if technical_indicator == 'STOCHRSI(14)':
                    stochrsi_14 = signal
                if technical_indicator == 'MACD(12,26)':
                    macd_12_26 = signal
                if technical_indicator == 'ADX(14)':
                    adx_14 = signal
                if technical_indicator == 'Williams %R':
                    williams_r = signal
                if technical_indicator == 'CCI(14)':
                    cci_14 = signal
                if technical_indicator == 'ATR(14)':
                    atr_14 = signal
                if technical_indicator == 'Highs/Lows(14)':
                    highs_lows_14 = signal
                if technical_indicator == 'Ultimate Oscillator':
                    ult_oscillator = signal
                if technical_indicator == 'ROC':
                    roc = signal
                if technical_indicator == 'Bull/Bear Power(13)':
                    bull_bear_pow_13 = signal

            stocks.update_one({'symbol': symbol}, {'$set': {
                'history': True,
                'date': date,
                'price': price,
                'macd_trade': macd_trade,
                'macd_profit': macd_profit,
                'macdmod_trade': macdmod_trade,
                'macdmod_profit': macdmod_profit,
                'cci_trade': cci_trade,
                'cci_profit': cci_profit,
                'cci90_trade': cci90_trade,
                'cci90_profit': cci90_profit,
                'win_strategy': win_strategy,
                't_rsi_14': rsi_14,
                't_stoch_9_6': stoch_9_6,
                't_stochrsi_14': stochrsi_14,
                't_macd_12_26': macd_12_26,
                't_adx_14': adx_14,
                't_williams_r': williams_r,
                't_cci_14': cci_14,
                't_atr_14': atr_14,
                't_highs_lows_14': highs_lows_14,
                't_ult_oscillator': ult_oscillator,
                't_roc': roc,
                't_bull_bear_pow_13': bull_bear_pow_13
            }})
            print('{} Symbol {} processed and saved.'.format(counter, symbol))
        except Exception as e:
            print("{} Symbol {} history not found.".format(counter, symbol))
            print(type(e))
            print(e.args)
        counter += 1

    end_time = time.time()
    print("Execution time: {}".format(end_time - start_time))


create_stock_info()
create_stock_history()
