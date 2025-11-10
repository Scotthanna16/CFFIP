# main.py: Orchestrates ingestion, computation, and reporting
import json

from data_loader import load_data_pandas, load_data_polars
from metrics import compute_pandas_metrics, compute_polars_metrics
from parallel import compute_with_processes, compute_with_threads
from portfolio import aggregate_portfolio_metrics, aggregate_portfolio_metrics_s
from reporting import Profiler

GENERATE_MARKDOWN = True


def main():

    profiler = Profiler()
    profiler.add_function("load_data_pandas", load_data_pandas)
    profiler.add_function("load_data_polars", load_data_polars)

    pandas_data = load_data_pandas()
    polars_data = load_data_polars()

    profiler.add_function("compute_pandas_metrics", compute_pandas_metrics, pandas_data)
    profiler.add_function("compute_polars_metrics", compute_polars_metrics, polars_data)

    profiler.add_function("compute_with_threads", compute_with_threads, pandas_data)
    profiler.add_function("compute_with_processes", compute_with_processes, pandas_data)

    with open("portfolio_structure.json", "r") as f:
        portfolio = json.load(f)

    profiler.add_function(
        "aggregate_portfolio_metrics_s",
        aggregate_portfolio_metrics_s,
        portfolio,
        polars_data,
    )

    profiler.add_function(
        "aggregate_portfolio_metrics",
        aggregate_portfolio_metrics,
        portfolio,
        polars_data,
    )

    profiler.profile(repeats=3)
    profiler.report()
    profiler.plot("plots/pandas_vs_polars_performance.png")

    # ------------------------------------#
    # Markdown File Generation (optional) #
    # ------------------------------------#

    if GENERATE_MARKDOWN:
        with open("performance_report.md", "w") as f:
            f.write("# Performance Report\n\n")
            f.write("## Function Performance Metrics\n\n")
            f.write("| Function | Time (sec) | Memory (MiB) |\n")
            f.write("|----------|------------|---------------|\n")
            for name, metrics in profiler.results.items():
                f.write(
                    f"| {name} | {metrics['time']:.6f} | {metrics['memory']:.2f} |\n"
                )
            f.write(
                "\n![Performance Comparison](plots/pandas_vs_polars_performance.png)\n"
            )


if __name__ == "__main__":
    main()
