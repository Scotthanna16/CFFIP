"""
Exponential and Simple Moving Average implementations.

This module provides efficient implementations of exponential moving averages
and simple moving averages used in technical analysis strategies.
"""

from typing import List, Optional


class ExponentialMovingAverage:
    """
    Exponential Moving Average (EMA) calculator.

    Uses the standard EMA formula: EMA = alpha * price + (1 - alpha) * previous_EMA
    where alpha = 2 / (period + 1)
    """

    def __init__(self, period: int) -> None:
        """
        Initialize the Exponential Moving Average.

        Args:
            period: The lookback period for the EMA

        Raises:
            ValueError: If period is not a positive integer
        """
        if not isinstance(period, int) or period <= 0:
            raise ValueError(f"Period must be a positive integer, got {period}")

        self._alpha: float = 2 / (period + 1)
        self._ema: Optional[float] = None

    def update(self, data: float) -> float:
        """
        Update the EMA with new data.

        Args:
            data: New data point to include in the calculation

        Returns:
            Current EMA value
        """
        if self._ema is None:
            self._ema = data
        else:
            self._ema = self._alpha * data + (1 - self._alpha) * self._ema
        return self._ema

    def __call__(self, data: float) -> float:
        """Allow the EMA to be called as a function."""
        return self.update(data)


class MovingAverage:
    """
    Simple Moving Average (SMA) calculator.

    Maintains a window of values and calculates the average over that window.
    """

    def __init__(self, window: int) -> None:
        """
        Initialize the Moving Average.

        Args:
            window: The window size for the moving average

        Raises:
            ValueError: If window is not a positive integer
        """
        if not isinstance(window, int) or window <= 0:
            raise ValueError(f"Window must be a positive integer, got {window}")

        self._window: int = window
        self._values: List[float] = []
        self._moving_average: Optional[float] = None

    def update(self, data: float) -> float:
        """
        Update the moving average with new data.

        Args:
            data: New data point to include in the calculation

        Returns:
            Current moving average value
        """
        self._values.append(data)

        if len(self._values) > self._window:
            self._values.pop(0)

        # Calculate average based on actual number of values we have
        self._moving_average = sum(self._values) / len(self._values)

        return self._moving_average

    def __call__(self, data: float) -> float:
        """Allow the moving average to be called as a function."""
        return self.update(data)
