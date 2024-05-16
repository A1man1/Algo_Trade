from enum import Enum

class PositionType(Enum):
    LONG = "long"
    SHORT = "short"
    
    
class TradeType(Enum):
    BUY = 'buy'
    SELL = 'sell'
    
class StrategyType(Enum):
    MEAN_REVISION:str = 'mean_revision'
    VWAP:str = 'vwap'
    POV:str = 'pov'