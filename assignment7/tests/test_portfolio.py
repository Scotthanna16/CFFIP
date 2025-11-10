import math

import polars as pl

from portfolio import (
    Position,
    aggregate_portfolio_metrics,
    aggregate_portfolio_metrics_s,
    position_metrics,
)


def _make_df():
    # 25 time steps for two symbols (AAPL, MSFT)
    prices_a = [100.0 + i * 0.5 for i in range(25)]
    prices_b = [200.0 + i * 1.0 for i in range(25)]

    symbols = []
    prices = []
    for i in range(25):
        symbols.append("AAPL")
        prices.append(prices_a[i])
        symbols.append("MSFT")
        prices.append(prices_b[i])

    return pl.DataFrame({"symbol": symbols, "price": prices})


def test_position_metrics_simple():
    df = _make_df()
    series = df.filter(pl.col("symbol") == "AAPL").select("price").to_series()

    last_price = float(series[-1])
    pos = Position(symbol="AAPL", quantity=10, price=last_price)

    res = position_metrics(pos, series)

    assert res["symbol"] == "AAPL"
    assert math.isclose(res["value"], 10 * last_price, rel_tol=1e-9)
    # volatility and drawdown should be numeric scalars
    assert isinstance(res["volatility"], (float, int))
    assert isinstance(res["drawdown"], (float, int))


def test_aggregate_portfolio_metrics_simple():
    df = _make_df()

    portfolio = {
        "name": "Test Portfolio",
        "positions": [
            {"symbol": "AAPL", "quantity": 10, "price": 0},
            {"symbol": "MSFT", "quantity": 5, "price": 0},
        ],
        "sub_portfolios": [],
    }

    metrics_s, _ = aggregate_portfolio_metrics_s(portfolio, df)
    metrics_p, _ = aggregate_portfolio_metrics(portfolio, df)

    last_a = float(
        df.filter(pl.col("symbol") == "AAPL").select("price").to_series()[-1]
    )
    last_b = float(
        df.filter(pl.col("symbol") == "MSFT").select("price").to_series()[-1]
    )
    expected = 10 * last_a + 5 * last_b

    # total_value should match expected last-price valuation
    assert math.isclose(metrics_s["total_value"], expected, rel_tol=1e-9)
    assert math.isclose(metrics_p["total_value"], expected, rel_tol=1e-6)

    # sequential and multiprocessing results should be close
    assert math.isclose(
        metrics_s["total_value"], metrics_p["total_value"], rel_tol=1e-6
    )
