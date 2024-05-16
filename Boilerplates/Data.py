from abc import ABC
from __future__ import print_function
import time
import upstox_client
from upstox_client.rest import ApiException
from pprint import pprint
import requests
from websocket.web_socket_data import fetch_market_data

class IData(ABC):
    def __init__(self):
        pass

    def get_market_quote():
        #to get current market price
        pass

    def get_historical_data():
        pass

    def get_market_feed():
        pass

class UpstocksDataClient(IData):
    def __init__(self, access_token):
        self.configuration = upstox_client.Configuration()
        self.configuration.access_token = access_token

    def get_market_quote(self, symbol, api_version):
        try:
            api_instance = upstox_client.MarketQuoteApi(upstox_client.ApiClient(upstox_client.Configuration()))
            api_response = api_instance.get_full_market_quote(symbol, api_version)
            return api_response
        except ApiException as e:
            print("Exception when calling MarketQuoteApi->get_market_quote: %s\n" % e)
            raise

    def get_historical_data(self, symbol, interval, to_date, api_version):
        try:
            api_instance = upstox_client.HistoryApi()
            api_response = api_instance.get_historical_candle_data(symbol, interval, to_date, api_version)
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling HistoryApi->get_historical_candle_data: %s\n" % e)

    def get_market_feed(self):
        #to use websocket
        # fetch_market_data()
        pass