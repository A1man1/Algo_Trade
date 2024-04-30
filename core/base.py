from pydantic import BaseModel
from typing import List, Tuple , Optional
from pandas import DataFrame
import pandas as pd
import requests
from abc import ABC, abstractmethod
from core import log

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


class Portfolio:

    def __init__(self, url=None, stock_name=None, interval=None, api_key=None, outputsize="compact",
                 function_type='TIME_SERIES_INTRADAY', data_frame:Optional[DataFrame]=None, from_dataframe = False):
        
        self.trades: List[Trade] = []
        self.positions: List[Position] = []
        self.total_profit: float = 0
        self.data_frame= None
        
        if from_dataframe:
            if not data_frame.empty:
                self.data_frame = data_frame
                self.stock_name = 'APPle'
            else:
                raise ValueError('"Need DataFrame"') 
        elif url:
            # Modified this line
            self.api_key = api_key
            self.url = url
            self.function = function_type
            self.stock_name = stock_name
            self.interval = interval
            self.output_size = outputsize
            self.data_frame = self.fetch_data_from_api()
        else:
            raise ValueError('"Need url"') 
            

    def fetch_data_from_api(self) -> pd.DataFrame:
        """
        Fetch historical price data from an API URL and return as a DataFrame.
        """
        params = {
            "function": self.function,
            "symbol": self.stock_name,
            "interval": self.interval,
            "apikey": self.api_key,
            "outputsize": self.output_size
        }

        response = requests.get(self.url, params=params)
        if response.status_code == 200:
            data = response.json().get(f"Time Series ({self.interval})", {})
            print(data)
            if not data:
                raise ValueError("Given url isn't working")
            
            df = DataFrame(data).T.reset_index()
            df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
            return df
        else:
            raise ValueError(f"Error fetching data from API: {response.text}")

    def open_position(self, shares: int, entry_price: float):
        """
        Open a new position in the portfolio.

        Args:
            quantity (int): Quantity of the asset.
            entry_price (float): Entry price of the asset.
        """
        # Create a new Position object
        position = Position(stock_name=self.stock_name, number=len(self.positions) + 1, entry_price=entry_price,
                            shares=shares, type_='long')
        self.positions.append(position)
        position.show()  # Display position details

    def close_position(self, position_to_close: Position, current_price: float, percent: float):
        """
        Close a position in the portfolio.

        Args:
            position_to_close (Position): The position object to be closed.
            current_price (float): The current price of the asset.
        """
        if position_to_close:
        # Calculate the quantity to close based on the specified percentage
            quantity_to_close = int(position_to_close.shares * percent)

            # Calculate profit/loss based on current price
            entry_price = position_to_close.entry_price
            profit_loss = (current_price - entry_price) * quantity_to_close
            position_to_close.profit_loss = profit_loss

            # Remove quantity_to_close from the position
            position_to_close.shares -= quantity_to_close

            # Log the trade
            trade = Trade(stock_name=position_to_close.stock_name, quantity=quantity_to_close, price=current_price,
                        trade_type='long')
            self.trades.append(trade)

            # If the entire position is closed, remove it from the portfolio
            if position_to_close.shares <= 0:
                self.positions.remove(position_to_close)


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

