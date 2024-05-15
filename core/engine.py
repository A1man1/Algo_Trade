from Stratgies import VWAP, MeanReversion
from core import Order, settings


class AlgoTrade(Order):
    def __init__(self, *args, **kwargs):
        super(AlgoTrade, self).__init__(*args, **kwargs)

    def set_strategy(self):
        results = None
        if isinstance(self.strategy_types, str):
            if self.strategy_types == settings.MEAN_REVISION:
                mean = MeanReversion(self)
                results = mean.execute()

            elif self.strategy_types == settings.VMAP:
                vwap = VWAP(self)
                results = vwap.execute()
        else:
            results = {}
            for strategy in self.strategy_types:
                if strategy == settings.MEAN_REVISION:
                    mean = MeanReversion(self)
                    results[settings.MEAN_REVISION] = mean.execute()

                if strategy == settings.VWAP:
                    vwap = VWAP(self)
                    results[settings.VWAP] = vwap.execute()

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

        return results
