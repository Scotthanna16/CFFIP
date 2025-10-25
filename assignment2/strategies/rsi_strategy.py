"""
RSI Strategy Implementation

This strategy generates buy signals when RSI < 30 (oversold condition).
"""

# TODO: Fix indicator history tracking for RSI.


from .strategy import Strategy
from models import MarketDataPoint, Signal, MarketAction, SignalList
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class RSIStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self._buy_threshold = 30
        self._sell_threshold = 70
        self._rsis = {}
        self._period = 14

    def _get_rsi(self, symbol: str, price: float) -> float | None:
        if symbol in self._rsis:
            data = self._rsis[symbol]
            if len(data) < self._period:
                data.append(price)
                self._rsis[symbol] = data
                return None
            else:
                data.append(price)
                if len(data) > self._period:
                    data.pop(0)
                deltas = np.diff(data)

                up = deltas[deltas > 0].sum() / self._period
                down = -deltas[deltas < 0].sum() / self._period
                rs = up / down if down != 0 else 0
                rsi = 100 - (100 / (1 + rs))
                return rsi

        data = [price]
        self._rsis[symbol] = data

    def generate_signals(self, *data: MarketDataPoint) -> SignalList:
        signals = []
        for tick in data:

            rsi = self._get_rsi(tick.symbol, tick.price)
            if rsi is None:
                signals.append(
                    Signal(
                        action=MarketAction.HOLD,
                        symbol=tick.symbol,
                        quantity=0,
                        price=tick.price,
                    )
                )

            else:
                if rsi < self._buy_threshold:
                    signals.append(
                        Signal(
                            action=MarketAction.BUY,
                            symbol=tick.symbol,
                            quantity=1,
                            price=tick.price,
                        )
                    )

                elif rsi > self._sell_threshold:
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

            self._update_prices(tick)
            self._indicator_history[tick.symbol]["rsi"].append(rsi)

        return signals

    def plot_indicators(self, symbol: str):
        pass
