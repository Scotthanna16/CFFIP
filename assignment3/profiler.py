# # import data_loader
# # import strategies
# # import matplotlib.pyplot as plt
# # import timeit
# # import tracemalloc

# # # === Helper Functions ===


# # def measure_performance(func, n):
# #     """
# #     Measure execution time and peak memory (Python allocations only)
# #     """
# #     tracemalloc.start()
# #     func(n)
# #     current, peak = tracemalloc.get_traced_memory()
# #     tracemalloc.stop()
# #     return peak / 1024**2  # convert bytes to MB


# # def time_Naive(n):
# #     strat = strategies.NaiveMovingAverageStrategy()
# #     for tick in data_points[:n]:
# #         strat.generate_signals(tick)


# # def time_Optimized(n):
# #     strat = strategies.OptimizedNaiveMovingAverageStrategy()
# #     for tick in data_points[:n]:
# #         strat.generate_signals(tick)


# # def time_Windowed(n):
# #     strat = strategies.WindowedMovingAverageStrategy()
# #     for tick in data_points[:n]:
# #         strat.generate_signals(tick)


# # def time_OptimizedWindowed(n):
# #     strat = strategies.OptimizedWindowedMovingAverageStrategy()
# #     for tick in data_points[:n]:
# #         strat.generate_signals(tick)


# # if __name__ == "__main__":
# #     data_points = data_loader.load_market_data()

# #     input_sizes = [1000, 5000, 10000, 20000, 50000, 100000]

# #     naive_times = []
# #     optimized_times = []
# #     windowed_times = []
# #     windowed_optimized_times = []

# #     naive_mem = []
# #     optimized_mem = []
# #     windowed_mem = []
# #     windowed_optimized_mem = []

# #     for size in input_sizes:
# #         print(f"Finding time for size: {size}")
# #         naive_times.append(timeit.Timer(lambda: time_Naive(size)).timeit(number=1))
# #         optimized_times.append(
# #             timeit.Timer(lambda: time_Optimized(size)).timeit(number=1)
# #         )
# #         windowed_times.append(
# #             timeit.Timer(lambda: time_Windowed(size)).timeit(number=1)
# #         )
# #         windowed_optimized_times.append(
# #             timeit.Timer(lambda: time_OptimizedWindowed(size)).timeit(number=1)
# #         )
# #         print()

# #     for size in input_sizes:
# #         print(f"\nRunning for input size: {size}")

# #         m = measure_performance(time_Naive, size)
# #         naive_mem.append(m)

# #         m = measure_performance(time_Optimized, size)
# #         optimized_mem.append(m)

# #         m = measure_performance(time_Windowed, size)
# #         windowed_mem.append(m)

# #         m = measure_performance(time_OptimizedWindowed, size)
# #         windowed_optimized_mem.append(m)
# #         print()

# #     plt.figure(figsize=(8, 5))
# #     plt.figure(figsize=(8, 5))
# #     plt.plot(input_sizes, naive_times, marker="o", label="Naive MA")
# #     plt.plot(input_sizes, optimized_times, marker="o", label="Optimized Naive MA")
# #     plt.plot(input_sizes, windowed_times, marker="o", label="Windowed MA")
# #     plt.plot(
# #         input_sizes, windowed_optimized_times, marker="o", label="Optimized Windowed MA"
# #     )
# #     plt.xlabel("Input Size")
# #     plt.ylabel("Time (seconds)")
# #     plt.title("Execution Time vs Input Size for Each Strategy (log Y-axis)")
# #     plt.legend()
# #     # plt.xscale("log")
# #     plt.yscale("log")
# #     plt.grid(True)

# #     plt.savefig("time.png", dpi=300)
# #     plt.show()
# #     plt.close()

# #     plt.figure(figsize=(8, 5))
# #     plt.plot(input_sizes, naive_mem, marker="o", label="Naive (mem)")
# #     plt.plot(input_sizes, optimized_mem, marker="o", label="Optimized (mem)")
# #     plt.plot(input_sizes, windowed_mem, marker="o", label="Windowed (mem)")
# #     plt.plot(
# #         input_sizes,
# #         windowed_optimized_mem,
# #         marker="o",
# #         label="Optimized Windowed (mem)",
# #     )
# #     plt.xlabel("Input Size")
# #     plt.ylabel("Peak Memory (MB)")
# #     # plt.xscale("log")
# #     plt.legend()
# #     plt.grid(True)
# #     plt.title("Peak Memory vs Input Size")
# #     plt.savefig("memory.png", dpi=300)

# #     plt.show()


# import timeit
# import cProfile
# import pstats
# from memory_profiler import memory_usage
# from strategies import (
#     NaiveMovingAverageStrategy,
#     OptimizedNaiveMovingAverageStrategy,
#     WindowedMovingAverageStrategy,
#     OptimizedWindowedMovingAverageStrategy,
# )
# from data_loader import load_market_data_generator, load_market_data
# import matplotlib.pyplot as plt
# import numpy as np


# class StrategyProfiler:
#     def __init__(self):
#         self.__results = {}

#     def timeit_benchmark(self, strat, n, repeats=None):
#         if repeats is None:
#             repeats = 3 if n <= 10000 else 1  # Adaptive: fewer for large n to save time

#         s = strat()

#         data = load_market_data_generator()

#         def task():
#             for _ in range(n):
#                 s.generate_signals(next(data))

#         t = timeit.Timer(task)
#         time_taken = t.timeit(number=repeats) / repeats
#         return time_taken

#     def memory_benchmark(self, strat, n):
#         data = load_market_data_generator()

#         def task(args):
#             s = strat()
#             for _ in range(n):
#                 s.generate_signals(next(data))

#         mem_usage = memory_usage((task, (None,), {}), max_iterations=1, interval=0.01)
#         peak_mem = max(mem_usage)  # in MB
#         return peak_mem

#     def cprofile_benchmark(self, strat, n_ticks, output_file=None):
#         data = load_market_data_generator()

#         def workload():
#             strategy = strat()
#             for _ in range(n_ticks):
#                 tick = next(data)
#                 strategy.generate_signals(tick)

#         pr = cProfile.Profile()
#         pr.enable()
#         workload()
#         pr.disable()

#         if output_file:
#             pr.dump_stats(output_file)

#         stats = pstats.Stats(pr)
#         stats.sort_stats("cumtime")
#         print(f"\nTop 5 hotspots for {strat.__name__} (n={n_ticks}):")
#         stats.print_stats(5)  # Limit to top 5 for brevity
#         return stats

#     def profile(self, strat, sizes):
#         self.__results[strat.__name__] = {
#             "time": {},
#             "memory": {},
#             "cprofile": None,
#         }

#         for size in sizes:
#             t = self.timeit_benchmark(strat, size)
#             self.__results[strat.__name__]["time"][size] = t
#             m = self.memory_benchmark(strat, size)
#             self.__results[strat.__name__]["memory"][size] = m

#         max_size = max(sizes)
#         cp_stats = self.cprofile_benchmark(
#             strat, max_size, output_file=f"{strat.__name__}_{max_size}.prof"
#         )
#         self.__results[strat.__name__]["cprofile"] = cp_stats
#         return self.__results[strat.__name__]

#     @property
#     def results(self):
#         return self.__results


# def plot_results(results):
#     input_sizes = sorted(next(iter(results.values()))["time"].keys())  # Dynamic sizes
#     strategy_names = list(results.keys())
#     colors = plt.cm.Set1(np.linspace(0, 1, len(strategy_names)))

#     # Runtime plot (semilogy for scaling)
#     plt.figure(figsize=(10, 6))
#     for i, strat_name in enumerate(strategy_names):
#         sizes = list(results[strat_name]["time"].keys())
#         times = list(results[strat_name]["time"].values())
#         if sizes:
#             plt.semilogy(
#                 sizes, times, marker="o", linewidth=2, label=strat_name, color=colors[i]
#             )

#     plt.xlabel("Input Size (ticks)", fontsize=12)
#     plt.ylabel("Execution Time (seconds)", fontsize=12)
#     plt.title("Runtime Scaling (log y-axis)", fontsize=14)
#     plt.grid(True, alpha=0.3)
#     plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
#     plt.tight_layout()
#     runtime_plot = "runtime_scaling.png"
#     plt.savefig(runtime_plot, dpi=300, bbox_inches="tight")
#     plt.show()
#     plt.close()

#     # Memory plot (linear)
#     plt.figure(figsize=(10, 6))
#     for i, strat_name in enumerate(strategy_names):
#         sizes = list(results[strat_name]["memory"].keys())
#         mems = list(results[strat_name]["memory"].values())
#         if sizes:
#             plt.plot(
#                 sizes, mems, marker="s", linewidth=2, label=strat_name, color=colors[i]
#             )

#     plt.xlabel("Input Size (ticks)", fontsize=12)
#     plt.ylabel("Peak Memory Usage (MB)", fontsize=12)
#     plt.title("Memory Scaling", fontsize=14)
#     plt.grid(True, alpha=0.3)
#     plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
#     plt.tight_layout()
#     memory_plot = "memory_scaling.png"
#     plt.savefig(memory_plot, dpi=300, bbox_inches="tight")
#     plt.show()
#     plt.close()

#     return runtime_plot, memory_plot


# def main():
#     print("Loading data...")
#     data_points = load_market_data()
#     print(f"Loaded {len(data_points)} points")

#     profiler = StrategyProfiler()

#     strategies_dict = {
#         "Naive": NaiveMovingAverageStrategy,
#         "OptimizedNaive": OptimizedNaiveMovingAverageStrategy,
#         "Windowed": WindowedMovingAverageStrategy,
#         "OptimizedWindowed": OptimizedWindowedMovingAverageStrategy,
#     }

#     input_sizes = [1000, 5000, 10000, 20000, 50000, 100000]

#     for name, strat in strategies_dict.items():
#         print(f"\n=== Profiling {name} ===")
#         profiler.profile(strat, input_sizes)

#     runtime_plot, memory_plot = plot_results(profiler.results)
#     print(f"Plots saved: {runtime_plot}, {memory_plot}")


# if __name__ == "__main__":
#     main()


# quick test
import gc
from memory_profiler import profile, memory_usage
from strategies import (
    NaiveMovingAverageStrategy,
    OptimizedNaiveMovingAverageStrategy,
    WindowedMovingAverageStrategy,
    OptimizedWindowedMovingAverageStrategy,
)
from data_loader import load_market_data_generator
import tracemalloc
from line_profiler import LineProfiler
import matplotlib.pyplot as plt
import numpy as np

# for printing json
import json

SIZES = [1000, 5000, 10000, 20000, 50000, 100000]


class StrategyProfiler:
    def __init__(self):
        self.__results = {}

    @property
    def results(self):
        return self.__results

    def test_memory(self, strategy_class, nticks):
        strategy = strategy_class()
        data_gen = load_market_data_generator()
        for _ in range(nticks):
            tick = next(data_gen)
            strategy.generate_signals(tick)

        return strategy

    def test_time(self, strategy_class, nticks):
        import timeit

        strategy = strategy_class()
        data_gen = load_market_data_generator()

        def task():
            for _ in range(nticks):
                tick = next(data_gen)
                strategy.generate_signals(tick)

        t = timeit.Timer(task)
        time_taken = t.timeit(number=1)
        return time_taken

    def run(self):

        strategies = [
            NaiveMovingAverageStrategy,
            OptimizedNaiveMovingAverageStrategy,
            WindowedMovingAverageStrategy,
            OptimizedWindowedMovingAverageStrategy,
        ]
        # initialize results dict
        self.__results = {
            strat.__name__: {"memory": {}, "runtime": {}} for strat in strategies
        }
        tracemalloc.start()
        sizes = SIZES
        for size in sizes:
            for strat in strategies:
                print(f"\nTesting {strat.__name__}...")
                self.test_memory(strat, size)
                current, peak = tracemalloc.get_traced_memory()
                print(
                    f"Current memory usage for {strat.__name__}: {current / 1024**2:.2f} MB; Peak: {peak / 1024**2:.2f} MB"
                )
                self.__results[strat.__name__]["memory"][size] = peak / 1024**2
                tracemalloc.reset_peak()

        for size in sizes:
            for strat in strategies:
                gc.collect()
                print(f"\nTiming {strat.__name__}...")
                t = self.test_time(strat, size)
                self.__results[strat.__name__]["runtime"][size] = t
                print(f"Completed timing for {strat.__name__} with {size} ticks")

        tracemalloc.stop()

        return self.__results

    def plot_results(self):

        input_sizes = sorted(next(iter(self.__results.values()))["runtime"].keys())
        strategy_names = list(self.__results.keys())
        colors = plt.cm.Set1(np.linspace(0, 1, len(strategy_names)))  # type: ignore

        # Runtime plot (semilogy for scaling / easier to see)
        plt.figure(figsize=(10, 6))
        for i, strat_name in enumerate(strategy_names):
            sizes = list(self.__results[strat_name]["runtime"].keys())
            times = list(self.__results[strat_name]["runtime"].values())
            if sizes:
                plt.semilogy(
                    sizes,
                    times,
                    marker="o",
                    linewidth=2,
                    label=strat_name,
                    color=colors[i],
                )

        plt.xlabel("Input Size (ticks)", fontsize=12)
        plt.ylabel("Execution Time (seconds)", fontsize=12)
        plt.title("Runtime Scaling (log y-axis)", fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()
        runtime_plot = "runtime_scaling.png"
        plt.savefig(runtime_plot, dpi=300, bbox_inches="tight")
        plt.show()
        plt.close()

        # Memory plot (linear)
        plt.figure(figsize=(10, 6))
        for i, strat_name in enumerate(strategy_names):
            sizes = list(self.__results[strat_name]["memory"].keys())
            mems = list(self.__results[strat_name]["memory"].values())
            if sizes:
                plt.plot(
                    sizes,
                    mems,
                    marker="s",
                    linewidth=2,
                    label=strat_name,
                    color=colors[i],
                )

        plt.xlabel("Input Size (ticks)", fontsize=12)
        plt.ylabel("Peak Memory Usage (MB)", fontsize=12)
        plt.title("Memory Scaling", fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()
        memory_plot = "memory_scaling.png"
        plt.savefig(memory_plot, dpi=300, bbox_inches="tight")
        plt.show()
        plt.close()

        return runtime_plot, memory_plot


if __name__ == "__main__":
    profiler = StrategyProfiler()
    results = profiler.run()
    # dump results to json
    with open("profiling_results.json", "w") as f:
        json.dump(results, f, indent=4)
    print("\nProfiling results saved to profiling_results.json")
    runtime_plot, memory_plot = profiler.plot_results()
    print(f"Plots saved: {runtime_plot}, {memory_plot}")
