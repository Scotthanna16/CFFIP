# tests/test_broker.py
import pytest


def test_buy_and_sell_updates_cash_and_pos(broker):
    broker.market_order("BUY", 2, 10.0)
    assert (broker.position, broker.cash) == (2, 1000 - 20.0)
    broker.market_order("SELL", 2, 10.0)
    assert (broker.position, broker.cash) == (0, 1000.0)


def test_buy(broker):
    broker.market_order("BUY", 2, 10.0)
    assert (broker.position, broker.cash) == (2, 1000 - 20.0)


def test_sell(broker):
    broker.market_order("SELL", 2, 10.0)
    assert (broker.position, broker.cash) == (-2, 1020.0)


def test_rejects_zero_quant(broker):
    with pytest.raises(ValueError):
        broker.market_order("BUY", 0, 10)


def test_rejects_negative_quant(broker):
    with pytest.raises(ValueError):
        broker.market_order("BUY", -1, 10)


def test_assert_zero_cash(broker):
    broker.market_order("BUY", 10, 100.0)
    assert (broker.position, broker.cash) == (10, 0)


def test_buy_at_zero(broker):
    broker.market_order("BUY", 10, 100.0)
    assert (broker.position, broker.cash) == (10, 0)
    with pytest.raises(Exception) as e:
        broker.market_order("BUY", 200, 10.0)
    assert str(e.value) == "Not Enough Cash"


def test_sell_at_zero(broker):
    broker.market_order("BUY", 10, 100.0)
    assert (broker.position, broker.cash) == (10, 0)
    broker.market_order("SELL", 10, 50)
    assert (broker.position, broker.cash) == (0, 500)


def test_sell_at_zero_then_buy(broker):
    broker.market_order("BUY", 10, 100.0)
    assert (broker.position, broker.cash) == (10, 0)
    broker.market_order("SELL", 10, 50)
    assert (broker.position, broker.cash) == (0, 500)
    broker.market_order("BUY", 5, 50)
    assert (broker.position, broker.cash) == (5, 250)


def test_rejects_insufficient_cash(broker):
    with pytest.raises(Exception) as e:
        broker.market_order("BUY", 200, 10.0)
    assert str(e.value) == "Not Enough Cash"
