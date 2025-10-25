# tests/test_strategy.py
import pandas as pd
import numpy as np


def test_signals_length(strategy, prices):
    sig = strategy.signals(prices)
    assert len(sig) == len(prices)


def test_signals_values(strategy, prices):
    sig = strategy.signals(prices)
    assert all(v in [-1, 0, 1] for v in sig.dropna().unique())


def test_signals_type(strategy, prices):
    signals = strategy.signals(prices)
    assert isinstance(signals, pd.Series)


def test_high_positive_returns_generate_positive_signal(strategy):
    prices = pd.Series([100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 1000])
    signals = strategy.signals(prices)

    assert signals.iloc[-1] == 1


def test_high_negative_returns_generate_negative_signal(strategy):
    prices = pd.Series(
        [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 100]
    )
    signals = strategy.signals(prices)

    assert signals.iloc[-1] == -1


def test_0_returns_generate_0_signal(strategy):
    prices = pd.Series(
        [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
    )
    signals = strategy.signals(prices)
    assert signals.iloc[-1] == 0


def test_short_series(strategy):
    prices = pd.Series([1000])
    signals = strategy.signals(prices)
    assert len(signals) == 1
    assert signals.iloc[0] == 0


def test_empty_series(strategy):
    prices = pd.Series([])
    signals = strategy.signals(prices)
    assert len(signals) == 0
    assert isinstance(signals, pd.Series)


def test_NaNs_series(strategy):
    prices = pd.Series([np.nan] * 10 + [0])
    signals = strategy.signals(prices)
    assert len(signals) == 11
    for i in range(11):
        assert signals.iloc[i] == 0
