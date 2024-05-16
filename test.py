import pandas as pd
import requests

from core import AlgoTrade , settings

# import pandas_datareader as pdr
# import datetime 
# aapl = pdr.get_data_yahoo('AAPL', 
#                           start=datetime.datetime(2012, 1, 1), 
#                           end=datetime.datetime(2012, 10, 1))

# import quandl 
# aapl = quandl.get("WIKI/AAPL", start_date="2006-10-01", end_date="2012-01-01")
# Create AlgoTrade instance
# trade = AlgoTrade(settings.api_url,settings.symbol,settings.interval,settings.apikey, stock_name='Apple',strategy_types= [settings.VWAP], quantity=2)

# data = aapl #pd.read_csv('data.csv')
# data.columns = [i.lower() for i in data.columns]
# #print(data.columns)
# data['timestamp']= pd.to_datetime(data.index, format="%m/%d/%Y")
# # Remove commas and convert Volume to integer
# # data["volume"] = data["volume"].apply(lambda x: x.replace(",", ""))
# # print(data['volume'])
# data['volume'] = data['volume'].apply(int)
# data[['open', 'high', 'low', 'close', 'volume']] = data[['open', 'high', 'low', 'close','volume']].astype(float)


from nsepython import *
import datetime
import pandasql as pd

end_date = datetime.datetime.now().strftime("%d-%m-%Y")
end_date = str(end_date)

start_date = (datetime.datetime.now()- datetime.timedelta(days=65)).strftime("%d-%m-%Y")
start_date = str(start_date)

symbol = "GODREJIND"
series = "EQ"

df = equity_history(symbol,series,start_date,end_date)
data =pd.sqldf("select CH_TIMESTAMP as timestamp , CH_OPENING_PRICE as open ,CH_TRADE_HIGH_PRICE as high , CH_TRADE_LOW_PRICE as low ,CH_TOT_TRADED_VAL as volume , CH_CLOSING_PRICE as close from  df ", locals())
data['volume'] = data['volume'].apply(int)
data[['open', 'high', 'low', 'close', 'volume']] = data[['open', 'high', 'low', 'close','volume']].astype(float)

trade = AlgoTrade(stock_name='GODREJIND',data_frame=data,from_dataframe=True,strategy_types= [settings.VWAP], quantity=1)


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

