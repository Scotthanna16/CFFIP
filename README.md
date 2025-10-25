# Repo for Computing for Finance in Python assignments

### These assignments were a team effort between myself and @amoukabary
### Assignment 1: 
#### Algorithmic Trading Backtester: 
This project implements a **CSV-based algorithmic trading backtester** in Python. It reads pre-generated market data from CSV files, applies modular trading strategies, simulates order execution, and generates a detailed performance report.  

The system is built with a strong focus on **object-oriented design**, **data immutability**, and **robust error handling**, showcasing how to structure a small but realistic trading engine.  

**Key Features:**  
- Parses market data into immutable `MarketDataPoint` dataclasses  
- Implements a mutable `Order` class for managing trade state  
- Defines an abstract `Strategy` base class with concrete strategy subclasses (e.g., Moving Average, Momentum)  
- Uses lists and dictionaries for time-series buffering and portfolio tracking  
- Handles invalid or failed orders gracefully via custom exceptions (`OrderError`, `ExecutionError`)  
- Produces a Markdown performance report with total return, Sharpe ratio, and drawdown metrics  
  

### Assignment 2: 
#### Multi-Signal Strategy Simulation: 
This project implements a **multi-signal trading simulator** for the **S&P 500 (2005–2025)**. Using object-oriented Python, it downloads historical price data, executes multiple technical indicator–based strategies, and compares their performance under realistic capital constraints.  

The simulator focuses on **modularity**, **execution efficiency**, and **signal evaluation** through realistic trading simulations.  

**Key Features:**  
- Efficient data acquisition via a modular `PriceLoader` class using `yfinance`  
- A static **BenchmarkStrategy** for baseline performance  
- Four signal-driven strategies:  
  - *Moving Average Crossover*  
  - *Volatility Breakout*  
  - *MACD Crossover*  
  - *RSI Oversold*  
- Object-oriented architecture with a shared `Strategy` base class  
- Full backtesting engine tracking trades, holdings, cash, and portfolio value  
- Performance visualization and comparison through a Jupyter notebook  

### Assignment 3:
#### Runtime & Space Complexity in Financial Signal Processing
This project explores **runtime and space complexity in financial signal processing** by implementing and analyzing trading strategies with different computational efficiencies. Using Python, the module ingests market data, applies multiple strategies, and benchmarks their runtime and memory performance through profiling and theoretical Big-O analysis.  

The goal is to understand how **algorithmic design choices impact scalability**, execution speed, and memory usage in real-world financial systems.  

**Key Features:**  
- Parses market data into immutable `MarketDataPoint` dataclasses  
- Implements two trading strategies with distinct complexities:  
  - `NaiveMovingAverageStrategy`: recomputes averages from scratch (O(n) time, O(n) space)  
  - `WindowedMovingAverageStrategy`: maintains a sliding window buffer (O(1) time, O(k) space)  
- Annotates all implementations with **Big-O complexity** and inline justifications  
- Profiles runtime and memory performance using `timeit`, `cProfile`, and `memory_profiler`  
- Visualizes performance scaling across input sizes (1k, 10k, 100k ticks)  
- Applies optimization techniques (e.g., `collections.deque`, vectorization, memoization, streaming)  

### Assignment 5:
#### Testing & CI in Financial Engineering
This project implements a **minimal daily-bar backtester** focused on **unit testing, code coverage, and continuous integration (CI)** in Python. The goal is not alpha generation, but rather engineering discipline—building reliable, testable components and enforcing code quality through automation.  

You’ll design modular components (data loader, strategy, broker, and backtester), write comprehensive unit tests with `pytest`, achieve ≥90% coverage, and configure **GitHub Actions** to automatically run all tests and coverage checks on every commit.  

**Key Features:**  
- Modular backtester with four components:  
  - `PriceLoader`: generates or loads synthetic price data  
  - `Strategy`: outputs daily trading signals (e.g., `VolatilityBreakoutStrategy`)  
  - `Broker`: handles market orders, updates cash/position deterministically  
  - `Backtester`: executes a daily loop (signal at t−1, trade at t)  
- Complete unit test suite using `pytest`, fixtures, and mocks  
- Continuous Integration pipeline using **GitHub Actions**  
- Enforced **≥90% coverage threshold** with `coverage.py`  
- Fast, deterministic, and isolated test design (no external APIs or I/O)  


