# portfolio.py: aggregates portfolio metrics
import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import Mapping

import numpy as np
import polars as pl

from data_loader import load_data_polars


@dataclass(frozen=True)
class Position:
    symbol: str
    quantity: int
    price: float


def parse_position(data: Mapping) -> Position:
    """Parse position data into a Position object"""

    return Position(
        symbol=data["symbol"],
        quantity=int(data["quantity"]),
        price=float(data["price"]),
    )


def position_metrics(position: Position, data: pl.Series) -> dict:
    """computes position metrics from provided position and market data"""

    if data.is_empty():
        raise ValueError(f"No market data found for symbol: {position.symbol}")

    rets = data.pct_change().drop_nulls()
    vol = rets.rolling_std(window_size=20).mean()
    max_drawdown = ((data - data.cum_max()) / data.cum_max()).min()

    value = position.quantity * data[-1]

    return {
        "symbol": position.symbol,
        "value": value,
        "volatility": vol,
        "drawdown": max_drawdown,
    }


def _init_metrics(portfolio) -> dict:
    name = portfolio.get("name", "unamed")
    owner = portfolio.get("owner", "unknown")
    metrics = {
        "name": name,
        "owner": owner,
        "total_value": 0.0,
        "aggregate_volatility": 0.0,
        "max_drawdown": 0.0,
        "positions": [],
        "sub_portfolios": [],
    }
    return metrics


def _process_positions(
    portfolio: dict, metrics: dict, df: pl.DataFrame
) -> tuple[float, float]:

    tot_val: pl.Series | None = None

    for pos_data in portfolio.get("positions", []):
        position = parse_position(pos_data)
        data = (
            df.filter(pl.col("symbol") == position.symbol).select("price").to_series()
        )
        if tot_val is None:
            tot_val = data * position.quantity
        else:
            tot_val += data * position.quantity
        pos_metrics = position_metrics(position, data)
        metrics["positions"].append(pos_metrics)
        metrics["total_value"] += pos_metrics["value"]
        metrics["aggregate_volatility"] += (
            pos_metrics["volatility"] * pos_metrics["value"]
        )

    return tot_val


def _process_subportfolios(
    portfolio: dict, metrics: dict, df: pl.DataFrame, tot_val
) -> float:

    for sub_portfolio in portfolio.get("sub_portfolios", []):
        sub_metrics, sub_val = aggregate_portfolio_metrics_s(sub_portfolio, df)
        tot_val += sub_val
        metrics["sub_portfolios"].append(sub_metrics)
        metrics["total_value"] += sub_metrics["total_value"]
        metrics["aggregate_volatility"] += (
            sub_metrics["aggregate_volatility"] * sub_metrics["total_value"]
        )

    return tot_val


def _cleanup_metrics(metrics: dict, tot_val: float) -> dict:
    if metrics["total_value"] > 0:
        metrics["aggregate_volatility"] /= metrics["total_value"]
    else:
        metrics["aggregate_volatility"] = 0.0

    rets = tot_val.pct_change().drop_nulls()
    if not rets.is_empty():
        metrics["max_drawdown"] = (
            (tot_val - tot_val.cum_max()) / tot_val.cum_max()
        ).min()

    return metrics


def aggregate_portfolio_metrics_s(portfolio, df: pl.DataFrame) -> dict:
    """Aggregates metrics across all positions and subportfolios in the portfolio."""

    metrics = _init_metrics(portfolio)
    tot_val = _process_positions(portfolio, metrics, df)
    tot_val = _process_subportfolios(portfolio, metrics, df, tot_val)
    metrics = _cleanup_metrics(metrics, tot_val)

    return metrics, tot_val


def _process_positions_parallel(
    portfolio: dict, df: pl.DataFrame
) -> tuple[dict, pl.Series]:
    metrics = []
    tot_val: pl.Series | None = None

    positions = portfolio.get("positions", [])
    with ProcessPoolExecutor() as executor:
        futures = []
        for pos_data in positions:
            position = parse_position(pos_data)
            data = (
                df.filter(pl.col("symbol") == position.symbol)
                .select("price")
                .to_series()
            )
            futures.append(
                (executor.submit(position_metrics, position, data), position, data)
            )

        for future, position, data in futures:
            pos_metrics = future.result()
            metrics.append(pos_metrics)
            if tot_val is None:
                tot_val = data * position.quantity
            else:
                tot_val += data * position.quantity

    return metrics, tot_val


def aggregate_portfolio_metrics(portfolio, df: pl.DataFrame) -> dict:
    """Wrapper to aggregate portfolio metrics using multiprocessing."""

    metrics = _init_metrics(portfolio)
    pos_metrics, tot_val = _process_positions_parallel(portfolio, df)
    metrics["positions"] = pos_metrics

    # Aggregate position-level totals into the portfolio metrics
    # NOTE: kinda confused here cause i thought i was already doing this in _process_positions_parallel
    # clearly something is off
    # pos_metrics is a list of dicts with keys: value, volatility, etc.
    for pm in pos_metrics:
        try:
            val = float(pm.get("value", 0.0))
        except Exception:
            val = 0.0
        try:
            vol = float(pm.get("volatility", 0.0))
        except Exception:
            vol = 0.0

        metrics["total_value"] += val
        metrics["aggregate_volatility"] += vol * val

    tot_val = _process_subportfolios(portfolio, metrics, df, tot_val)
    metrics = _cleanup_metrics(metrics, tot_val)

    return metrics, tot_val


if __name__ == "__main__":

    data = load_data_polars("market_data-1.csv")

    portfolio = json.load(open("portfolio_structure.json", "r"))

    metrics, _ = aggregate_portfolio_metrics_s(portfolio, data)
    print(json.dumps(metrics, indent=2))

    metrics_mp, _ = aggregate_portfolio_metrics(portfolio, data)
    print(json.dumps(metrics_mp, indent=2))
