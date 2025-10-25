"""
Moving Average Strategy Implementation

This strategy generates buy signals when the short-term moving average
crosses above the long-term moving average, and sell signals when it
crosses below.
"""

from typing import Dict, Any

import matplotlib.pyplot as plt
import pandas as pd

from config.constants import DEFAULT_SHORT_WINDOW, DEFAULT_LONG_WINDOW
from models import MarketDataPoint, Signal, MarketAction, SignalList
from .ema import MovingAverage
from .strategy import Strategy


class MovingAverageStrategy(Strategy):
    """
    Moving Average crossover strategy implementation.

    This strategy uses two moving averages with different lookback periods.
    A buy signal is generated when the short MA crosses above the long MA,
    and a sell signal when the short MA crosses below the long MA.
    """

    def __init__(
        self,
        short_window: int = DEFAULT_SHORT_WINDOW,
        long_window: int = DEFAULT_LONG_WINDOW,
    ) -> None:
        """
        Initialize the Moving Average Strategy.

        Args:
            short_window: Lookback period for short-term moving average
            long_window: Lookback period for long-term moving average

        Raises:
            ValueError: If window parameters are invalid
        """
        super().__init__()

        if short_window <= 0 or long_window <= 0:
            raise ValueError("Window parameters must be positive integers")
        if short_window >= long_window:
            raise ValueError("Short window must be less than long window")

        self._short_window = short_window
        self._long_window = long_window
        self._moving_averages: Dict[str, Dict[str, Any]] = {}

    def _get_moving_average(self, symbol: str) -> Dict[str, Any]:
        """
        Get or create moving average calculators for a symbol.

        Args:
            symbol: Ticker symbol

        Returns:
            Dictionary containing moving average state
        """
        if symbol in self._moving_averages:
            return self._moving_averages[symbol]

        short = MovingAverage(self._short_window)
        long = MovingAverage(self._long_window)
        moving_averages = {
            "length": 0,
            "short": short,
            "long": long,
        }
        self._moving_averages[symbol] = moving_averages
        return moving_averages

    def generate_signals(self, *data: MarketDataPoint) -> SignalList:
        """
        Generate trading signals based on moving average crossover.

        Args:
            *data: Variable number of MarketDataPoint objects

        Returns:
            List of trading signals

        Raises:
            ValueError: If invalid market data is provided
        """
        if not data:
            return []

        signals = []
        for tick in data:
            # Validate input data
            if not isinstance(tick, MarketDataPoint):
                raise ValueError(f"Invalid data point type: {type(tick)}")
            if tick.price < 0.01:
                raise ValueError(f"Invalid price {tick.price} for {tick.symbol}")
            if not tick.symbol or not isinstance(tick.symbol, str):
                raise ValueError(f"Invalid symbol: {tick.symbol}")

            moving_averages = self._get_moving_average(tick.symbol)
            moving_averages["length"] += 1
            short = moving_averages["short"].update(tick.price)
            long = moving_averages["long"].update(tick.price)

            if moving_averages["length"] < self._long_window:
                signals.append(
                    Signal(
                        action=MarketAction.HOLD,
                        symbol=tick.symbol,
                        quantity=0,
                        price=tick.price,
                    )
                )
            else:
                if short > long:
                    signals.append(
                        Signal(
                            action=MarketAction.BUY,
                            symbol=tick.symbol,
                            quantity=1,
                            price=tick.price,
                        )
                    )
                else:
                    signals.append(
                        Signal(
                            action=MarketAction.SELL,
                            symbol=tick.symbol,
                            quantity=1,
                            price=tick.price,
                        )
                    )

            # Update internal state
            self._update_prices(tick)
            self._indicator_history[tick.symbol]["short"].append(short)
            self._indicator_history[tick.symbol]["long"].append(long)

        return signals

    def plot_indicators(self, symbol: str) -> None:
        """
        Plot the moving average indicators for a given symbol.

        Args:
            symbol: The ticker symbol to plot indicators for

        Raises:
            ValueError: If no indicator history exists for the symbol
        """
        if symbol not in self._indicator_history:
            raise ValueError(f"No indicator history available for symbol: {symbol}")

        if not self._indicator_history[symbol]:
            raise ValueError(f"Empty indicator history for symbol: {symbol}")

        df = pd.DataFrame(self._indicator_history[symbol])
        if df.empty:
            raise ValueError(f"No indicator data to plot for symbol: {symbol}")

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df.index, df["short"], label=f"Short MA ({self._short_window})")
        ax.plot(df.index, df["long"], label=f"Long MA ({self._long_window})")
        ax.legend()
        ax.grid(True)
        ax.set_title(f"Moving Average Strategy for {symbol}")
        ax.set_xlabel("Time")
        ax.set_ylabel("Price")
        plt.tight_layout()
        plt.show()
