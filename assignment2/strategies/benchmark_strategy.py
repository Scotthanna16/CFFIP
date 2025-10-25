"""
Benchmark Strategy Implementation

This strategy buys X shares of each ticker on the first day and holds them.
"""

# TODO: Implement the BenchmarkStrategy class

from .strategy import Strategy
from models import MarketDataPoint, Signal
from typing import List
from models import MarketAction, SignalList
from config.constants import DEFAULT_INITIAL_CASH


class BenchmarkStrategy(Strategy):
    def __init__(self, cash=DEFAULT_INITIAL_CASH, quantity=None):
        super().__init__()
        self._cash = cash
        self._quantity = quantity
        self._is_first_day = True

    def generate_signals(self, *data: MarketDataPoint) -> SignalList:

        if self._is_first_day:

            if self._quantity is None:
                total_price = 0
                for tick in data:
                    total_price += tick.price
                self._quantity = int(self._cash / total_price)

            signals = [
                Signal(
                    action=MarketAction.BUY,
                    symbol=tick.symbol,
                    quantity=self._quantity,
                    price=tick.price,
                )
                for tick in data
            ]
            # total_value = 0
            # for tick in data:
            #     total_value += tick.price * self._quantity

            # print(total_value)
            self._is_first_day = False
        else:
            signals = [
                Signal(
                    action=MarketAction.HOLD,
                    symbol=tick.symbol,
                    quantity=self._quantity,
                    price=tick.price,
                )
                for tick in data
            ]
            # total_value = 0
            # for tick in data:
            #     total_value += tick.price * self._quantity

            # print(total_value)

        return signals

    def plot_indicators(self, symbol: str):
        pass
