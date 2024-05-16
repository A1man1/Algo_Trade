from typing import List, Tuple
from core.base import Strategy
from core import log
from pandas import DataFrame, Series


class MeanReversion(Strategy):

    def __init__(self,order,quantity,short_ma_window=20, long_ma_window=100, threshold=0.02, transaction_fee=0.01,percent_close=0.2):

        super().__init__(order, quantity, short_ma_window, long_ma_window, threshold, transaction_fee,percent_close)

        self.holding = False

    def calculate(self) -> DataFrame | Series | None:
        # Calculate short and long term moving averages
        self.order.data_frame['short_ma'] = self.order.data_frame['close'].rolling(window=self.short_ma_window).mean()
        self.order.data_frame['long_ma'] = self.order.data_frame['close'].rolling(window=self.long_ma_window).mean()


    def generate_signals(self) -> Tuple[List[Tuple[str | float]] | float]:
        signals =[]
        for index, row in self.order.data_frame.iterrows():
            close_price = row['close']
            short_ma = row['short_ma']
            long_ma = row['long_ma']
        #    
            # Check for potential buy signal (close price falls below threshold distance from long MA)
            if not self.holding and close_price < (1 - self.threshold) * long_ma:
                self.holding = True
                self.entry_price = close_price
                signals.append(('buy', index, close_price, self.quantity))
                # Open a long position when buy signal is triggered
                self.order.open_position(entry_price=self.entry_price, shares=self.quantity)
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
                signals.append(('sell', index, close_price, self.quantity))
                self.entry_price = None
                
                # Close the long position when sell signal is triggered
                position_to_close = self.order.positions[-1]  # Assuming last opened position is to be closed
                self.order.close_position(position_to_close=position_to_close, percent=self.percent_close, current_price=close_price)
                # Optional: Print sell signal with profit (after fees) and gross profit
                self.order.total_profit += profit

        return signals, self.order.total_profit
    
    def execute(self) -> Tuple[List[Tuple[str, float, float]], float]:
        self.calculate()
        return self.generate_signals()

        

    # def calculate(self) -> DataFrame:

    #     """

    #     Calculate short and long term moving averages.


    #     Returns:

    #         pandas DataFrame: DataFrame with short and long moving averages.

    #     """

    #     self.order.data_frame['short_ma'] = self.order.data_frame['close'].rolling(window=self.short_ma_window).mean()

    #     self.order.data_frame['long_ma'] = self.order.data_frame['close'].rolling(window=self.long_ma_window).mean()

    #     return self.order.data_frame


    # def generate_signals(self, data_frame: DataFrame) -> Tuple[List[Tuple[str, float, float]], float]:

    #     """

    #     Generate buy/sell signals and calculate total profit.


    #     Args:

    #         data_frame (DataFrame): DataFrame with short and long moving averages.


    #     Returns:

    #         Tuple[List[Tuple[str, float, float]], float]: Signals (buy/sell) and total profit.

    #     """

    #     signals = []


    #     entry_price = None

    #     total_profit = 0


    #     for index, row in data_frame.iterrows():

    #         close_price = row['close']

    #         short_ma = row['short_ma']

    #         long_ma = row['long_ma']


    #         if not self.holding and close_price < (1 - self.threshold) * long_ma:

    #             # Buy signal

    #             self.holding = True

    #             entry_price = close_price

    #             self.order.open_position(entry_price=entry_price, shares=self.order.positions[-1].shares)
                
    #             signals.append(('buy', index, close_price, self.quantity))


    #         if self.holding and (

    #             (close_price > (1 + self.threshold) * long_ma) or

    #             (close_price > short_ma and short_ma > long_ma)

    #         ):

    #             # Sell signal

    #             gross_profit = close_price - entry_price

    #             transaction_cost = 2 * self.transaction_fee

    #             profit = gross_profit - transaction_cost

    #             self.order.close_position(position_to_close=self.order.positions[-1], percent=0.2, current_price=close_price)

    #             signals.append(('sell', index, close_price, self.quantity))

    #             total_profit += profit

    #             self.holding = False

    #             entry_price = None


    #     self.order.total_profit = total_profit

    #     return signals, total_profit


    # def execute(self) -> Tuple[List[Tuple[str, float, float]], float]:

    #     data_frame = self.calculate()

    #     return self.generate_signals(data_frame)