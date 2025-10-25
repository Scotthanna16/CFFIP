"""
Clean reporting and tracking system for the trading engine.

This module provides comprehensive reporting and analytics functionality
for tracking portfolio performance, signals, and market data throughout
the backtesting process.
"""

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt  # type: ignore
import pandas as pd  # type: ignore

from models import MarketDataPoint, Signal, SignalList

RISK_FREE_RATE = 0.02


class Report:
    """
    Handles all tracking and reporting for the trading engine.

    This class manages historical data tracking including NAV history,
    portfolio snapshots, signal history, and performance metrics.
    It also provides visualization capabilities for performance analysis.
    """

    def __init__(self) -> None:
        """
        Initialize the Report class.

        Sets up empty data structures for tracking portfolio performance
        and trading activity.
        """
        self._nav_history: List[Dict[str, Any]] = []
        self._portfolio_history: List[Dict[str, Any]] = []
        self._signal_history: List[Dict[str, Any]] = []
        self._performance_metrics: Dict[str, Any] = {}
        self._price_data: pd.DataFrame = pd.DataFrame()

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get the calculated performance metrics.

        Returns:
            Dictionary containing various performance metrics
        """
        return self._performance_metrics

    def set_price_data(self, price_data: pd.DataFrame) -> None:
        """
        Set the price data for the report.

        Args:
            price_data: Historical price data used in backtesting
        """
        self._price_data = price_data

    def _track_nav(self, timestamp: datetime, nav: float, cash: float) -> None:
        """
        Track NAV over time.

        Args:
            timestamp: When the NAV was recorded
            nav: Net Asset Value at the timestamp
            cash: Cash balance at the timestamp
        """
        self._nav_history.append({"timestamp": timestamp, "nav": nav, "cash": cash})

    def _track_portfolio(
        self, timestamp: datetime, portfolio_snapshot: Dict[str, Any]
    ) -> None:
        """
        Track portfolio state over time.

        Args:
            timestamp: When the portfolio state was recorded
            portfolio_snapshot: Dictionary containing portfolio state data
        """
        self._portfolio_history.append({"timestamp": timestamp, **portfolio_snapshot})

    def _track_signal(self, timestamp: datetime, signal: Signal) -> None:
        """
        Track individual trading signals.

        Args:
            timestamp: When the signal was generated
            signal: The trading signal to record
        """
        self._signal_history.append(
            {
                "timestamp": timestamp,
                "action": signal.action.value,
                "symbol": signal.symbol,
                "quantity": signal.quantity,
                "price": signal.price,
            }
        )

    def update(
        self,
        timestamp: datetime,
        nav: float,
        cash: float,
        portfolio_snapshot: Dict[str, Any],
        signals: SignalList,
    ) -> None:
        """
        Update the report with new data.

        Args:
            timestamp: Current timestamp
            nav: Current NAV
            cash: Current cash balance
            portfolio_snapshot: Current portfolio state
            signals: List of signals generated at this timestamp
        """
        self._track_nav(timestamp, nav, cash)
        self._track_portfolio(timestamp, portfolio_snapshot)
        for signal in signals:
            self._track_signal(timestamp, signal)

    def calculate_performance_metrics(self) -> None:
        """
        Calculate comprehensive performance metrics.

        Computes various performance metrics including total return,
        Sharpe ratio, maximum drawdown, and volatility.
        """
        if not self._nav_history:
            return

        nav_df = self.get_nav_dataframe()
        if nav_df.empty:
            return

        # Calculate returns
        nav_df["daily_return"] = nav_df["nav"].pct_change()
        nav_df["cumulative_return"] = (nav_df["nav"] / nav_df["nav"].iloc[0] - 1) * 100

        # Basic metrics
        total_return = nav_df["cumulative_return"].iloc[-1]
        annualized_return = ((100 + total_return) / 100) ** (
            252 / len(nav_df)
        )  # Assuming daily data
        # 100+ total_return
        # Volatility (annualized)
        daily_volatility = nav_df["daily_return"].std()
        annualized_volatility = daily_volatility * (252**0.5)

        # sharpe_ratio = (
        #     (annualized_return - 100 * RISK_FREE_RATE) / annualized_volatility
        #     if annualized_volatility > 0
        #     else 0
        # )

        # Maximum drawdown
        returns = nav_df["nav"].pct_change().fillna(0)
        cumulative = (1 + returns).cumprod()
        max_dd = (cumulative.cummax() - cumulative).max() * 100

        # Win rate (if we have signal data)
        signal_df = self.get_signal_dataframe()

        # Store metrics
        self._performance_metrics = {
            "total_return_pct": total_return,
            "annualized_return_pct": 100 * (annualized_return - 1),
            "annualized_volatility_pct": annualized_volatility * 100,
            "sharpe_ratio": 100
            * (annualized_return - 1 - RISK_FREE_RATE)
            / (100 * annualized_volatility) if annualized_volatility > 0 else 0,
            "max_drawdown_pct": max_dd,
            "total_trades": len(
                [x for x in signal_df["action"] if x in ["BUY", "SELL"]]
            ) if not signal_df.empty else 0,
            "data_points": len(nav_df),
            "total assets": nav_df["nav"].iloc[-1],  # Exclude nav column
        }

    def get_signal_dataframe(self) -> pd.DataFrame:
        """
        Get signal history as DataFrame.

        Returns:
            DataFrame with timestamp index containing signal data
        """
        if not self._signal_history:
            return pd.DataFrame()

        df = pd.DataFrame(self._signal_history)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)
        return df

    def get_nav_dataframe(self) -> pd.DataFrame:
        """
        Get NAV history as DataFrame.

        Returns:
            DataFrame with timestamp index containing NAV and cash data
        """
        if not self._nav_history:
            return pd.DataFrame()

        df = pd.DataFrame(self._nav_history)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)
        return df

    def performance_dataframe(self) -> pd.DataFrame:
        df = pd.DataFrame()

        if not self._nav_history:
            print("No NAV history to plot.")

        nav_df = self.get_nav_dataframe()
        if nav_df.empty:
            print("No NAV history to plot.")
            return df

        df = nav_df.copy()
        df["returns"] = df["nav"].pct_change().fillna(0)
        df["cumulative_return"] = (df["returns"] + 1).cumprod() - 1
        df["drawdown"] = (df["nav"].cummax() - df["nav"]) / df["nav"].cummax()

        return df

    def plot_performance(self) -> None:
        """
        Plot performance metrics including NAV and drawdowns.
        """

        df = self.performance_dataframe()
        df.plot(subplots=True, figsize=(12, 8))

    def plot_signals(self, symbol: str) -> None:
        """
        Plot signals on price chart for a given symbol.

        Args:
            symbol: The ticker symbol to plot signals for
        """
        if self._price_data.empty:
            print("No price data available for plotting.")
            return

        if symbol not in self._price_data.columns:
            print(f"No price data available for symbol: {symbol}")
            return

        price_series = self._price_data[symbol].dropna()
        if price_series.empty:
            print(f"No price data available for symbol: {symbol}")
            return

        signal_df = self.get_signal_dataframe()
        if signal_df.empty:
            print("No signal data available for plotting.")
            return

        buy_signals = signal_df[
            (signal_df["symbol"] == symbol) & (signal_df["action"] == "BUY")
        ]
        sell_signals = signal_df[
            (signal_df["symbol"] == symbol) & (signal_df["action"] == "SELL")
        ]

        plt.figure(figsize=(14, 7))
        plt.plot(price_series.index, price_series.values, label=f"{symbol} Price")

        plt.scatter(
            buy_signals.index,
            price_series.reindex(buy_signals.index),
            marker="^",
            color="g",
            label="Buy Signal",
            alpha=1,
        )
        plt.scatter(
            sell_signals.index,
            price_series.reindex(sell_signals.index),
            marker="v",
            color="r",
            label="Sell Signal",
            alpha=1,
        )

        plt.title(f"Trading Signals for {symbol}")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.grid()
        plt.show()
