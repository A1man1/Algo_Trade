#builtin imports
from typing import Optional , List
import requests

# third party imports
import pandas as pd
from pandas import DataFrame

#imports from modules
from core.base import IPortfolio , Position , Trade

    
class Portfolio(IPortfolio):

    def __init__(self, url=None, stock_name=None, interval=None, api_key=None, outputsize="compact",
                 function_type='TIME_SERIES_INTRADAY', data_frame:Optional[pd.DataFrame]=None, from_dataframe=False):
        
        self.trades: List[Trade] = []
        self.positions: List[Position] = []
        self.total_profit: float = 0
        self.data_frame= None
        
        if from_dataframe:
            if not data_frame.empty:
                self.data_frame = data_frame
                self.stock_name = self.stock_name
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
            if not data:
                raise ValueError("Given url isn't working")
            
            df = pd.DataFrame(data).T.reset_index()
            df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
            return df
        else:
            raise ValueError(f"Error fetching data from API: {response.text}")

    def open_position(self, shares: int, entry_price: float, trade_type: str, tend_type:str, stop_loss, exit_price):
        """
        Open a new position in the portfolio.

        Args:
            shares (int): Quantity of the asset.
            entry_price (float): Entry price of the asset.
            trade_type (str): Type of trade (buy/sell).
        """
        # Create a new Position object
        position = Position(
            stock_name=self.stock_name,
            number=len(self.positions) + 1,
            entry_price=entry_price,
            shares=shares,
            type_tends=tend_type,
            exit_price=exit_price,
            stop_loss=stop_loss
        )
        self.positions.append(position)
        position.show()  # Display position details

        # Log the trade
        trade = Trade(
            stock_name=self.stock_name,
            quantity=shares,
            price=entry_price,
            trade_type=trade_type
        )
        self.trades.append(trade)
        

    def close_position(self, position_to_close: 'Position', current_price: float, percent: float,trade_type:str):
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
            
            profit_loss = (entry_price - current_price) * position_to_close.shares
            position_to_close.profit_loss = profit_loss
            
            # Log the trade
            trade = Trade(
                stock_name=position_to_close.stock_name,
                quantity=quantity_to_close,
                price=current_price,
                trade_type=trade_type
            )
            self.trades.append(trade)

        # This part of the code is checking if the shares of a particular position have reached zero
        # or less. If the shares have reached zero or less, it means that the entire position has been
        # closed (all shares have been sold). In that case, the position is removed from the list of
        # positions in the portfolio using `self.positions.remove(position_to_close)`. This ensures
        # that closed positions are no longer included in the list of active positions within the
        # portfolio.
            # If the entire position is closed, remove it from the portfolio
            if position_to_close.shares <= 0:
                self.positions.remove(position_to_close)


