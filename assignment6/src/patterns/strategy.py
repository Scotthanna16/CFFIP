# patterns/strategy.py
from abc import ABC, abstractmethod
from src.models import MarketDataPoint
from collections import deque, defaultdict
import json
from typing import Dict, List
import numpy as np

"""
Strategy Pattern

- Problem: Support interchangeable trading strategies.
- Expectations:
    - Create abstract Strategy.generate_signals(tick: MarketDataPoint) -> list.
    - Implement:
        - MeanReversionStrategy
        - BreakoutStrategy
    - Each maintains internal state and uses parameters from strategy_params.json.
    - Demonstrate strategy interchangeability and signal generation.
"""


class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, tick: MarketDataPoint) -> list:
        pass


class MeanReversionStrategy(Strategy):
    def __init__(self, lookback_window: int, threshold: float):
        self._lookback_window = lookback_window
        self._threshold = threshold
        self._prices = defaultdict(lambda: deque(maxlen=lookback_window))
        self._sum_prices = defaultdict(lambda: 0.0)

    def generate_signals(self, tick: MarketDataPoint) -> list:
        signals = []
        price = tick.price
        symbol = tick.symbol

        if len(self._prices[symbol]) < self._lookback_window:
            self._prices[symbol].append(price)
            self._sum_prices[symbol] += price
            return signals
        else:
            self._sum_prices[symbol] -= self._prices[symbol][0]
            self._prices[symbol].append(price)
            self._sum_prices[symbol] += price
            moving_average = self._sum_prices[symbol] / self._lookback_window

            if price / moving_average < (1 - self._threshold):
                signals.append("BUY")
            elif price / moving_average > (1 + self._threshold):
                signals.append("SELL")

        return signals

    @classmethod
    def from_json(cls, filepath: str) -> "MeanReversionStrategy":

        with open(filepath, "r") as f:
            data = json.load(f)
        params = data.get("MeanReversionStrategy", {})
        lookback_window = params.get("lookback_window", None)
        threshold = params.get("threshold", None)

        if lookback_window is None or threshold is None:
            raise ValueError("Missing parameters for MeanReversionStrategy")

        return cls(lookback_window=lookback_window, threshold=threshold)


class BreakoutStrategy(Strategy):

    def __init__(self, lookback_window, threshold):
        self._price_history: dict[str, list[float]] = {}
        self._return_history: dict[str, list[float]] = {}
        self._lookback_window = lookback_window
        self._threshold = threshold

    def _rolling_vol(self, returns: list[float]) -> float | None:
        if len(returns) < self._lookback_window:
            return None
        return np.std(returns[-self._lookback_window :])

    def generate_signals(self, tick: MarketDataPoint) -> list:
        if tick.symbol in self._price_history:
            self._price_history[tick.symbol].append(tick.price)
            ret = (
                tick.price - self._price_history[tick.symbol][-2]
            ) / self._price_history[tick.symbol][-2]
            if tick.symbol in self._return_history:
                self._return_history[tick.symbol].append(ret)
            else:
                self._return_history[tick.symbol] = [ret]

            vol = self._rolling_vol(self._return_history[tick.symbol])

            if ret is None or vol is None:
                return []
            if ret > vol * (1 + self._threshold):
                return ["BUY"]
            elif ret < -vol * (1 + self._threshold):
                return ["SELL"]
            else:
                return []

        else:
            self._price_history[tick.symbol] = [tick.price]
            return []

    @classmethod
    def from_json(cls, filepath: str) -> "BreakoutStrategy":
        with open(filepath, "r") as f:
            data = json.load(f)
        params = data.get("BreakoutStrategy", {})
        lookback_window = params.get("lookback_window", None)
        threshold = params.get("threshold", None)

        if lookback_window is None or threshold is None:
            raise ValueError("Missing parameters for BreakoutStrategy")

        return cls(lookback_window=lookback_window, threshold=threshold)
