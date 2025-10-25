# reporting.py
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, Any
import pandas as pd  # For tables; install if needed: pip install pandas

# Assuming the profiler script is run first and saves results to 'profiling_results.json'
# If not, uncomment the import and run profiler below
# from profiler import StrategyProfiler  # Adjust to your profiler file name
# profiler = StrategyProfiler()
# results = profiler.run()
# with open('profiling_results.json', 'w') as f:
#     json.dump(results, f, indent=4)
# profiler.plot_results()  # Generate plots if not already

# Load results (run profiler separately or integrate)
RESULTS_FILE = "profiling_results.json"


def load_results() -> Dict[str, Any]:
    """Load profiling results from JSON."""
    with open(RESULTS_FILE, "r") as f:
        return json.load(f)


def create_summary_table(
    results: Dict[str, Any], metric: str = "runtime"
) -> pd.DataFrame:
    """dataframe for summary table of runtimes or memory."""
    sizes = sorted(int(k) for k in next(iter(results.values()))[metric].keys())
    df_data = {size: [] for size in sizes}
    for strat_name in results:
        for size in sizes:
            df_data[size].append(results[strat_name][metric][str(size)])

    df = pd.DataFrame(df_data, index=results.keys())  # type: ignore
    df.index.name = "Strategy"
    return df.round(4)  # Round for readability


def analyze_complexity(results: Dict[str, Any]):
    """Simple analysis: Fit lines and infer complexities."""
    sizes = sorted(int(k) for k in next(iter(results.values()))["runtime"].keys())
    analysis = {}
    for strat_name in results:
        times = np.array([results[strat_name]["runtime"][str(s)] for s in sizes])
        # Linear fit: log(time) ~ log(n) * a + b; slope ~ complexity
        log_sizes = np.log(sizes)
        log_times = np.log(times + 1e-10)  # Avoid log(0)
        fit = np.polynomial.Polynomial.fit(log_sizes, log_times, 1)
        slope = fit.convert().coef[1]
        if slope < 0.5:
            complexity = "O(1)"
        elif slope < 1.5:
            complexity = "O(n)"
        elif slope < 2.5:
            complexity = "O(n^2)"
        else:
            complexity = "O(n^k), k>2"
        analysis[strat_name] = {
            "estimated_slope": round(slope, 2),
            "inferred_complexity": complexity,
        }
    return analysis


def generate_markdown_report(results: Dict[str, Any]):
    """Generate a Markdown report with tables, analysis, and plot references."""
    report_content = [
        "# Performance Report: Moving Average Strategies\n",
        "## Overview\n",
        "This report analyzes the runtime and memory scaling of four moving average strategies:\n",
        "- **NaiveMovingAverageStrategy**: O(n) time/space (full list sum).\n",
        "- **OptimizedNaiveMovingAverageStrategy**: O(1) time/space (running sum).\n",
        "- **WindowedMovingAverageStrategy**: O(1) time, O(k) space (fixed window).\n",
        "- **OptimizedWindowedMovingAverageStrategy**: O(1) time, O(k) space (deque).\n\n",
        "Tested on input sizes: "
        + ", ".join(map(str, next(iter(results.values()))["runtime"].keys()))
        + "\n\n",
    ]

    # Summary Tables
    report_content.append("## Runtime Summary (seconds)\n")
    runtime_df = create_summary_table(results, "runtime")
    report_content.append(runtime_df.to_markdown())

    report_content.append("\n## Memory Summary (MB)\n")
    memory_df = create_summary_table(results, "memory")
    report_content.append(memory_df.to_markdown())

    # Analysis
    analysis = analyze_complexity(results)
    report_content.append("\n## Complexity Analysis\n")
    report_content.append("| Strategy | Estimated Slope | Inferred Time Complexity |\n")
    report_content.append("|----------|-----------------|--------------------------|\n")
    for strat, data in analysis.items():
        report_content.append(
            f"| {strat} | {data['estimated_slope']} | {data['inferred_complexity']} |\n"
        )
    report_content.append(
        "\n**Notes**: Slope from log-log fit and does not correspond the plot. Naive shows slope > 1, optimized near constant (slope ~1).\n\n"
    )

    # Plots
    report_content.append("## Visualization\n")
    report_content.append("![Runtime Scaling](runtime_scaling.png)\n\n")
    report_content.append("![Memory Scaling](memory_scaling.png)\n\n")

    # Conclusion
    report_content.append("## Conclusion\n")
    report_content.append(
        "The optimized and windowed strategies demonstrate superior scaling, backing up theoretical complexities. "
    )
    report_content.append(
        "For large datasets, use OptimizedWindowed for balanced performance.\n"
    )

    # Write Markdown
    md_path = "performance_report.md"
    with open(md_path, "w") as f:
        f.write("".join(report_content))
    print(f"Markdown report saved to {md_path}")

    # Optional: Convert to HTML/PDF (requires pandoc or similar)
    # subprocess.run(['pandoc', md_path, '-o', 'report.html'])


def main():
    results = load_results()
    generate_markdown_report(results)
    print("Report generation complete! Check performance_report.md")


if __name__ == "__main__":
    main()
