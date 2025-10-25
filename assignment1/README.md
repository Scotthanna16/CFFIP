## Assignment 1 – CSV-Based Algorithmic Trading Backtester

Modular backtesting engine to evaluate trading strategies on CSV price data.

### Setup

Requirements: see `requirements.txt`

```bash
# From repo root
cd assignment1

# 1) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt
```

### Run

```bash
# Ensure input data exists at data/market_data.csv (ISO timestamp,symbol,price)
python main.py
```

Optional: regenerate sample data

```bash
# Writes a CSV with header: timestamp,symbol,price
python -c "from src.data_generator import generate_market_csv as g; g('AAPL',150.0,'data/market_data.csv',500,0.02,0.0)"
```

### Outputs

Generated in `out/`:

- trade_data.csv, portfolio_data.csv
- equity_curve.csv, periodic_returns.csv
- equity_curve.png, periodic_returns.png

Summary metrics are saved to `performance.md`.

### Data format

CSV with header: `timestamp,symbol,price` where `timestamp` is ISO-8601.

### Module overview (`src/`)

- `data_loader.py`:
  - `load_market_data(file_path)` -> list of `MarketDataPoint` parsed from CSV.
- `models/models.py`:
  - Core types: `MarketDataPoint`, `Signal`, `Order`, `Portfolio` and errors.
  - `Portfolio.add_order(order)` updates positions/cash; `snapshot()` returns numeric state.
- `strategies/strategies.py`:
  - Base `Strategy.generate_signals(tick)` -> list[`Signal`].
  - Included: `SimpleMovingAverageCrossoverStrategy`, `MeanReversionStrategy`, `ExponentialMovingAverageCrossoverStrategy`.
- `engine/engine.py`:
  - `Engine.run(strategy, market_data)` processes ticks, executes orders, yields `(trade, log)` and logs to `Report`.
- `reporting/reporting.py`:
  - `Report` collects trades/portfolio, writes CSV/PNG, computes total return, Sharpe, max drawdown.

### Add a strategy

1. Subclass `Strategy` and implement `generate_signals(tick: MarketDataPoint) -> list[Signal]`.
2. Register it in `main.py` under `strategies_to_test`.

**_NOTE:_** Currently, adding a strategy to `strategies_to_test` will create conflicts with reporting as report names are not unique. This should be updated before testing multiple strategies at once

Authors: Andrew Moukabary, Scott Hanna, Reece VanDeWeghe, Colin Huh
