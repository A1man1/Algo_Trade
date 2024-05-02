from abc import ABC

class IPortfolio(ABC):
    def __init__(self):
        self.holdings = {}

    def add_stock(self, symbol, quantity):
        pass

    def remove_stock(self, symbol, quantity):
        pass

    def get_portfolio(self):
        pass

class Portfolio(IPortfolio):
    def __init__(self):
        self.stocks = {}

    def add_stock(self, symbol, quantity):
        if symbol in self.stocks:
            self.stocks[symbol] += quantity
        else:
            self.stocks[symbol] = quantity

    def remove_stock(self, symbol, quantity):
        if symbol in self.stocks:
            if self.stocks[symbol] >= quantity:
                self.stocks[symbol] -= quantity
            else:
                print("Not enough stocks to sell.")
        else:
            print("You don't own this stock.")

    def get_portfolio(self):
        return self.stocks