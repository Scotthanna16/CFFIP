# Assignment 3 - Andrew Moukabary & Scott Hanna

## Setup

1. Create and activate a virtual environment (optional but recommended):

```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

2. Install the required packages:

```bash
   pip install -r requirements.txt
```

3. Run the profiler to generate performance data and plots:

```bash
   python profiler.py
```

4. Generate the performance report:

```bash
   python reporting.py
```

## Files

- `strategies.py`: Contains implementations of four moving average strategies.
- `profiler.py`: Profiles the strategies for runtime and memory usage.
- `reporting.py`: Generates a markdown report summarizing the profiling results.
- `performance_report.md`: The generated performance report.
- `models.py`: Contains data models used in the strategies.
- `requirements.txt`: Lists the required Python packages.
- `tests/*`: Unit tests for the strategies and profiler.
