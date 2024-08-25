from enum import Enum


class MarketMode(Enum):
    BULLISH = 'BU'
    BULLISH_STRONG = 'BUS'
    IDLE = 'ID'
    BEARISH = 'BE'
    BEARISH_STRONG = 'BES'