from typing import List, Tuple
from core.base import Strategy, Portfolio
from core import log
from pandas import DataFrame

class MeanReversion(Strategy):
    def __init__(self, portfolio: Portfolio, short_ma_window=20, long_ma_window=100, threshold=0.02, transaction_fee=0.01):
        super().__init__(portfolio, short_ma_window, long_ma_window, threshold, transaction_fee)
        self.holding = False

   

    def execute(self) -> Tuple[List[Tuple[str, float, float]], float]:
        buy_timestamps = []
        sell_timestamps_profits = []
        
        # Calculate short and long term moving averages
        self.portfolio.data_frame['short_ma'] = self.portfolio.data_frame['close'].rolling(window=self.short_ma_window).mean()
        self.portfolio.data_frame['long_ma'] = self.portfolio.data_frame['close'].rolling(window=self.long_ma_window).mean()

        
        for index, row in self.portfolio.data_frame.iterrows():
            close_price = row['close']
            short_ma = row['short_ma']
            long_ma = row['long_ma']
        #    
            # Check for potential buy signal (close price falls below threshold distance from long MA)
            if not self.holding and close_price < (1 - self.threshold) * long_ma:
                self.holding = True
                self.entry_price = close_price
                buy_timestamps.append(row['timestamp'])
                # Open a long position when buy signal is triggered
                self.portfolio.open_position(entry_price=self.entry_price, shares=1)
                # Optional: Print buy signal

            # Check for potential sell signal (two conditions)
            if self.holding and (
                (close_price > (1 + self.threshold) * long_ma) or  # Price above upper threshold of long MA
                (close_price > short_ma and short_ma > long_ma)  # Price above short MA which is above long MA
            ):
                self.holding = False
                gross_profit = close_price - self.entry_price  # Gross profit before fees
                transaction_cost = 2 * self.transaction_fee  # Fixed fee for both buy and sell
                profit = gross_profit - transaction_cost  # Profit after fees
                sell_timestamps_profits.append((row['timestamp'], profit, gross_profit))
                self.entry_price = None
                
                # Close the long position when sell signal is triggered
                position_to_close = self.portfolio.positions[-1]  # Assuming last opened position is to be closed
                self.portfolio.close_position(position_to_close=position_to_close, percent=0.2, current_price=close_price)
                # Optional: Print sell signal with profit (after fees) and gross profit
                self.portfolio.total_profit += profit

        return sell_timestamps_profits, self.portfolio.total_profit