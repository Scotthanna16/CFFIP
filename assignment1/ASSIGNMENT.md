# CSV-Based Algorithmic Trading Backtester

## Overview

Design and implement a modular Python backtester that reads pre-generated market data from a CSV file, applies trading strategies, executes simulated orders, and produces a performance report. You will practice mutable versus immutable types, object-oriented design with abstract classes and inheritance, container management using lists and dictionaries, and robust exception handling.

## Learning Objectives

- Parse CSV data into immutable dataclass instances.
- Distinguish and use mutable classes for order management.
- Build an abstract `Strategy` interface with concrete subclasses.
- Manage time-series data and portfolio state using lists and dictionaries.
- Define custom exceptions and handle errors without stopping the backtest.
- Generate a Markdown report summarizing key performance metrics.

## Task Specifications

1. **Data Ingestion & Immutable Types**

   - Read `market_data.csv` (columns: `timestamp`, `symbol`, `price`) using the built-in `csv` module.
   - Define a frozen dataclass `MarketDataPoint` with attributes `timestamp` (`datetime`), `symbol` (`str`), and `price` (`float`).
   - Parse each row into a `MarketDataPoint` and collect them in a list.

2. **Mutable Order Management**

   - Implement an `Order` class with mutable attributes: `symbol`, `quantity`, `price`, and `status`.
   - Demonstrate in a unit test that you can update `Order.status` but not `MarketDataPoint.price`.

3. **Object-Oriented Design**

   - Create an abstract base class:

     ```python
     from abc import ABC, abstractmethod

     class Strategy(ABC):
         @abstractmethod
         def generate_signals(self, tick: MarketDataPoint) -> list:
             pass
     ```

   - Provide two concrete strategies (e.g., moving average crossover, momentum) that inherit from `Strategy`.
   - Encapsulate any internal buffers or indicator values as private attributes (e.g., `self._prices`, `self._window`).

4. **Containers for Data & Signals**

   - Buffer incoming `MarketDataPoint` instances in a list.
   - Store open positions in a dictionary keyed by symbol: `{'AAPL': {'quantity': 0, 'avg_price': 0.0}}`.
   - Collect signals as a list of tuples `(action, symbol, qty, price)` before converting them to `Order` objects.

5. **Exception Handling**

   - Define custom exceptions:

     ```python
     class OrderError(Exception): pass
     class ExecutionError(Exception): pass
     ```

   - Raise `OrderError` for invalid orders (e.g., zero or negative quantity).
   - In the execution engine, simulate occasional failures and raise `ExecutionError`; catch and log these errors to continue processing.

6. **Execution Engine**

   - Iterate through the list of `MarketDataPoint` objects in timestamp order.
   - For each tick:
     - Invoke each strategy to generate signals.
     - Instantiate and validate `Order` objects.
     - Execute orders by updating the portfolio dictionary.
   - Wrap order creation and execution in `try/except` blocks for resilience.

7. **Performance Reporting**

   - After processing all ticks, compute:
     - Total return
     - Series of periodic returns
     - Sharpe ratio
     - Maximum drawdown
   - Generate a `performance.md` report with:
     - Tables summarizing metrics
     - An equity-curve plot (e.g., ASCII art or embedded chart link)
     - A short narrative interpretation of results

## Deliverables

Upload all these files into a github repo that I will be able to open. My github username is sdonadio.

- `data_loader.py`
- `models.py` (dataclasses, `Order`, exceptions)
- `strategies.py`
- `engine.py`
- `reporting.py`
- `main.py` orchestrating data loading, strategy execution, and reporting (or use a python notebook)
- Unit tests covering (if you don't know how to create unit testing for now, you can just use a python notebook):
  - CSV parsing into frozen dataclass
  - Mutable behavior of `Order`
  - Exception raising and handling
- `performance.ipynb` containing metrics, tables, plots, and narrative
- `README.md` with setup instructions and module descriptions

PS: you will find the data generator.

[data_generator.py](https://canvas.uchicago.edu/courses/66215/files/13823389?wrap=1)
