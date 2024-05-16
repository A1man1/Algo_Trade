from typing import Optional, List

from Stratgies import VWAP, MeanReversion , POV
from core.order import Order 
from core import settings
from core.model import StrategyType


class AlgoTrade(Order):
    def __init__(self,stock_name,strategy_types:Optional[List[str]|str],quantity=1,short_ma_window=0, long_ma_window=100, threshold=0.01,percent_close=0.2,
                 transaction_fee=0.02,*args, **kwargs):
        self.strategy_types = strategy_types
        self.stock_name= stock_name
        super(AlgoTrade, self).__init__(*args, **kwargs)
        
        self.vwap = VWAP(self,quantity=quantity,short_ma_window=short_ma_window,long_ma_window=long_ma_window,threshold=threshold,transaction_fee=transaction_fee,percent_close=percent_close)
        self.mean = MeanReversion(self,quantity=quantity,short_ma_window=short_ma_window,long_ma_window=long_ma_window,threshold=threshold,transaction_fee=transaction_fee,percent_close=percent_close)
        self.pov = POV(self,quantity=quantity,short_ma_window=short_ma_window,long_ma_window=long_ma_window,threshold=threshold,transaction_fee=transaction_fee,percent_close=percent_close)


    def set_strategy(self):
        results = None
        if isinstance(self.strategy_types, str):
            if self.strategy_types == StrategyType.MEAN_REVISION:
                results = self.mean.execute()

            elif self.strategy_types == StrategyType.VWAP:
                results = self.vwap.execute()
            
            elif self.strategy_types == StrategyType.POV:
                    results[settings.POV] = self.pov.execute()

        else:
            results = {}
            for strategy in self.strategy_types:
                if strategy == StrategyType.MEAN_REVISION:
                    results[StrategyType.MEAN_REVISION] = self.mean.execute()

                if strategy == StrategyType.VWAP:
                    results[StrategyType.VWAP] = self.vwap.execute()

                if strategy == StrategyType.POV:
                    results[StrategyType.POV] = self.pov.execute()

        return results

    def execute_trade(self):
        """
        Simulate trades and update portfolio based on DataFrame.
        """
        processed_data = self.set_strategy()
        results = None
        if isinstance(processed_data, list):
            results = self.place_order(processed_data)
        else:
            results = {}
            for strategy, data in processed_data.items():
                data = self.place_order(data)
                results[strategy] = data

        return results , self.trades , self.positions
