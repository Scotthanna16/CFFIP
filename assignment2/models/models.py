"""
Core data models for the trading system.

This module defines the fundamental data structures used throughout
the trading system, including market data points, trading signals,
and market actions.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List


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


# Type aliases for better code clarity
PositionDict = Dict[str, Dict[str, float]]
# example: {
#     "AAPL": {"quantity": 10, "avg_price": 150.0},
#     "CASH": {"quantity": 1000.0, "avg_price": 1.0}
# }


PositionHistory = Dict[datetime, PositionDict]
# example: {
#     datetime(2023, 1, 1): {
#         "AAPL": {"quantity": 10, "avg_price": 150.0},
#         "CASH": {"quantity": 1000.0, "avg_price": 1.0}
#     },
#     datetime(2023, 1, 2): {
#         "AAPL": {"quantity": 5, "avg_price": 155.0},
#         "CASH": {"quantity": 1250.0, "avg_price": 1.0}
#     },
# }


PriceDict = Dict[str, float]
# example: {
#     "AAPL": 160.0,
#     "GOOGL": 2800.0
# }


SignalList = List[Signal]
# example: [
#     Signal(action=MarketAction.BUY, symbol="AAPL", quantity=10, price=150.0),
#     Signal(action=MarketAction.SELL, symbol="GOOGL", quantity=5, price=2800.0)
# ]


class PortfolioUpdateError(Exception):
    """Custom exception for invalid portfolio updates."""

    pass
