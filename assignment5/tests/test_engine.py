# tests/test_engine.py
from unittest.mock import MagicMock
import pandas as pd
import numpy as np
from backtester.engine import Backtester


# example
def test_engine_uses_tminus1_signal(prices, broker, strategy, monkeypatch):
    # Force exactly one buy at t=10 by controlling signals
    fake_strategy = MagicMock()
    fake_strategy.signals.return_value = prices * 0
    fake_strategy.signals.return_value.iloc[9] = 1  # triggers buy at t=10
    bt = Backtester(fake_strategy, broker)
    eq = bt.run(prices)
    assert broker.position == 1
    assert broker.cash == 1000 - float(prices.iloc[10])


def test_engine_uses_tminus1_signal_sell(prices, broker, strategy, monkeypatch):
    # Force exactly one sell at t=10 by controlling signals
    fake_strategy = MagicMock()
    fake_strategy.signals.return_value = prices * 0
    fake_strategy.signals.return_value.iloc[9] = -1  # triggers sell at t=10
    bt = Backtester(fake_strategy, broker)
    eq = bt.run(prices)
    assert broker.position == -1
    assert broker.cash == 1000 + float(prices.iloc[10])


def test_engine_no_signal(prices, broker, strategy, monkeypatch):
    # No signals should result in no trades
    fake_strategy = MagicMock()
    fake_strategy.signals.return_value = prices * 0  # no signals
    bt = Backtester(fake_strategy, broker)
    eq = bt.run(prices)
    assert broker.position == 0
    assert broker.cash == 1000


# Edge case tests


def test_engine_empty_series(broker, strategy):
    """Test that engine handles empty price series gracefully"""
    empty_prices = pd.Series([], dtype=float)
    bt = Backtester(strategy, broker)
    bt.run(empty_prices)
    # Should not crash and should maintain initial state
    assert broker.position == 0
    assert broker.cash == 1000


def test_engine_constant_price_series(broker, strategy):
    """Test engine behavior with constant prices (no volatility)"""
    constant_prices = pd.Series([100.0] * 50)
    bt = Backtester(strategy, broker)
    bt.run(constant_prices)
    # With constant prices, returns are 0, so signals should be 0 or NaN
    # No trades should occur
    assert broker.position == 0
    assert broker.cash == 1000


def test_engine_nans_at_head(broker, strategy):
    """Test engine handles NaNs at the beginning of the series"""
    prices_with_nans = pd.Series([np.nan, np.nan, np.nan] + [0] * 9 + [10, 1])
    bt = Backtester(strategy, broker)
    bt.run(prices_with_nans)
    # Engine should skip NaN values and only process valid prices
    assert isinstance(broker.position, (int, float))
    assert isinstance(broker.cash, (int, float))


def test_engine_very_short_series(broker, strategy):
    """Test engine with very short price series (fewer than strategy window)"""
    short_prices = pd.Series([100.0, 101.0, 99.0])
    bt = Backtester(strategy, broker)
    bt.run(short_prices)
    assert broker.position == 0
    assert broker.cash == 1000


def test_engine_all_nans(broker, strategy):
    """Test engine with series containing only NaNs"""
    nan_prices = pd.Series([np.nan] * 20)
    bt = Backtester(strategy, broker)
    bt.run(nan_prices)
    # Should handle gracefully without trades
    assert broker.position == 0
    assert broker.cash == 1000


def test_engine_single_valid_price_after_nans(broker, strategy):
    """Test edge case with mostly NaNs and one valid price"""
    prices = pd.Series([np.nan] * 10 + [100.0])
    bt = Backtester(strategy, broker)
    bt.run(prices)
    # Not enough data for rolling window, no trades
    assert broker.position == 0
    assert broker.cash == 1000
