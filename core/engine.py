from Stratgies import VWAP , MeanReversion
from core import Portfolio, settings

class AlgoTrade(Portfolio):
    def __init__(self, *args, **kwargs):
        super(AlgoTrade, self).__init__(*args, **kwargs)
        
    def execute_trade(self,strategy_name):
        """
        Simulate trades and update portfolio based on DataFrame.
        """
        results = None
        
        if strategy_name == settings.MEAN_REVISION:
            mean = MeanReversion(self)
            results = mean.execute()
        
        elif strategy_name == settings.VMAP:
            vwap =  VWAP(self)
            results = vwap.execute()
        
        
        return results
        
        
        # for index, row in self.data_frame.iterrows():
        #     close_price = row['close']  # Assuming 'close' is the column name for closing prices
            # Simulate trading strategy (example: buy if price > 100)
            # if close_price > 100:
            #     # Create a Trade object
            #     trade = Trade(stock_name=self.stock_name, quantity=1, price=close_price, trade_type='sell')
            #     self.trades.append(trade)
            #     # Open a position with the trade's details
            #     self.open_position(quantity=1, entry_price=close_price)