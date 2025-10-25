"""
Base Strategy Class

This module defines the abstract base class for all trading strategies.
All concrete strategy implementations must inherit from this class.
"""

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, List

from models import MarketDataPoint, Signal, SignalList


class Strategy(ABC):
    """
    Abstract base class for all trading strategies.

    This class provides the common interface and functionality that all
    trading strategies must implement. It handles price tracking and
    provides the framework for signal generation.
    """

    def __init__(self) -> None:
        """Initialize the strategy with empty price and indicator histories."""
        self._prices: Dict[str, List[float]] = defaultdict(list)
        self._indicator_history: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: defaultdict(list)
        )

    def _update_prices(self, *data: MarketDataPoint) -> None:
        """
        Update internal price history with new market data.

        Args:
            *data: Variable number of MarketDataPoint objects
        """
        for point in data:
            self._prices[point.symbol].append(point.price)

    @abstractmethod
    def generate_signals(self, *data: MarketDataPoint) -> SignalList:
        """
        Generate trading signals based on market data.

        This method must be implemented by all concrete strategy classes.
        It analyzes the provided market data and returns appropriate
        trading signals.

        Args:
            *data: Variable number of MarketDataPoint objects (1 per symbol)

        Returns:
            List of trading signals to execute

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def plot_indicators(self, symbol: str) -> None:
        """
        Plot indicators for a given symbol.

        This method should be implemented by strategies that support
        visualization of their indicators.

        Args:
            symbol: The ticker symbol to plot indicators for

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclass has not implemented this method")
