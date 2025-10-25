# backtester/strategy.py
import numpy as np
import pandas as pd

# from price_loader import PriceLoader


class VolatilityBreakoutStrategy:

    def __init__(self, window=10):
        self.window = window

    def signals(self, prices: pd.Series) -> pd.Series:

        returns = prices.pct_change(fill_method=None)
        volatility = returns.rolling(window=self.window).std()
        signals = (returns - volatility).apply(
            lambda x: 1 if x > 0 else (-1 if x < 0 else 0)
        )
        return signals


vs = VolatilityBreakoutStrategy()

print(vs.signals(pd.Series([np.nan] * 5)))
