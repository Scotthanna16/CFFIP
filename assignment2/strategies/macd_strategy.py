"""
MACD Strategy Implementation

This strategy generates buy signals when MACD line crosses above signal line
and sell signals when it crosses below.

https://www.investopedia.com/terms/m/macd.asp
"""

from typing import Dict, Any, Optional

import matplotlib.pyplot as plt
import pandas as pd

from models import MarketDataPoint, Signal, MarketAction, SignalList
from .ema import ExponentialMovingAverage
from .strategy import Strategy


class MACDStrategy(Strategy):
    """
    MACD (Moving Average Convergence Divergence) strategy implementation.

    This strategy uses the MACD indicator to generate trading signals based on
    the relationship between the MACD line and signal line crossovers.
    """

    def __init__(
        self,
        short_window: int = 12,
        long_window: int = 26,
        signal_window: int = 9,
        tolerance: float = 0.001,
    ) -> None:
        """
        Initialize the MACDStrategy class.

        Args:
            short_window: The short window for the MACD. Defaults to 12.
            long_window: The long window for the MACD. Defaults to 26.
            signal_window: The signal window for the MACD. Defaults to 9.
            tolerance: Tolerance for crossover detection. Defaults to 0.001.

        Raises:
            ValueError: If window parameters are invalid
        """
        super().__init__()

        if short_window <= 0 or long_window <= 0 or signal_window <= 0:
            raise ValueError("All window parameters must be positive integers")
        if short_window >= long_window:
            raise ValueError("Short window must be less than long window")

        self._short_window = short_window
        self._long_window = long_window
        self._signal_window = signal_window
        self._emas: Dict[str, Dict[str, Any]] = {}
        self._macd_length = self._long_window + self._signal_window
        self._tolerance = tolerance
        self._previous_macd: Dict[str, float] = {}
        self._previous_sig: Dict[str, float] = {}

    def _get_emas(self, symbol: str):

        if symbol in self._emas:
            return self._emas[symbol]

        length = 0
        ema_short = ExponentialMovingAverage(self._short_window)
        ema_long = ExponentialMovingAverage(self._long_window)
        ema_signal = ExponentialMovingAverage(self._signal_window)

        emas = {
            "length": length,
            "short": ema_short,
            "long": ema_long,
            "signal": ema_signal,
        }

        self._emas[symbol] = emas

        return emas

    def generate_signals(self, *data: MarketDataPoint) -> SignalList:
        """
        Generate trading signals based on MACD crossover.

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

            emas = self._get_emas(tick.symbol)
            emas["length"] += 1
            short = emas["short"].update(tick.price)
            long = emas["long"].update(tick.price)
            macd = short - long
            sig = emas["signal"].update(macd)

            if emas["length"] < self._macd_length:
                signals.append(
                    Signal(
                        action=MarketAction.HOLD,
                        symbol=tick.symbol,
                        quantity=0,
                        price=tick.price,
                    )
                )
            else:
                # Initialize previous values if not exists
                if tick.symbol not in self._previous_macd:
                    self._previous_macd[tick.symbol] = macd
                    self._previous_sig[tick.symbol] = sig
                    signals.append(
                        Signal(
                            action=MarketAction.HOLD,
                            symbol=tick.symbol,
                            quantity=0,
                            price=tick.price,
                        )
                    )
                else:
                    prev_macd = self._previous_macd[tick.symbol]
                    prev_sig = self._previous_sig[tick.symbol]

                    # Buy if MACD crosses above signal line
                    if prev_macd <= prev_sig and macd > sig:
                        signals.append(
                            Signal(
                                action=MarketAction.BUY,
                                symbol=tick.symbol,
                                quantity=1,
                                price=tick.price,
                            )
                        )
                    # Sell if MACD crosses below signal line
                    elif prev_macd >= prev_sig and macd < sig:
                        signals.append(
                            Signal(
                                action=MarketAction.SELL,
                                symbol=tick.symbol,
                                quantity=1,
                                price=tick.price,
                            )
                        )
                    else:
                        signals.append(
                            Signal(
                                action=MarketAction.HOLD,
                                symbol=tick.symbol,
                                quantity=0,
                                price=tick.price,
                            )
                        )

            # Update previous values
            self._previous_macd[tick.symbol] = macd
            self._previous_sig[tick.symbol] = sig
            self._update_prices(tick)
            self._indicator_history[tick.symbol]["macd"].append(macd)
            self._indicator_history[tick.symbol]["sig"].append(sig)

        return signals

    def plot_indicators(self, symbol: str) -> None:
        """
        Plot the MACD indicators for a given symbol.

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

        df["hist"] = df["macd"] - df["sig"]

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot histogram with different colors for positive and negative values
        positive_mask = df["hist"] >= 0
        negative_mask = df["hist"] < 0

        # Plot positive values in green
        ax.bar(
            df.index[positive_mask],
            df["hist"][positive_mask],
            color="green",
            alpha=0.7,
        )

        # Plot negative values in red
        ax.bar(
            df.index[negative_mask],
            df["hist"][negative_mask],
            color="red",
            alpha=0.7,
        )

        # Add zero line
        ax.axhline(y=0, color="black", linestyle="-", alpha=0.3)

        ax.plot(
            df.index, df["macd"], color="blue", label="MACD", linewidth=1, alpha=0.5
        )
        ax.plot(
            df.index, df["sig"], color="orange", label="Signal", linewidth=1, alpha=0.5
        )

        # Customize the plot
        ax.set_title(f"MACD Plot for {symbol}")
        ax.set_xlabel("Time")
        ax.set_label("MACD - Signal")
        ax.grid(True, alpha=0.3)

        ax.legend(loc="upper left")

        plt.tight_layout()
        plt.show()
