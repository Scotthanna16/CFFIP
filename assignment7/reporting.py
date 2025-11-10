"""reporting.py - Generate performance reports comparing different implmentations"""

import multiprocessing as mp
import time
import timeit
from functools import partial, wraps

import matplotlib.pyplot as plt
import memory_profiler
import psutil

from data_loader import load_data_pandas, load_data_polars


class Profiler:
    """Class to profile time and memory usage of functions."""

    def __init__(self):
        self.funcs: dict[str, callable] = {}
        self.results: dict[str, dict[str, float]] = {}

    def add_function(self, name: str, func: callable, *args, **kwargs):
        """Add a function to be profiled."""
        self.funcs[name] = (func, args, kwargs)

    def profile(self, repeats: int = 5):

        for name, (func, args, kwargs) in self.funcs.items():
            # Time profiling
            timer = timeit.Timer(lambda: func(*args, **kwargs))
            time_taken = timer.timeit(number=repeats) / repeats

            # Memory profiling
            mem_usage = memory_profiler.memory_usage(
                (func, args, kwargs), max_usage=True, retval=False
            )

            # cpu usage

            self.results[name] = {"time": time_taken, "memory": mem_usage}

    def report(self):
        """Generate a report of the profiling results."""
        for name, metrics in self.results.items():
            print(
                f"Function: {name} | Time: {metrics['time']:.6f} sec | Memory: {metrics['memory']:.2f} MiB"
            )

    def plot(self, filepath: str = None):
        """
        Plot the profiling results.
        Args:
            filepath (str): If provided, save the plot to this file.
        """
        fig, (ax_time, ax_mem) = plt.subplots(1, 2, figsize=(10, 5))

        time_data = [(name, metrics["time"]) for name, metrics in self.results.items()]
        memory_data = [
            (name, metrics["memory"]) for name, metrics in self.results.items()
        ]

        names_time, times = zip(*time_data)
        names_mem, mems = zip(*memory_data)
        ax_time.bar(names_time, times, color="skyblue")
        ax_time.set_title("Function Execution Time")
        ax_time.set_ylabel("Time (seconds)")

        ax_mem.bar(names_mem, mems, color="salmon")
        ax_mem.set_title("Function Memory Usage")
        ax_mem.set_ylabel("Memory (MiB)")
        # plt.tight_layout()

        # slant x-axis labels for better readability
        for ax in (ax_time, ax_mem):
            plt.sca(ax)
            plt.xticks(rotation=45, ha="right")

        # plt.legend()
        # make sure axis labels are not cut off
        plt.tight_layout()
        # plt.show()

        if filepath:
            plt.savefig(filepath)
        else:
            plt.show()


if __name__ == "__main__":
    # profiler = Profiler()
    # profiler.add_function(
    #     "Load Pandas", load_data_pandas, file_path="market_data-2.csv"
    # )
    # profiler.add_function(
    #     "Load Polars", load_data_polars, file_path="market_data-2.csv"
    # )

    # profiler.profile(repeats=3)
    # profiler.report()
    # profiler.plot()
    p = psutil.Process()
    p1 = p.cpu_percent()
    for _ in range(20):
        ...
    p2 = p.cpu_percent()

    print(f"CPU percent: {p1:.3f}")
    print(f"CPU percent: {p2:.3f}")
