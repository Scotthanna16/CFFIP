import pytest
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

# Import your functions
from parallel import (
    get_performance_metrics,
    compute_with_threads,
    compute_with_processes,
)


# ---- MOCK UTILS ----
def mock_log_resource_usage(msg):
    pass


# ---- FIXTURES ----
@pytest.fixture
def sample_df():
    """Creates a dummy DataFrame with multiple symbols and 50 price points each."""
    np.random.seed(42)
    data = {
        "symbol": np.repeat(["AAPL", "MSFT"], 50),
        "price": np.concatenate(
            [
                np.linspace(100, 150, 50) + np.random.randn(50),
                np.linspace(200, 250, 50) + np.random.randn(50),
            ]
        ),
    }
    return pd.DataFrame(data)


@pytest.fixture
def single_symbol_df():
    """DataFrame with one symbol only."""
    np.random.seed(0)
    prices = np.linspace(100, 120, 50) + np.random.randn(50)
    return pd.DataFrame({"symbol": "AAPL", "price": prices})


# ---- UNIT TESTS ----


def test_get_performance_metrics_shape(single_symbol_df):
    """Ensure returned DataFrame has correct columns and shape."""
    result = get_performance_metrics(single_symbol_df)

    assert set(result.columns) == {"return", "ma20", "std20", "sharpe20"}
    assert len(result) == len(single_symbol_df)


def test_parallel_thread_and_process_output(sample_df, monkeypatch):
    """Ensure thread and process versions return same results."""

    thread_results = compute_with_threads(sample_df)
    process_results = compute_with_processes(sample_df)

    # Check both return two results (one per symbol)
    assert len(thread_results) == len(process_results) == 2

    # Compare corresponding DataFrames' last 10 rows
    for t_res, p_res in zip(thread_results, process_results):
        pd.testing.assert_frame_equal(
            t_res.tail(10).reset_index(drop=True),
            p_res.tail(10).reset_index(drop=True),
            check_exact=False,
            atol=1e-8,
        )


def test_handles_constant_prices(monkeypatch):
    df = pd.DataFrame({"symbol": "AAPL", "price": np.ones(50)})

    result = get_performance_metrics(df)
    assert result["std20"].isna().any() or (result["std20"] == 0).any()
    assert result["sharpe20"].isna().all()


def test_handles_empty_df(monkeypatch):
    """Gracefully handle empty input."""
    df = pd.DataFrame({"symbol": [], "price": []})
    result = get_performance_metrics(df)
    assert result.empty


def test_consistency_of_parallel_results(monkeypatch, sample_df):
    """Threaded and multiprocess results should match sequential logic."""

    # Compute sequentially
    baseline = [get_performance_metrics(sub) for _, sub in sample_df.groupby("symbol")]

    # Compute with threads
    threaded = compute_with_threads(sample_df)
    processed = compute_with_processes(sample_df)

    for b, t, p in zip(baseline, threaded, processed):
        pd.testing.assert_frame_equal(
            b.tail(10).reset_index(drop=True), t.tail(10).reset_index(drop=True)
        )
        pd.testing.assert_frame_equal(
            b.tail(10).reset_index(drop=True), p.tail(10).reset_index(drop=True)
        )
