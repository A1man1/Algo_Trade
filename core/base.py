from pydantic import BaseModel 
from typing import List, Tuple, Optional
from abc import ABC, abstractmethod
from pandas import Series, DataFrame

from core.model import TradeType , PositionType


class Trade(BaseModel):
    stock_name: str
    quantity: int
    price: float
    trade_type: TradeType  # 'buy' or 'sell'

    def calculate_cost(self) -> float:
        return self.quantity * self.price

    def __str__(self) -> str:
        return f"Trade: {self.stock_name} - {self.trade_type} {self.quantity} shares at ${self.price:.2f} each"


class Position(BaseModel):
    number: int
    entry_price: float
    shares: float # The number of shares in the position.
    stock_name: str # A string representing the name of the stock.
    exit_price: float = 0  # price at which the position was exited (defaulted to 0).
    profit_loss: float = 0 # profit or loss incurred in the position (defaulted to 0).
    stop_loss: float = 0  # stop loss price for the position (defaulted to 0).
    type_tends: PositionType  #type of position (long or short).

    def show(self):
        print(f"No. {self.number}")
        print(f"stock {self.stock_name}")
        print(f"Type: {self.type_tends}")
        print(f"Entry: {self.entry_price}")
        print(f"Shares: {self.shares}")
        print(f"Exit: {self.exit_price}")
        print(f"Stop: {self.stop_loss}")
        print(f"profit_loss: {self.profit_loss}\n")

    def __str__(self) -> str:
        return f"{self.type_tends} {self.shares}x{self.entry_price}"


class IOrder (ABC):
    def __init__(self):
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

    # @abstractmethod
    # def get_portfolio(self):
    #     pass


class Strategy(ABC):
    def __init__(self, order:IOrder,quantity,short_ma_window=0, long_ma_window=100, threshold=0.01,
                 transaction_fee=0.01,percent_close=0.2):
        self.quantity=quantity
        self.order = order
        #self.stop_loss= stop_loss
        self.short_ma_window = short_ma_window
        self.long_ma_window = long_ma_window
        self.threshold = threshold
        self.transaction_fee = transaction_fee
        self.percent_close=percent_close

    @abstractmethod
    def calculate(self) -> Optional[DataFrame | Series]:
        pass

    @abstractmethod
    def generate_signals(self) -> Tuple[List[Tuple[str, float, float]], float]:
        pass

    @abstractmethod
    def execute(self) -> Optional[Tuple[List[Tuple[str, float, float]], float] | None]:
        pass

