from pydantic import BaseModel
from typing import List, Tuple , Optional
from pandas import DataFrame
import pandas as pd
import requests
from abc import ABC, abstractmethod
from core import log
import Portfolio

class Trade(BaseModel):
    stock_name: str
    quantity: int
    price: float
    trade_type: str  # 'buy' or 'sell'

    def calculate_cost(self) -> float:
        return self.quantity * self.price

    def __str__(self) -> str:
        return f"Trade: {self.stock_name} - {self.trade_type} {self.quantity} shares at ${self.price:.2f} each"


class Position(BaseModel):
    number: int
    entry_price: float
    shares: float
    stock_name: str
    exit_price: float = 0
    profit_loss: float = 0
    stop_loss: float = 0
    type_: str
    

    def show(self):
        print(f"No. {self.number}")
        print(f"Type: {self.type_}")
        print(f"Entry: {self.entry_price}")
        print(f"Shares: {self.shares}")
        print(f"Exit: {self.exit_price}")
        print(f"Stop: {self.stop_loss}\n")

    def __str__(self) -> str:
        return f"{self.type_} {self.shares}x{self.entry_price}"


class IOrder (ABC):
    def __init__(self, strategy_types: Optional[List[str]]):
        self.strategy_types = strategy_types
        self.order_history = []
    
    @abstractmethod
    def place_order(self, symbol, quantity, order_type):
        pass

    @abstractmethod
    def modify_order(self, order_id, new_quantity):
        pass

    @abstractmethod
    def cancel_order(self, order_id):
        pass

    @abstractmethod
    def get_order_history(self):
        return self.order_history
    
    @abstractmethod
    def set_strategy(self):
        pass


class IPortfolio(ABC):
    def __init__(self):
        self.holdings = {}

    @abstractmethod
    def open_position(self, symbol, quantity):
        pass

    @abstractmethod
    def close_position(self, symbol, quantity):
        pass

    @abstractmethod
    def get_portfolio(self):
        pass


class Strategy(ABC):
    def __init__(self, portfolio: Portfolio, short_ma_window=0, long_ma_window=100, threshold=0.01,
                 transaction_fee=0.01):
        self.portfolio = portfolio
        self.short_ma_window = short_ma_window
        self.long_ma_window = long_ma_window
        self.threshold = threshold
        self.transaction_fee = transaction_fee

    @abstractmethod
    def execute(self) -> Tuple[List[Tuple[str, float, float]], float]:
        pass

