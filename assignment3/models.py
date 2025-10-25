from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod


class MarketAction(Enum):
    """Enumeration of possible trading actions."""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class MarketDataPoint:
    """
    Represents a single market data point.

    This immutable dataclass contains timestamp, symbol, and price information
    for a specific market observation.
    """

    timestamp: datetime
    symbol: str
    price: float


@dataclass(frozen=True)
class Signal:
    """
    Represents a trading signal.

    This immutable dataclass contains information about a trading action
    including the action type, symbol, quantity, and price.
    """

    action: MarketAction
    symbol: str
    quantity: int
    price: float



# Type aliases
SignalList = list[Signal]

class Strategy(ABC):

    @abstractmethod
    def generate_signals(self, tick: MarketDataPoint) -> SignalList:

        pass
