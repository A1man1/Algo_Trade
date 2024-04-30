from typing import List, Tuple
from pandas import Series , DataFrame
from core.base import Portfolio, Strategy


class VWAP(Strategy):
   
    def execute(self) -> Tuple[List[Tuple[str, float, float]], float]:
        vwap = self.calculate_vwap()
        signals, total_profit = self.generate_signals(vwap)
        return signals, total_profit

    def calculate_vwap(self) -> Series:
        """
        Calculate Volume-Weighted Average Price (VWAP) for each row in the DataFrame.

        Returns:
            pandas Series: Series containing VWAP values corresponding to each row in the DataFrame.
        """
        # Calculate cumulative sum of price * volume
        self.portfolio.data_frame['cumulative_pv'] = (self.portfolio.data_frame['close'] * self.portfolio.data_frame['volume']).cumsum()

        # Calculate cumulative sum of volume
        self.portfolio.data_frame['cumulative_volume'] = self.portfolio.data_frame['volume'].cumsum()

        # Calculate VWAP using rolling window
        self.portfolio.data_frame['vwap'] = self.portfolio.data_frame['cumulative_pv'] / self.portfolio.data_frame['cumulative_volume']

        # Shift VWAP values by short_ma_window to align with current period
        self.portfolio.data_frame['vwap'] = self.portfolio.data_frame['vwap'].shift(self.short_ma_window)

        return self.portfolio.data_frame['vwap']
    

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

        for index, row in self.portfolio.data_frame.iterrows():
            close_price = row['close']
            current_vwap = vwap.loc[index]  # Get VWAP value corresponding to the current row

            if not holding and close_price < current_vwap * (1 - self.threshold):
                # Buy signal
                self.portfolio.open_position(entry_price=close_price, shares=1)
                entry_price = close_price
                holding = True
                signals.append(('buy', index, close_price))

            if holding and close_price > current_vwap * (1 + self.threshold):
                # Sell signal
                percent_profit = (close_price - self.portfolio.positions[-1].entry_price) / entry_price
                self.portfolio.close_position(position_to_close=self.portfolio.positions[-1],percent=0.2,current_price=close_price) #set close 
                total_profit += percent_profit
                holding = False
                signals.append(('sell', index, close_price))

        self.portfolio.total_profit = total_profit  # Update total profit attribute in portfolio

        return signals, self.portfolio.total_profit

    