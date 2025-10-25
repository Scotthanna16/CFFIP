# Repo for Computing for Finance in Python assignments

### These assignments were a team effort between myself and @amoukabary
### Assignment 1: 
#### - Algorithmic Trading Backtester: 
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
#### - Multi-Signal Strategy Simulation: 
This project implements a multi-signal trading simulator for the S&P 500 (2005–2025). Using object-oriented Python, it downloads historical price data, executes multiple technical indicator–based strategies, and compares their performance under realistic capital constraints.
The simulator includes:
PriceLoader for efficient data acquisition and storage using yfinance
BenchmarkStrategy as a static long-only baseline
Four signal-driven strategies:
Moving Average Crossover
Volatility Breakout
MACD Crossover
RSI Oversold
A full backtesting engine tracking trades, holdings, cash, and portfolio value
A Jupyter notebook for visualization and performance comparison across strategies
The project emphasizes modularity, execution efficiency, and signal evaluation through realistic trading simulations.


