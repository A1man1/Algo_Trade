from typing import List, Tuple
from pandas import Series
from core.base import Strategy
from core.model import PositionType, TradeType

class VWAP(Strategy):
    def __init__(self, order, quantity=1, short_ma_window=0, long_ma_window=100, threshold=0.01, transaction_fee=0.01, percent_close=0.2):
        super().__init__(order, quantity, short_ma_window, long_ma_window, threshold, transaction_fee, percent_close)
        self.holding = False

    def execute(self) -> Tuple[List[Tuple[TradeType, float, float]], float]:
        vwap = self.calculate()
        signals, total_profit = self.generate_signals(vwap)
        return signals, total_profit

    def calculate(self) -> Series:
        """
        Calculate Volume-Weighted Average Price (VWAP) for each row in the DataFrame.

        Returns:
            pandas Series: Series containing VWAP values corresponding to each row in the DataFrame.
        """
        # Calculate cumulative sum of price * volume
        self.order.data_frame['cumulative_pv'] = (
            self.order.data_frame['close'] * self.order.data_frame['volume']).cumsum()

        # Calculate cumulative sum of volume
        self.order.data_frame['cumulative_volume'] = self.order.data_frame['volume'].cumsum()

        # Calculate VWAP using rolling window
        self.order.data_frame['vwap'] = self.order.data_frame['cumulative_pv'] / self.order.data_frame['cumulative_volume']

        # Shift VWAP values by short_ma_window to align with current period
        self.order.data_frame['vwap'] = self.order.data_frame['vwap'].shift(self.short_ma_window)

        return self.order.data_frame['vwap']


    def generate_signals(self, vwap: Series) -> Tuple[List[Tuple[TradeType, float, float]], float]:
        """
        Generate buy/sell signals and calculate total profit based on VWAP.

        Args:
            vwap (Series): Series containing VWAP values.

        Returns:
            Tuple[List[Tuple[TradeType, float, float]], float]: Signals (buy/sell) and total profit.
        """
        signals = []

        for index, row in self.order.data_frame.iterrows():
            close_price = row['close']
            # Get VWAP value corresponding to the current row
            current_vwap = vwap.loc[index]
            # Determine trend type based on the relationship between close price and VWAP
            position_type = PositionType.LONG if close_price > current_vwap else PositionType.SHORT

            if not self.holding and close_price < current_vwap * (1 - self.threshold):
                # Buy signal
                exit_price = close_price * (1 + self.threshold)  # Calculate exit price dynamically
                stop_loss = close_price * (1 - self.threshold)  # Calculate stop-loss price dynamically

                self.order.open_position(entry_price=close_price, shares=self.quantity, tend_type=position_type, trade_type=TradeType.BUY, exit_price=exit_price, stop_loss=stop_loss)
                
                self.holding = True
                signals.append((TradeType.BUY, index, close_price, self.quantity))

            if self.holding and close_price > current_vwap * (1 + self.threshold):
                # Sell signal
                percent_profit = (close_price - self.order.positions[-1].entry_price) / self.order.positions[-1].entry_price
                self.order.close_position(position_to_close=self.order.positions[-1], percent=self.percent_close, current_price=close_price, trade_type=TradeType.SELL)  # set close
                self.order.total_profit += percent_profit
                self.holding = False
                signals.append((TradeType.SELL, index, close_price, self.quantity))
                

        return signals, self.order.total_profit
