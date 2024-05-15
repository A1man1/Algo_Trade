from typing import List, Tuple
from pandas import Series
from core.base import  Strategy


class VWAP(Strategy):
    def __init__(self, order, quantity=1, short_ma_window=0, long_ma_window=100, threshold=0.01, transaction_fee=0.01):
        super().__init__(order,quantity, short_ma_window, long_ma_window, threshold, transaction_fee)

    def execute(self) -> Tuple[List[Tuple[str, float, float]], float]:
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
        self.order.data_frame['cumulative_volume'] = self.order.data_frame['volume'].cumsum(
        )

        # Calculate VWAP using rolling window
        self.order.data_frame['vwap'] = self.order.data_frame['cumulative_pv'] / \
            self.order.data_frame['cumulative_volume']

        # Shift VWAP values by short_ma_window to align with current period
        self.order.data_frame['vwap'] = self.order.data_frame['vwap'].shift(
            self.short_ma_window)

        return self.order.data_frame['vwap']


    def generate_signals(self, vwap: Series) -> Tuple[List[Tuple[str, float, float]], float]:
        """
        Generate buy/sell signals and calculate total profit based on VWAP.

        Args:
            vwap (Series): Series containing VWAP values.

        Returns:
            Tuple[List[Tuple[str, float, float]], float]: Signals (buy/sell) and total profit.
        """
        signals = []
        holding = False
        entry_price = None
        total_profit = 0
        
        print(self.order.data_frame)

        for index, row in self.order.data_frame.iterrows():
            close_price = row['close']
            # Get VWAP value corresponding to the current row
            current_vwap = vwap.loc[index]

            if not holding and close_price < current_vwap * (1 - self.threshold):
                # Buy signal
                self.order.open_position(
                    entry_price=close_price, shares=self.quantity)
                entry_price = close_price
                holding = True
                signals.append(('buy', index, close_price,
                               self.quantity))

            if holding and close_price > current_vwap * (1 + self.threshold):
                # Sell signal
                percent_profit = (
                    close_price - self.order.positions[-1].entry_price) / entry_price
                self.order.close_position(
                    position_to_close=self.order.positions[-1], percent=0.2, current_price=close_price)  # set close
                total_profit += percent_profit
                holding = False
                signals.append(('sell', index, close_price,
                               self.quantity))

        # Update total profit attribute in order
        self.order.total_profit = total_profit

        return signals, self.order.total_profit
