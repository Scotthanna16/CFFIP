"""
Trading Engine class to manage backtesting and execution.

This module provides the main trading engine that orchestrates strategy
execution, portfolio management, and performance tracking.
"""

from datetime import datetime
from typing import Dict, List, Any

import pandas as pd  # type: ignore

from config.constants import DEFAULT_INITIAL_CASH

from engine.report import Report
from models import MarketDataPoint, Signal, SignalList, PriceDict, MarketAction
from portfolio import Portfolio
from strategies import Strategy


class Engine:
    """
    Main trading engine that orchestrates strategy execution and portfolio management.

    This class handles the core backtesting functionality, executing trading
    strategies on historical data and tracking portfolio performance.
    """

    def __init__(
        self,
        strategy: Strategy,
        cash: float = DEFAULT_INITIAL_CASH,
        short: bool = False,
        negative_cash: bool = False,
    ) -> None:

        self._strategy = strategy
        self._portfolio = Portfolio(cash=cash, short=short, negative_cash=negative_cash)
        self._report = Report()

    def _execute_strategy(self, *data: MarketDataPoint) -> SignalList:
        """
        Execute the strategy and return the signals.

        Args:
            *data: Variable number of MarketDataPoint objects (1 per symbol)

        Returns:
            List of trading signals

        Raises:
            ValueError: If invalid market data is provided
        """
        # Simple data validation
        if not data:
            return []

        for point in data:
            if point.price <= 0:
                raise ValueError(f"Invalid price {point.price} for {point.symbol}")

        return self._strategy.generate_signals(*data)

    def run(self, data: pd.DataFrame) -> None:
        """
        Run the backtest on the provided data.

        Args:
            data: Historical price data for backtesting

        Raises:
            ValueError: If data is invalid or empty
        """
        if data is None or data.empty:
            raise ValueError("Data cannot be None or empty")

        if not isinstance(data, pd.DataFrame):
            raise ValueError(f"Data must be a pandas DataFrame, got {type(data)}")

        if data.index.name != "timestamp" and not pd.api.types.is_datetime64_any_dtype(
            data.index
        ):
            raise ValueError("Data index must be datetime-like")

        self._report.set_price_data(data)

        # looping over trading days
        for _, row in data.iterrows():
            # Create market data points with proper timestamp conversion
            timestamp = (
                row.name
                if isinstance(row.name, datetime)
                else pd.to_datetime(str(row.name))
            )

            prices: PriceDict = {
                str(symbol): float(row[symbol]) for symbol in row.index  # type: ignore
            }
            market_data = [
                MarketDataPoint(
                    timestamp=timestamp,
                    symbol=str(symbol),
                    price=float(row[symbol]),  # type: ignore
                )
                for symbol in row.index
            ]

            # Execute strategy
            signals = self._execute_strategy(*market_data)
            executed_signals: SignalList = []

            # Execute signals
            for signal in signals:
                try:
                    if signal.action == MarketAction.HOLD:
                        continue
                    self._portfolio.execute_signal(signal)
                    executed_signals.append(signal)
                except Exception:
                    # Log error but continue with other signals
                    continue

            # update report

            nav = self._portfolio.get_nav(prices)
            cash = self._portfolio.cash

            # Track NAV and portfolio state
            timestamp = (
                row.name
                if isinstance(row.name, datetime)
                else pd.to_datetime(str(row.name))
            )

            # Track portfolio snapshot with all positions and market values
            portfolio_snapshot: Dict[str, Any] = {
                "nav": nav,
                "cash": cash,
                "total_invested": nav - cash,
            }

            self._report.update(
                timestamp, nav, cash, portfolio_snapshot, executed_signals
            )

        # Calculate final performance metrics
        self._report.calculate_performance_metrics()

    def get_report(self) -> Report:
        """
        Get the report object for accessing historical data.

        Returns:
            Report object containing performance data and analytics
        """
        return self._report

    def plot_performance(self) -> None:
        """
        Plot the performance of the trading strategy.

        This method generates visualizations of key performance metrics
        such as portfolio value over time, drawdowns, and returns distribution.
        """
        self._report.plot_performance()

    def plot_signals(self, ticker: str) -> None:
        """
        Plot the trading signals on the price chart for a specific ticker.

        Args:
            ticker: The asset symbol to plot signals for.
        """
        self._report.plot_signals(ticker)
