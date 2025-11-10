# Trading System

A multi-process trading system that simulates real-time price feeds, order book management, and automated trading strategies using shared memory and TCP sockets.

## Architecture

- **Gateway**: Generates and broadcasts price and news streams via TCP sockets
- **OrderBook**: Receives prices, stores them in shared memory
- **Strategy**: Reads prices from shared memory, generates trading signals based on moving averages and sentiment
- **OrderManager**: Receives and processes orders from the strategy

## Quick Start (run from root)

```bash
python -m src.main
```

Press `Ctrl+C` to shutdown all processes. Something is wrong here...

## Configuration

Edit `src/constants.py` to configure:
- `SYMBOLS`: List of trading symbols (default: `["AAPL", "MSFT", "GOOG"]`)
- `INTERVAL`: Update frequency in seconds (default: `1.0`)
- `SIMULATED_TIME_DELTA`: Amount of time simulted per `INTERVAL` seconds
- `BULL_THRESHOLD` / `BEAR_THRESHOLD`: Sentiment thresholds for trading signals\
- `LOG_LEVEL`: level of logs outputted. DEBUG allows you to see much more info about the IPC
- Port numbers: `PRICE_PORT`, `NEWS_PORT`, `STRATEGY_PORT`

## Strategy

The strategy uses:
- **SMA (20-period)** and **LMA (50-period)** moving averages for price signals
- **News sentiment** (0-100) for market sentiment
- Generates BUY signals when: sentiment > 75 and SMA > LMA
- Generates SELL signals when: sentiment < 25 and SMA < LMA

## Logs

All logs are written to `out.log` and stdout. Logs include price updates, order generation, and system events.

## Tests (run from root)

```{bash}
python -m pytest tests
```

