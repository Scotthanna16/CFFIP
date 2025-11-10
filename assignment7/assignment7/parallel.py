import multiprocessing as mp
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

import numpy as np
import pandas as pd
import psutil

from data_loader import load_data_pandas

"""
Even though the GIL prevents parrallelism, the Threads perform better here because they share the same memory
Market_data is a pretty big file, and for the processes there is a lot of copying going on which is slowing down
execution (because every process has to copy the data for that ticker). Multiprocessing is goign to work better
when less copying is needed, and the computations are more complicated. Because computing the rolling average is 
fairly inexpensive and pandas has a nice implementation, the amount of time saved in computation for Multiprocessing
is minimal compared to the amount of time lost copying.

CPU usage is printed: Generally, CPU usage goes up for multiprocessing which makes sense, 
memory and runtime are computed in main/reporting
"""


def log_resource_usage(note=""):
    time.sleep(0.1)
    cpu_usage = psutil.cpu_percent(interval=0.1)
    print(f"[{note}] CPU: {cpu_usage:.6f}%")


def get_performance_metrics(df: pd.DataFrame) -> pd.DataFrame:
    log_resource_usage("Current Usage:")
    temp = pd.DataFrame()
    temp["return"] = df["price"].pct_change()
    temp["ma20"] = temp["return"].rolling(20, min_periods=1).mean()
    temp["std20"] = temp["return"].rolling(20, min_periods=1).std()
    temp["sharpe20"] = temp["ma20"].div(temp["std20"].replace(0, np.nan))

    return temp


def compute_with_threads(df: pd.DataFrame):
    print("Threads:")
    results = []
    with ThreadPoolExecutor() as executor:
        for _, subdf in df.groupby("symbol"):
            results.append(executor.submit(get_performance_metrics, subdf))
        results = [res.result() for res in results]
    return results


def compute_with_processes(df: pd.DataFrame):
    print("MultiProcess:")
    results = []
    with ProcessPoolExecutor(mp.cpu_count()) as executor:
        for _, subdf in df.groupby("symbol"):
            results.append(executor.submit(get_performance_metrics, subdf))
        results = [res.result() for res in results]
    return results


# if __name__ == "__main__":
#     df_pandas = load_data_pandas()
#     res = compute_with_threads(df_pandas)
#     res2 = compute_with_processes(df_pandas)
#     # print(res)
#     # print(res2)
