import pytest
import pandas as pd
import polars as pl
import numpy as np
from data_loader import load_data_pandas
from metrics import compute_pandas_metrics, compute_polars_metrics  # adjust import


@pytest.fixture
def sample_data():
    # Two symbols, each with 30 timestamps
    np.random.seed(42)
    timestamps = pd.date_range("2023-01-01", periods=30, freq="D")
    data = []
    for symbol in ["AAPL", "MSFT"]:
        prices = np.linspace(100, 130, 30) + np.random.normal(0, 1, 30)
        for t, p in zip(timestamps, prices):
            data.append({"timestamp": t, "symbol": symbol, "price": p})
    df_pandas = pd.DataFrame(data)
    df_polars = pl.DataFrame(df_pandas)
    return df_pandas, df_polars


def test_compute_pandas_metrics_structure(sample_data):
    df_pandas, _ = sample_data
    result_df, elapsed = compute_pandas_metrics(df_pandas.copy())

    # Check columns
    expected_cols = {
        "timestamp",
        "symbol",
        "price",
        "return",
        "ma20",
        "std20",
        "sharpe20",
    }
    assert expected_cols.issubset(result_df.columns), "Missing expected columns"

    # Check types and length
    assert isinstance(result_df, pd.DataFrame)
    assert len(result_df) == len(df_pandas)
    assert elapsed >= 0

    # Check some known properties
    assert result_df["return"].isna().sum() == 2  # one NaN per symbol at start


def test_compute_polars_metrics_structure(sample_data):
    _, df_polars = sample_data
    result_df, elapsed = compute_polars_metrics(df_polars.clone())

    # Check columns
    expected_cols = {"timestamp", "symbol", "return", "ma20", "std20", "sharpe20"}
    assert expected_cols.issubset(result_df.columns), "Missing expected columns"

    # Check types and length
    assert isinstance(result_df, pl.DataFrame)
    assert result_df.height == df_polars.height
    assert elapsed >= 0


def test_pandas_vs_polars_consistency(sample_data):
    df_pandas, df_polars = sample_data

    pandas_df, _ = compute_pandas_metrics(df_pandas.copy())
    polars_df, _ = compute_polars_metrics(df_polars.clone())

    # Convert Polars -> Pandas for comparison
    polars_df = polars_df.to_pandas()

    # Sort and align
    pandas_df = pandas_df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    polars_df = polars_df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)

    for symbol in ["AAPL", "MSFT"]:
        pd_last10 = (
            pandas_df[pandas_df["symbol"] == symbol].tail(10).reset_index(drop=True)
        )
        pl_last10 = (
            polars_df[polars_df["symbol"] == symbol].tail(10).reset_index(drop=True)
        )

        # Round for floating-point stability before equality
        pd_last10_rounded = pd_last10[["ma20", "std20", "sharpe20"]].round(6)
        pl_last10_rounded = pl_last10[["ma20", "std20", "sharpe20"]].round(6)

        pd.testing.assert_frame_equal(
            pd_last10_rounded,
            pl_last10_rounded,
            check_dtype=False,
            check_exact=False,
            atol=1e-6,
            obj=f"Last 10 rows differ for {symbol}",
        )


def test_constant_price_data():
    timestamps = pd.date_range("2023-01-01", periods=50)
    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "symbol": ["AAPL"] * 50,
            "price": [100.0] * 50,
        }
    )
    pl_df = pl.DataFrame(df)

    pd_res, _ = compute_pandas_metrics(df.copy())
    pl_res, _ = compute_polars_metrics(pl_df.clone())
    pl_res = pl_res.to_pandas()

    pd_last10 = pd_res.tail(10)
    pl_last10 = pl_res.tail(10)

    np.testing.assert_allclose(pd_last10["ma20"].fillna(0), 0)
    np.testing.assert_allclose(pl_last10["ma20"].fillna(0), 0)
    np.testing.assert_allclose(pd_last10["std20"].fillna(0), 0)
    np.testing.assert_allclose(pl_last10["std20"].fillna(0), 0)


def test_increasing_prices_positive_mean():
    timestamps = pd.date_range("2023-01-01", periods=50)
    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "symbol": ["AAPL"] * 50,
            "price": np.linspace(100, 200, 50),
        }
    )
    pd_res, _ = compute_pandas_metrics(df.copy())
    last10 = pd_res.tail(10)
    assert (last10["ma20"] > 0).all()


# if __name__ == "__main__":
#     pandasdf, polarsdf = sample_data()
#     test_pandas_vs_polars_consistency(pandasdf, polarsdf)
