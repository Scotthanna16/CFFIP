# backtester/engine.py
import pandas as pd
from .price_loader import PriceLoader
from .strategy import VolatilityBreakoutStrategy
from .broker import Broker
import numpy as np


class Backtester:
    def __init__(self, strategy=VolatilityBreakoutStrategy(5), broker=Broker()):
        self.strategy = strategy
        self.broker = broker

    def run(self, prices: pd.Series):
        # ensure prices is a pd.Series
        if not isinstance(prices, pd.Series):
            raise ValueError("Prices must be a pandas Series")
        # drop nans

        # don't modify the index
        prices = prices.dropna()

        signals = self.strategy.signals(prices)
        print("len prices:", len(prices))
        print("len signals:", len(signals))

        for signal, price in zip(signals.shift(1), prices):
            if signal == 1:
                self.broker.market_order("BUY", 1, price)
            elif signal == -1:
                self.broker.market_order("SELL", 1, price)
        # print(self.broker.cash + self.broker.position * signals["Prices"].iloc[-1])
