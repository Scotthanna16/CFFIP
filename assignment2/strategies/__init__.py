"""
Base Strategy Module

This module contains the base Strategy class that all other strategies inherit from.
"""

from strategies.strategy import Strategy
from strategies.benchmark_strategy import BenchmarkStrategy
from strategies.moving_average_strategy import MovingAverageStrategy
from strategies.volatility_breakout_strategy import VolatilityBreakoutStrategy
from strategies.macd_strategy import MACDStrategy
from strategies.rsi_strategy import RSIStrategy

__all__ = [
    "Strategy",
    "BenchmarkStrategy",
    "MovingAverageStrategy",
    "VolatilityBreakoutStrategy",
    "MACDStrategy",
    "RSIStrategy",
]
