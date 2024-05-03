from abc import ABC
import Portfolio
class IOrder:
    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.order_history = []

    def place_order(self, symbol, quantity, order_type):
        pass

    def modify_order(self, order_id, new_quantity):
        pass

    def cancel_order(self, order_id):
        pass

    def get_order_history(self):
        return self.order_history
    

class Order:
    def __init__(self, portfolio : Portfolio ):
        self.portfolio = portfolio
        self.order_history = []

    def place_order(self, symbol, quantity, order_type):
        if order_type == "buy":
            self.portfolio.add_stock(symbol, quantity)

            self.order_history.append({"symbol": symbol, "quantity": quantity, "order_type": order_type})
        elif order_type == "sell":
            self.portfolio.remove_stock(symbol, quantity)
            self.order_history.append({"symbol": symbol, "quantity": quantity, "order_type": order_type})
        else:
            print("Invalid order type.")

    def modify_order(self, symbol, quantity, order_type):
        for order in self.order_history:
            if order["symbol"] == symbol and order["order_type"] == order_type:
                order["quantity"] = quantity
                break
        else:
            print("Order not found.")

    def cancel_order(self, symbol, quantity, order_type):
        for order in self.order_history:
            if order["symbol"] == symbol and order["quantity"] == quantity and order["order_type"] == order_type:
                self.order_history.remove(order)
                break
        else:
            print("Order not found.")

    def get_order_history(self):
        return self.order_history