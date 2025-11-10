import numpy as np
import pytest

from src import strategy as strategy_mod


class DummyShm:
    def __init__(self, name, symbols, lock):
        self.name = name
        self._data = {s: np.nan for s in symbols}

    def read(self, symbol):
        return self._data.get(symbol, None)


@pytest.fixture(autouse=True)
def patch_shared_price_book(monkeypatch):
    """Ensure Strategy doesn't create real shared memory during tests."""

    def _dummy(name, symbols, lock):
        return DummyShm(name, symbols, lock)

    monkeypatch.setattr(strategy_mod, "SharedPriceBook", _dummy)
    yield


def make_strategy():
    return strategy_mod.Strategy(
        shm_name=None,
        shm_lock=None,
        freq=0.01,
        news_host="",
        news_port=0,
        strat_host="",
        strat_port=0,
        symbols=["AAPL"],
    )


def test_generate_signal_insufficient_prices_returns_none():
    s = make_strategy()
    prices = np.array([100.0] * 10)
    # sentiment high but not enough prices -> no signal
    assert s.generate_signal("AAPL", prices, 100) is None


def test_generate_signal_generates_buy_and_updates_position():
    s = make_strategy()

    # 30 values at 100, then 20 values at 110 => sma(20)=110, lma(50)=104 => positive
    prices = np.array([100.0] * 30 + [110.0] * 20)
    signal = s.generate_signal("AAPL", prices, 80)  # sentiment > BULL_THRESHOLD
    assert signal is not None
    parts = signal.split(",")
    assert parts[0] == "BUY"
    assert parts[2] == "AAPL"
    assert float(parts[3]) == pytest.approx(110.0)

    # second identical signal should not be emitted because position is already LONG
    signal2 = s.generate_signal("AAPL", prices, 80)
    assert signal2 is None


def test_generate_signal_generates_sell_and_updates_position():
    s = make_strategy()

    # make price_sig negative: 30 values at 110, 20 at 100 => sma=100, lma=106 => negative
    prices = np.array([110.0] * 30 + [100.0] * 20)
    signal = s.generate_signal("AAPL", prices, 10)  # sentiment < BEAR_THRESHOLD
    assert signal is not None
    parts = signal.split(",")
    assert parts[0] == "SELL"
    assert parts[2] == "AAPL"
    assert float(parts[3]) == pytest.approx(100.0)
