from typing import List, Tuple
from pandas import Series
from core.base import Strategy


class POV(Strategy):
    def __init__(self, order, quantity=1, short_ma_window=0, long_ma_window=100, threshold=0.01, transaction_fee=0.01,percent_close=0.2):
        super().__init__(order, quantity, short_ma_window, long_ma_window, threshold, transaction_fee,percent_close)

    def execute(self) -> Tuple[List[Tuple[str, float, float]], float]:
        pov = self.calculate()
        signals, total_profit = self.generate_signals(pov)
        return signals, total_profit

    def calculate(self) -> Series:
        """
        Calculate Percentage of Volume (POV) for each row in the DataFrame.

        Returns:
            pandas Series: Series containing POV values corresponding to each row in the DataFrame.
        """
        # Calculate cumulative sum of volume
        self.order.data_frame['cumulative_volume'] = self.order.data_frame['volume'].cumsum()

        # Calculate POV using rolling window
        self.order.data_frame['pov'] = self.order.data_frame['volume'] / self.order.data_frame['cumulative_volume']

        # Shift POV values by short_ma_window to align with current period
        self.order.data_frame['pov'] = self.order.data_frame['pov'].rolling(window=self.short_ma_window).mean()

        return self.order.data_frame['pov']

    def generate_signals(self, pov: Series) -> Tuple[List[Tuple[str, float, float]], float]:
        """
        Generate buy/sell signals and calculate total profit based on POV.

        Args:
            pov (Series): Series containing POV values.

        Returns:
            Tuple[List[Tuple[str, float, float]], float]: Signals (buy/sell) and total profit.
        """
        signals = []
        holding = False
        entry_price = None
        total_profit = 0
        
        for index, row in self.order.data_frame.iterrows():
            close_price = row['close']
            # Get POV value corresponding to the current row
            current_pov = pov.loc[index]

            if not holding and row['volume'] > current_pov:
                # Buy signal
                self.order.open_position(entry_price=close_price, shares=self.quantity)
                entry_price = close_price
                holding = True
                signals.append(('buy', index, close_price, self.quantity))

            if holding and row['volume'] < current_pov:
                # Sell signal
                percent_profit = (close_price - self.order.positions[-1].entry_price) / entry_price
                self.order.close_position(position_to_close=self.order.positions[-1], percent=self.percent_close, current_price=close_price)  # set close
                total_profit += percent_profit
                holding = False
                signals.append(('sell', index, close_price, self.quantity))

        # Update total profit attribute in order
        self.order.total_profit = total_profit

        return signals, self.order.total_profit
