# Performance Report

## Function Performance Metrics

| Function | Time (sec) | Memory (MiB) |
|----------|------------|---------------|
| load_data_pandas | 0.115184 | 282.23 |
| load_data_polars | 0.009825 | 325.84 |
| compute_pandas_metrics | 0.084410 | 342.45 |
| compute_polars_metrics | 0.020765 | 427.80 |
| compute_with_threads | 0.243177 | 444.77 |
| compute_with_processes | 1.009937 | 262.95 |
| aggregate_portfolio_metrics_s | 0.021656 | 250.09 |
| aggregate_portfolio_metrics | 0.672543 | 258.14 |

![Performance Comparison](plots/pandas_vs_polars_performance.png)
