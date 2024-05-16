from typing import List, Tuple
from core.base import Strategy
from core import log
from pandas import DataFrame, Series
from core.model import TradeType, PositionType


class MeanReversion(Strategy):

    def __init__(self,order,quantity,short_ma_window=20, long_ma_window=100, threshold=0.02, transaction_fee=0.01,percent_close=0.2):

        super().__init__(order, quantity,short_ma_window, long_ma_window, threshold, transaction_fee,percent_close)

        self.holding = False

    def calculate(self) -> DataFrame | Series | None:
        # Calculate short and long term moving averages
        self.order.data_frame['short_ma'] = self.order.data_frame['close'].rolling(window=self.short_ma_window).mean()
        self.order.data_frame['long_ma'] = self.order.data_frame['close'].rolling(window=self.long_ma_window).mean()

    def calculate_stop_loss(self,position_type,close_price, long_ma, trailing_percentage=2):
        # Calculate the trailing stop loss

        if position_type == PositionType.LONG:
            stop_loss = max(long_ma, close_price * (1 - trailing_percentage / 100))

        elif position_type == PositionType.SHORT:
            stop_loss = min(long_ma, close_price * (1 + trailing_percentage / 100))

        else:

            raise ValueError("Invalid position type")

        return stop_loss

 
    def generate_signals(self) -> Tuple[List[Tuple[str | float]] | float]:
        signals =[]
        for index, row in self.order.data_frame.iterrows():
            close_price = row['close']
            short_ma = row['short_ma']
            long_ma = row['long_ma']
           
            trend_type = PositionType.LONG if short_ma > long_ma else PositionType.SHORT
        
                
            # Check for potential buy signal (close price falls below threshold distance from long MA)
            if not self.holding and close_price < (1 - self.threshold) * long_ma:
                self.holding = True
                self.entry_price = close_price
                
                exit_price = self.entry_price * (1 + self.threshold)  # Calculate exit price dynamically
                stop_loss = self.entry_price * (1 - self.threshold)  # Calculate stop-loss price dynamically
                signals.append((TradeType.BUY, index, close_price, self.quantity))
                # Open a long position when buy signal is triggered
                
                # (self, shares: int, entry_price: float , stop_loss, type_tends):
                self.order.open_position(entry_price=self.entry_price, shares=self.quantity,
                                         tend_type=trend_type, trade_type = TradeType.BUY,exit_price=exit_price, stop_loss=stop_loss) 
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
                signals.append((TradeType.SELL, index, close_price, self.quantity))
                self.entry_price = None
                
                # Close the long position when sell signal is triggered
                position_to_close = self.order.positions[-1]  # Assuming last opened position is to be closed
                self.order.close_position(position_to_close=position_to_close, percent=self.percent_close, current_price=close_price,
                                          trade_type=TradeType.SELL)
                # Optional: Print sell signal with profit (after fees) and gross profit
                self.order.total_profit += profit

        return signals, self.order.total_profit
    
    def execute(self) -> Tuple[List[Tuple[str, float, float]], float]:
        self.calculate()
        return self.generate_signals()

