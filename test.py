import pandas as pd
import requests

from core import AlgoTrade , settings

# import pandas_datareader as pdr
# import datetime 
# aapl = pdr.get_data_yahoo('AAPL', 
#                           start=datetime.datetime(2012, 1, 1), 
#                           end=datetime.datetime(2012, 10, 1))

import quandl 
aapl = quandl.get("WIKI/AAPL", start_date="2006-10-01", end_date="2012-01-01")
# Create AlgoTrade instance
#trade = AlgoTrade(settings.api_url,settings.symbol,settings.interval,settings.apikey)

data = aapl #pd.read_csv('data.csv')
data.columns = [i.lower() for i in data.columns]
#print(data.columns)
data['timestamp']= pd.to_datetime(data.index, format="%m/%d/%Y")
# Remove commas and convert Volume to integer
# data["volume"] = data["volume"].apply(lambda x: x.replace(",", ""))
# print(data['volume'])
data['volume'] = data['volume'].apply(int)
data[['open', 'high', 'low', 'close', 'volume']] = data[['open', 'high', 'low', 'close','volume']].astype(float)


trade = AlgoTrade(stock_name='Apple',data_frame=data,from_dataframe=True,strategy_types= [settings.VWAP], quantity=2)


# portfolio = Portfolio(data_frame=data,stock_name=symbol)
# print(settings.MEAN_REVISION)
orders = trade.execute_trade()
# Print results
print(orders)


# for timestamp, profit, close_price in sell_signals[0]:
#      print(f"Timestamp: {timestamp}, Profit: ${profit:.2f}, Close Price: ${close_price:.2f}")

# print('vwap')

# sell_signals =trade.execute_trade()
# print(sell_signals)

# # Print remaining positions in the portfolio
# print("\nRemaining positions in the portfolio:")
# for position in trade.positions:
#     position.show()

