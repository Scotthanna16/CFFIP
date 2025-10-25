"""
Volatility Breakout Strategy Implementation

This strategy generates buy signals when daily return > rolling 20-day std dev.
"""

# TODO: Implement the VolatilityBreakoutStrategy class

from .strategy import Strategy
from models import MarketDataPoint, Signal, MarketAction, SignalList
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class VolatilityBreakoutStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self._price_history: dict[str, list[float]] = {}
        self._return_history: dict[str, list[float]] = {}


    def _rolling_vol(self, returns: list[float], window: int = 20) -> float | None:
        if len(returns) < window:
            return None
        return np.std(returns[-window:])



    def generate_signals(self, *data: MarketDataPoint) -> SignalList:
        signals = []
        for tick in data:
            # Update price history and get return
            if tick.symbol in self._price_history:
                self._price_history[tick.symbol].append(tick.price)
                ret = (tick.price - self._price_history[tick.symbol][-2]) / self._price_history[tick.symbol][-2]
                if tick.symbol in self._return_history:
                    self._return_history[tick.symbol].append(ret)
                else:
                    self._return_history[tick.symbol] = [ret]

                vol = self._rolling_vol(self._return_history[tick.symbol])



                if ret is None or vol is None:
                    signals.append(
                        Signal(
                            action=MarketAction.HOLD,
                            symbol=tick.symbol,
                            quantity=0,
                            price=tick.price,
                        )
                    )
                    continue

                if ret > vol:
                    signals.append(
                        Signal(
                            action=MarketAction.BUY,
                            symbol=tick.symbol,
                            quantity=1,
                            price=tick.price,
                        )
                    )
                elif ret < -vol:
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

            else:
                self._price_history[tick.symbol] = [tick.price]
                signals.append(
                    Signal(
                        action=MarketAction.HOLD,
                        symbol=tick.symbol,
                        quantity=0,
                        price=tick.price,
                    )
                )

        return signals

    def plot_indicators(self, symbol):
        

        raise NotImplementedError("Indicator plotting not implemented yet.")
