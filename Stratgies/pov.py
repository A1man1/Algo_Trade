from typing import List, Tuple
import pandas as pd
from core.base import Strategy
from core.model import PositionType, TradeType


class POV(Strategy):
    def __init__(self, order, quantity=1, short_ma_window=0, long_ma_window=100, threshold=0.01, transaction_fee=0.01, percent_close=0.2):
        super().__init__(order, quantity, short_ma_window, long_ma_window, threshold, transaction_fee, percent_close)
        self.holding = False

    def execute(self) -> Tuple[List[Tuple[str, float, float]], float]:
        pov = self.calculate()
        signals, total_profit = self.generate_signals(pov)
        return signals, total_profit

    def calculate(self) -> pd.Series:
        """
        Calculate Percentage of Volume (POV) for each row in the DataFrame.

        Returns:
            pandas Series: Series containing POV values corresponding to each row in the DataFrame.
        """
        # Calculate cumulative sum of volume
        self.order.data_frame['cumulative_volume'] = self.order.data_frame['volume'].cumsum()

        # Calculate POV using vectorized operations
        self.order.data_frame['pov'] = self.order.data_frame['volume'] / self.order.data_frame['cumulative_volume']
        self.order.data_frame['pov'] = self.order.data_frame['pov'].rolling(window=self.short_ma_window).mean()

        return self.order.data_frame['pov']

    def generate_signals(self, pov: pd.Series) -> Tuple[List[Tuple[str, float, float]], float]:
        """
        Generate buy/sell signals and calculate total profit based on POV.

        Args:
            pov (pd.Series): Series containing POV values.

        Returns:
            Tuple[List[Tuple[str, float, float]], float]: Signals (buy/sell) and total profit.
        """
        signals = []

        for index, row in self.order.data_frame.iterrows():
            close_price = row['close']
            current_pov = pov.loc[index]
            volume = row['volume']

            position_type = PositionType.LONG if close_price > current_pov else PositionType.SHORT

            if not self.holding and volume > current_pov:
                # Buy signal
                self.open_position_and_record_trade(close_price, position_type, TradeType.BUY)
                self.holding = True
                signals.append(('buy', index, close_price, self.quantity))

            if self.holding and volume < current_pov:
                # Sell signal
                self.close_position_and_record_trade(close_price)
                self.holding = False
                signals.append(('sell', index, close_price, self.quantity))

        return signals, self.order.total_profit

    def open_position_and_record_trade(self, price: float, position_type: PositionType, trade_type: TradeType):
        """
        Open a position in the portfolio and record the trade.

        Args:
            price (float): The price at which the position is opened.
            position_type (PositionType): The type of position (LONG or SHORT).
            trade_type (TradeType): The type of trade (BUY or SELL).
        """
        exit_price = price * (1 + self.threshold)  # Calculate exit price dynamically
        stop_loss = price * (1 - self.threshold)  # Calculate stop-loss price dynamically
        self.order.open_position(entry_price=price, shares=self.quantity, tend_type=position_type, trade_type=trade_type, exit_price=exit_price, stop_loss=stop_loss)

    def close_position_and_record_trade(self, current_price:float):
            """
            Close a position in the portfolio and record the trade.

            Args:
                price (float): The price at which the position is closed.
                trade_type (TradeType): The type of trade (BUY or SELL).
                current_price (float): The current price of the asset.
                percent (float): The percentage used to calculate profit/loss.
            """
            self.order.close_position(position_to_close=self.order.positions[-1], percent=self.percent_close, current_price=current_price, trade_type=TradeType.SELL)  # set close

