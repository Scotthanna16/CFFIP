#!/usr/bin/env python3
"""
Main orchestration script for the algorithmic trading backtester.
This script coordinates data loading, strategy execution, and reporting.
"""

import os
import sys
from pathlib import Path

# Add ./src directory to Python path
sys.path.append("./src")
import data_loader  # type: ignore
import strategies  # type: ignore
import engine  # type: ignore
import reporting  # type: ignore
from models import MarketDataPoint  # type: ignore

import matplotlib.pyplot as plt

initial_cash = 10000


def main():
    """Main function to orchestrate the backtesting process."""

    # Ensure output directory exists
    os.makedirs("out", exist_ok=True)

    print("=== Backtesting Engine ===")
    print("Loading market data...")

    # Load market data
    try:
        market_data = data_loader.load_market_data("data/market_data.csv")
        print(f"Loaded {len(market_data)} data points")
    except FileNotFoundError:
        print("Error: market_data.csv not found in data/ directory")
        return 1
    except Exception as e:
        print(f"Error loading data: {e}")
        return 1

    # Initialize strategies
    strategies_to_test = [
        (
            "Simple Moving Average Crossover",
            strategies.SimpleMovingAverageCrossoverStrategy(5, 20),
        ),
    ]

    # Test each strategy
    for strategy_name, strategy in strategies_to_test:
        print(f"\n=== Testing {strategy_name} Strategy ===")

        # Initialize engine and run backtest
        backtest_engine = engine.Engine(initial_cash=initial_cash)

        print("Running backtest...")
        trade_count = 0
        for trade, log in backtest_engine.run(strategy, market_data):
            if trade:  # Only count actual trades (not HOLD signals)
                trade_count += 1
                if trade_count <= 5:  # Show first 5 trades
                    print(f"  {log}")

        print(f"Total trades executed: {trade_count}")

        # Generate reports
        print("Generating performance reports...")

        backtest_engine.report.create_performance_data()
        backtest_engine.report.create_trade_data()
        backtest_engine.report.create_portfolio_data()

        print(f"Reports saved to out/ directory")
        print(f"Performance summary saved to performance.md")

        backtest_engine.report.output_performance_report()

    print("\nBacktest Done")

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
