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

### Assignment 6:
#### Design Patterns in Financial Software Architecture
This project implements a **modular financial analytics and trading platform** using key **object-oriented design patterns**.  
Through realistic financial scenarios, you will apply **creational**, **structural**, and **behavioral** patterns to build a system that is reusable, extensible, and easy to maintain.  

Each pattern is introduced in the context of a practical finance problem—ranging from instrument creation and portfolio construction to trade execution and signal broadcasting—illustrating how design choices impact flexibility, maintainability, and scalability in production systems.  

**Key Features:**  
- Creational Patterns:
  - `Factory` – Create different instrument types (Stock, Bond, ETF) dynamically.  
  - `Singleton` – Centralize configuration and parameters across modules.  
  - `Builder` – Construct complex nested portfolios fluently.  

- Structural Patterns:
  - `Decorator` – Extend instrument analytics (volatility, beta, drawdown) without modifying base classes.  
  - `Adapter` – Normalize heterogeneous external data sources (Yahoo Finance, Bloomberg XML).  
  - `Composite` – Represent hierarchical portfolio structures (positions, sub-portfolios).  

- Behavioral Patterns: 
  - `Strategy` – Support interchangeable trading logic (Mean Reversion, Breakout).  
  - `Observer` – Implement event-driven updates via signal publishing and listener modules.  
  - `Command` – Encapsulate trade execution and support undo/redo functionality.  


### Assignment 7:


#### Parallel Computing for Financial Data Processing 
This project implements a **parallelized data processing system** for large-scale financial time-series analytics. It explores the tradeoffs between **threading** and **multiprocessing**, benchmarks **pandas vs polars**, and applies concurrency to accelerate rolling metrics, signal generation, and portfolio aggregation.

The emphasis is on **computational efficiency**, **parallel architecture**, and **profiling performance** within a realistic financial analytics context.

**Key features:** 
- Data Ingestion & Profiling: 
  - Load market data using both `pandas` and `polars`.  
  - Parse time-indexed price data (`timestamp`, `symbol`, `price`).  
  - Benchmark ingestion time and memory usage with profiling tools.  

- Rolling Analytics:  
  - Compute per-symbol rolling metrics:  
    - 20-period Moving Average  
    - 20-period Rolling Standard Deviation  
    - Rolling Sharpe Ratio (risk-free rate = 0)  
  - Implement in both `pandas` and `polars`, comparing syntax and speed.  
  - Visualize results for representative assets (e.g., AAPL).  

- Threading vs Multiprocessing:  
  - Apply both `ThreadPoolExecutor` and `ProcessPoolExecutor` for parallel computation across symbols.  
  - Compare:  
    - Total runtime  
    - CPU utilization  
    - Memory consumption  
  - Discuss **GIL constraints** and when multiprocessing is advantageous.  

- Parallel Portfolio Aggregation:  
  - Compute per-position metrics: value, volatility, and drawdown.  
  - Aggregate portfolio hierarchies recursively:  
    - `total_value`  
    - `aggregate_volatility` (weighted average)  
    - `max_drawdown` (worst case)  
  - Compare sequential vs. parallel implementations for scalability.  
  - Output structured JSON summaries of computed portfolios.  

- Performance Benchmarking:  
  - Compare pandas vs polars across ingestion, computation, and aggregation.  
  - Profile runtime, memory usage, and parallel scaling using `timeit`, `memory_profiler`, and `psutil`.  
  - Visualize performance tradeoffs with bar charts and tables.  


### Assignement 8:


#### Interprocess Communication for Trading Systems    
This project implements a **simplified trading stack** using **interprocess communication (IPC)** to connect four independent components — **Gateway**, **OrderBook**, **Strategy**, and **OrderManager** — via **TCP sockets** and **shared memory**.  
Each process runs concurrently, communicating solely through serialized messages and shared memory synchronization, emulating how modern trading systems exchange data in real time.

The assignment emphasizes **socket programming**, **shared memory design**, **process orchestration**, and **low-latency communication** within a financial systems context.

**Key Features**  
- Real-Time Data Flow:
  - `Gateway` streams live tick prices and sentiment data over TCP sockets.  
  - `OrderBook` receives prices and maintains a synchronized shared memory store.  
  - `Strategy` reads from shared memory and sentiment feed to generate signals.  
  - `OrderManager` receives and logs executed orders in real time.

- Shared Memory Integration: 
  - Implements a `SharedPriceBook` class using `multiprocessing.shared_memory`.  
  - Provides atomic read/write operations with `Lock` synchronization.  
  - Enables low-latency market data sharing across processes.

- Trading Logic: 
  - **Price-based signal:** Moving average crossover (short vs. long window).  
  - **News-based signal:** Sentiment thresholds for buy/sell decisions.  
  - Executes trades only when both price and sentiment agree.  
  - Manages open position state to prevent duplicate orders.

- Order Handling:  
  - Orders are serialized and transmitted via sockets using consistent message framing (`MESSAGE_DELIMITER`).  
  - `OrderManager` acts as a trade execution server, logging and printing confirmations:
    ```
    Received Order 12: BUY 10 AAPL @ 173.20
    ```
    
- Resilience & Monitoring:  
  - Handles dropped connections and reconnection logic gracefully.  
  - Measures latency between tick and trade, throughput, and shared memory footprint.  


