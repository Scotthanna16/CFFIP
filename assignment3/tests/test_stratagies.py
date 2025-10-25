import sys, pathlib
import pytest

path = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(path))


from models import MarketDataPoint, MarketAction, Signal, Strategy
from strategies import (
    NaiveMovingAverageStrategy,
    WindowedMovingAverageStrategy,
    OptimizedNaiveMovingAverageStrategy,
    OptimizedWindowedMovingAverageStrategy,
)
from data_loader import load_market_data
from datetime import datetime


@pytest.fixture
def sample_data():

    data = []
    p = 100.0
    for i in range(20):
        if i >= 10:
            # after 10 ticks, jump between 99 and 101
            # this will cause moving average to be 100, but price to jump above and below
            p += 1.0 * (-1) ** i

        data.append(MarketDataPoint(timestamp=datetime.now(), symbol="AAPL", price=p))
    return data


@pytest.fixture
def naive_strategy():
    return NaiveMovingAverageStrategy()


@pytest.fixture
def optimized_naive_strategy():
    return OptimizedNaiveMovingAverageStrategy()


@pytest.fixture
def windowed_strategy():
    return WindowedMovingAverageStrategy(window=10)


@pytest.fixture
def optimized_windowed_strategy():
    return OptimizedWindowedMovingAverageStrategy(window=10)


def test_naive_strategy(naive_strategy, sample_data):
    for tick in sample_data:
        signals = naive_strategy.generate_signals(tick)
        assert isinstance(signals, list)
        assert all(isinstance(signal, Signal) for signal in signals)
        for signal in signals:
            assert signal.symbol == tick.symbol
            assert signal.price == tick.price
            assert signal.action in MarketAction


def test_naive_strategy_signals(naive_strategy, sample_data):
    # Test with a sequence of prices to check moving average logic

    for i, tick in enumerate(sample_data):

        signals = naive_strategy.generate_signals(tick)
        if i < 10:
            # For the first 10 ticks, the price is steadily increasing from 100 to 109
            # The moving average will always be less than the current price, so expect BUY
            assert signals[0].action == MarketAction.HOLD
        else:
            if i % 2 == 0:
                # even exponent --> p=101
                assert signals[0].action == MarketAction.BUY
            else:
                assert signals[0].action == MarketAction.SELL


def test_optimized_naive_strategy(optimized_naive_strategy, sample_data):

    for tick in sample_data:
        signals = optimized_naive_strategy.generate_signals(tick)
        assert isinstance(signals, list)
        assert all(isinstance(signal, Signal) for signal in signals)
        for signal in signals:
            assert signal.symbol == tick.symbol
            assert signal.price == tick.price
            assert signal.action in MarketAction


def test_optimized_naive_strategy_signals(optimized_naive_strategy, sample_data):
    # Test with a sequence of prices to check moving average logic

    for i, tick in enumerate(sample_data):

        signals = optimized_naive_strategy.generate_signals(tick)
        if i < 10:
            # For the first 10 ticks, the price is steadily increasing from 100 to 109
            # The moving average will always be less than the current price, so expect BUY
            assert signals[0].action == MarketAction.HOLD
        else:
            if i % 2 == 0:
                # even exponent --> p=101, avg approx. 100
                assert signals[0].action == MarketAction.BUY
            else:
                assert signals[0].action == MarketAction.SELL


def test_windowed_strategy(windowed_strategy, sample_data):

    for tick in sample_data:
        signals = windowed_strategy.generate_signals(tick)
        assert isinstance(signals, list)
        assert all(isinstance(signal, Signal) for signal in signals)
        for signal in signals:
            assert signal.symbol == tick.symbol
            assert signal.price == tick.price
            assert signal.action in MarketAction


def test_windowed_strategy_signals(windowed_strategy, sample_data):
    # Test with a sequence of prices to check moving average logic

    for i, tick in enumerate(sample_data):

        signals = windowed_strategy.generate_signals(tick)
        if i < 10:
            # For the first 10 ticks, the price is steadily increasing from 100 to 109
            # The moving average will always be less than the current price, so expect BUY
            assert signals[0].action == MarketAction.HOLD
        else:
            if i % 2 == 0:
                # even exponent --> p=101, avg approx. 100
                assert signals[0].action == MarketAction.BUY
            else:
                assert signals[0].action == MarketAction.SELL
