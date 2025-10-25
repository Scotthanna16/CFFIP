from abc import ABC, abstractmethod
from src.models import MarketDataPoint, Signal
from dataclasses import dataclass
from collections import defaultdict


class Strategy(ABC):

    def __init__(self):
        self._prices = defaultdict(list)

    @abstractmethod
    def generate_signals(
        self, tick: MarketDataPoint
    ) -> list[Signal]:  # (action, symbol, quantity, price)

        raise NotImplementedError("Subclasses must implement this method")


class SimpleMovingAverageCrossoverStrategy(Strategy):
    def __init__(self, short_window: int, long_window: int):
        super().__init__()
        self.__short_window = short_window
        self.__long_window = long_window
        self.__last_signal: dict[str, str] = {}

    def generate_signals(
        self, tick: MarketDataPoint
    ) -> list[Signal]:  # (action, symbol, quantity, price)

        signals = []
        symbol = tick.symbol
        price = float(tick.price)

        self._prices[symbol].append(price)

        if len(self._prices[symbol]) >= self.__long_window:
            short_ma = (
                sum(self._prices[symbol][-self.__short_window :]) / self.__short_window
            )
            long_ma = (
                sum(self._prices[symbol][-self.__long_window :]) / self.__long_window
            )
            if short_ma > long_ma:
                # if self.__last_signal.get(symbol) == "BUY":
                #     return signals
                signals.append(Signal("BUY", symbol, 1, price))
                self.__last_signal[symbol] = "BUY"
            elif short_ma < long_ma:
                # if self.__last_signal.get(symbol) == "BUY":
                #     return signals
                signals.append(Signal("SELL", symbol, 1, price))
                self.__last_signal[symbol] = "SELL"

            else:
                signals.append(Signal("HOLD", symbol, 0, price))

        else:
            signals.append(Signal("HOLD", symbol, 0, price))

        return signals


class MeanReversionStrategy(Strategy):
    # Mean Reversion Strategy
    def __init__(self, mean_length: int = 20, threshold: float = 0.05):
        super().__init__()
        self.__mean_length = mean_length
        self.__threshold = threshold

    def generate_signals(self, tick: MarketDataPoint) -> list[Signal]:
        signals = []
        symbol = tick.symbol
        price = float(tick.price)
        if symbol not in self._prices:
            self._prices[symbol] = []
        self._prices[symbol].append(price)

        if len(self._prices[symbol]) > self.__mean_length:
            self._prices[symbol].pop(0)

        if len(self._prices[symbol]) >= self.__mean_length:
            mean_price = sum(self._prices[symbol]) / self.__mean_length
            # print(f"Mean price for {symbol}: {mean_price}")
            if price < mean_price * (1 - self.__threshold):
                signals.append(Signal("BUY", symbol, 1, price))
            elif price > mean_price * (1 + self.__threshold):
                signals.append(Signal("SELL", symbol, 1, price))
        # Should be it
        return signals


class ExponentialMovingAverageCrossoverStrategy(Strategy):
    def __init__(self, short_window: int, long_window: int):
        super().__init__()
        self.__short_window = short_window
        self.__long_window = long_window
        self.__short_ema = {}
        self.__long_ema = {}
        self.__last_signal = {}

    def generate_signals(self, tick: MarketDataPoint) -> list[Signal]:
        signals = []
        symbol = tick.symbol
        price = float(tick.price)

        self._prices[symbol].append(price)

        if len(self._prices[symbol]) >= self.__long_window:
            # Calculate EMAs
            if symbol not in self.__short_ema:
                self.__short_ema[symbol] = price
                self.__long_ema[symbol] = price
            else:
                # Calculate smoothing factors
                short_alpha = 2.0 / (self.__short_window + 1)
                long_alpha = 2.0 / (self.__long_window + 1)

                # Update EMAs
                self.__short_ema[symbol] = (
                    short_alpha * price + (1 - short_alpha) * self.__short_ema[symbol]
                )
                self.__long_ema[symbol] = (
                    long_alpha * price + (1 - long_alpha) * self.__long_ema[symbol]
                )

            # Generate signals based on EMA crossover
            if self.__short_ema[symbol] > self.__long_ema[symbol]:
                if self.__last_signal.get(symbol) != "BUY":
                    signals.append(Signal("BUY", symbol, 1, price))
                    self.__last_signal[symbol] = "BUY"
            elif self.__short_ema[symbol] < self.__long_ema[symbol]:
                if self.__last_signal.get(symbol) != "SELL":
                    signals.append(Signal("SELL", symbol, 1, price))
                    self.__last_signal[symbol] = "SELL"

        return signals
