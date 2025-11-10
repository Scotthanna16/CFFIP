from data_loader import load_data_pandas, load_data_polars
import pandas as pd
import polars as pl
import numpy as np
import matplotlib.pyplot as plt
import time


def compute_pandas_metrics(df_pandas: pd.DataFrame) -> tuple[pd.DataFrame, float]:

    start = time.time()

    df_pandas["return"] = df_pandas.groupby("symbol")["price"].pct_change()
    df_pandas["ma20"] = df_pandas.groupby("symbol")["return"].transform(
        lambda x: x.rolling(20, min_periods=1).mean()
    )
    df_pandas["std20"] = df_pandas.groupby("symbol")["return"].transform(
        lambda x: x.rolling(20, min_periods=1).std()
    )
    df_pandas["sharpe20"] = df_pandas["ma20"] / df_pandas["std20"]

    elapsed = time.time() - start
    print(f"Pandas rolling metrics time: {elapsed:.4f} sec")

    df_pandas = df_pandas.reset_index()
    return df_pandas, elapsed


def compute_polars_metrics(df_polars: pl.DataFrame) -> tuple[pl.DataFrame, float]:
    start = time.time()

    df_polars = (
        df_polars.with_columns(
            (pl.col("price").pct_change().over("symbol")).alias("return")
        )
        .group_by("symbol", maintain_order=True)
        .agg(
            [
                pl.col("timestamp"),
                pl.col("return"),
                pl.col("return").rolling_mean(window_size=20).alias("ma20"),
                pl.col("return").rolling_std(window_size=20).alias("std20"),
            ]
        )
        .explode(["timestamp", "return", "ma20", "std20"])
        .with_columns((pl.col("ma20") / pl.col("std20")).alias("sharpe20"))
    )

    elapsed = time.time() - start
    print(f"Polars rolling metrics time: {elapsed:.4f} sec")

    return df_polars, elapsed


def compare_rolling_returns(
    df_pandas: pd.DataFrame, df_polars: pl.DataFrame, symbol: str = "AAPL"
):
    # --- Filter and prepare Pandas data ---
    df_pd = df_pandas[df_pandas["symbol"] == symbol].copy()
    df_pd = df_pd.sort_values("timestamp")

    # --- Filter and prepare Polars data ---
    df_pl = (
        df_polars.filter(pl.col("symbol") == symbol)
        .sort("timestamp")
        .select(["timestamp", "return", "ma20"])
        .to_pandas()
    )

    # --- Plot comparison ---
    plt.figure(figsize=(12, 6))
    plt.plot(
        df_pd["timestamp"],
        df_pd["ma20"],
        label="Pandas Rolling Mean (20)",
        color="blue",
    )
    plt.plot(
        df_pl["timestamp"],
        df_pl["ma20"],
        label="Polars Rolling Mean (20)",
        color="red",
        linestyle="--",
    )

    plt.title(f"{symbol} — Rolling 20-Period Mean of Returns (Pandas vs Polars)")
    plt.xlabel("Time")
    plt.ylabel("Return")
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    df_pandas = load_data_pandas()
    df_polars = load_data_polars()

    df_pandas, pandas_time = compute_pandas_metrics(df_pandas)
    df_polars, polars_time = compute_polars_metrics(df_polars)

    print(df_pandas)
    # compare_rolling_returns(df_pandas, df_polars, symbol="AAPL")

    # print("\nPerformance Summary:")
    # print(f"Pandas Time: {pandas_time:.4f} sec")
    # print(f"Polars Time: {polars_time:.4f} sec")
