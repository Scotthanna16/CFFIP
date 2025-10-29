# analytics.py
import numpy as np
from src.models import Instrument


class InstrumentDecorator(Instrument):
    def __init__(self, instrument: Instrument):
        self.instrument = instrument

    def __getattr__(self, name):
        return getattr(self.instrument, name)

    def get_metrics(self) -> dict[str, str | float]:
        return self.instrument.get_metrics()

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.instrument)})"


class VolatilityDecorator(InstrumentDecorator):

    def get_metrics(self):

        metrics = super().get_metrics()
        prices = np.array(self.prices, dtype=float)
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns)
        metrics["volatility"] = round(float(volatility), 4)
        return metrics


class BetaDecorator(InstrumentDecorator):
    def __init__(self, instrument: Instrument, benchmark_prices: list[float]):
        self.instrument = instrument
        self.benchmark_prices = benchmark_prices

    def get_metrics(self) -> dict[str, str | float]:
        metrics = super().get_metrics()
        prices = np.array(self.prices, dtype=float)
        returns = np.diff(prices) / prices[:-1]

        bench = np.array(self.benchmark_prices, dtype=float)
        bench_returns = np.diff(bench) / bench[:-1]

        cov = np.cov(returns, bench_returns)[0, 1]
        var = np.var(bench_returns)
        beta = cov / var

        metrics["beta"] = round(float(beta), 4)
        return metrics


class DrawdownDecorator(InstrumentDecorator):

    def get_metrics(self):
        metrics = super().get_metrics()
        prices = np.array(self.prices, dtype=float)
        cumulative_max = np.maximum.accumulate(prices)
        drawdowns = (prices - cumulative_max) / cumulative_max
        max_drawdown = drawdowns.min()
        metrics["max_drawdown"] = round(float(max_drawdown), 4)
        return metrics
