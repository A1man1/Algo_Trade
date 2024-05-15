from typing import Tuple, List, Optional

from pandas import Series, DataFrame

from core.base import IOrder
from core.portfolio import Portfolio


class OrderSub(IOrder):
    def __init__(self,*args,**kwargs):
        super(OrderSub, self).__init__(*args, **kwargs)
        

    def place_order(self, processed_data: Optional[Series | DataFrame]) -> Tuple[List[Tuple[str, float, float]], float]:
        """
        Generate buy/sell signals and calculate total profit based on Processed data.

        Args:
            Processed data (Series): Series containing Processed data values.

        Returns:
            Tuple[List[Tuple[str, float, float]], float]: Signals (buy/sell) and total profit.
        """
        order_history =[] 
        for trade_type, index, close_price, quantity in processed_data[0]:
            order_history.append({"symbol": self.symbol, "quantity": quantity,
                                      "order_type": trade_type, 'closed_price': close_price, 'index': index})
        
        self.order_history.extend(order_history)
        return order_history


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
    
class Order(Portfolio,OrderSub):
    def __init__(self,*args, **kwargs):
        self.order_history = []
        self.symbol = self.stock_name
        super(Order, self).__init__(*args, **kwargs)
        