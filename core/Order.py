from typing import Tuple, List
import pandas as pd
from pandas import Series

from core import IOrder , Portfolio, settings
from Stratgies import MeanReversion, VWAP


    

class Order(IOrder, Portfolio):
    def __init__(self):
        self.order_history = []
        self.symbol = self.stock_name
       

    def place_order(self, processed_data: Series, threshold, quantity) -> Tuple[List[Tuple[str, float, float]], float]:
        """
        Generate buy/sell signals and calculate total profit based on Processed data.

        Args:
            Processed data (Series): Series containing Processed data values.

        Returns:
            Tuple[List[Tuple[str, float, float]], float]: Signals (buy/sell) and total profit.
        """
    
        holding = False
        entry_price = None
        total_profit = 0

        for index, row in self.data_frame.iterrows():
            close_price = row['close']
            current_vwap = processed_data.loc[index]  # Get processed data value corresponding to the current row

            if not holding and close_price < current_vwap * (1 - threshold):
                # Buy signal
                self.open_position(entry_price=close_price, shares=quantity)
                entry_price = close_price
                holding = True
                self.order_history.append({"quantity": quantity, "order_type": 'buy', "index":index, "close_price":close_price})
                

            if holding and close_price > current_vwap * (1 + threshold):
                # Sell signal
                percent_profit = (close_price - self.positions[-1].entry_price) / entry_price
                self.close_position(position_to_close=self.positions[-1],percent=0.2,current_price=close_price) #set close 
                total_profit += percent_profit
                holding = False
                self.order_history.append({"quantity": quantity, "order_type": 'sell', "index":index, "close_price":close_price})

        self.total_profit = total_profit  # Update total profit attribute in portfolio

        return self.order_history, self.total_profit


    def modify_order(self, quantity, order_type):
        for order in self.order_history:
            if order["order_type"] == order_type:
                order["quantity"] = quantity
                break
        else:
            print("Order not found.")


    def cancel_order(self, quantity, order_type, close_price):
        for order in self.order_history:
            if order["quantity"] == quantity and order["order_type"] == order_type and order["close_price"] == close_price:
                self.order_history.remove(order)
                break
        else:
            print("Order not found.")


    def get_order_history(self):
        return self.order_history