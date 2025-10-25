"""
Portfolio class to manage a collection of assets.

This module provides comprehensive portfolio management functionality
including position tracking, NAV calculations, and signal execution.
"""

from collections import defaultdict

from config.constants import DEFAULT_INITIAL_CASH
from models import (
    Signal,
    MarketAction,
    PositionDict,
    PriceDict,
    PositionHistory,
    SignalList,
    PortfolioUpdateError,
)
from datetime import datetime


class Portfolio:
    """
    Manages a collection of financial assets with position tracking and NAV calculations.

    This class handles portfolio state management, including position updates,
    cash balance tracking, and NAV calculations with support for both long
    and short positions.
    """

    def __init__(
        self,
        cash: float = DEFAULT_INITIAL_CASH,
        short: bool = False,
        negative_cash: bool = False,
    ) -> None:
        """
        Initialize the Portfolio class.

        Args:
            cash: The initial cash balance. Defaults to DEFAULT_INITIAL_CASH.
            allow_short: Whether short selling is allowed. Defaults to False.
        """
        self._initial_cash = cash
        self._assets: PositionDict = defaultdict(
            lambda: {"quantity": 0, "avg_price": 0.0}
        )
        self._allow_short = short
        self._negative_cash = negative_cash
        self._history: PositionHistory = dict()

        self._assets.update({"CASH": {"quantity": cash, "avg_price": 1.0}})

    @property
    def assets(self) -> PositionDict:
        """
        Get the current asset positions.

        Returns:
            A dictionary mapping asset symbols to their position details.
        """
        return dict(self._assets)  # Return a regular dict for immutability

    @property
    def history(self) -> PositionHistory:
        """
        Get the historical position data.

        Returns:
            A dictionary mapping timestamps to position snapshots.
        """
        return dict(self._history)  # Return a regular dict for immutability

    def get_nav(self, prices: PriceDict) -> float:
        """
        Calculate the Net Asset Value (NAV) of the portfolio.

        Args:
            prices: A dictionary mapping asset symbols to their current prices.

        Returns:
            The total NAV of the portfolio.
        """
        nav = self._assets["CASH"]["quantity"]  # Start with cash position

        try:
            for symbol, position in self._assets.items():
                if symbol == "CASH":
                    continue
                quantity = position["quantity"]
                price = prices[symbol]
                nav += quantity * price

        except KeyError as e:
            raise ValueError(f"Price for symbol {e} not provided in prices dict")

        return nav

    @property
    def cash(self) -> float:
        """
        Get the current cash balance.

        Returns:
            The current cash balance.
        """
        return float(self._assets["CASH"]["quantity"])

    def _validate_update(self, symbol: str, quantity: float, price: float) -> None:
        """
        Validate a position update.

        Ensures that the update does not violate short selling or negative cash constraints.

        Args:
            symbol: The asset symbol.
            quantity: The quantity to buy (positive) or sell (negative).
            price: The price per unit of the asset.

        Raises:
            ValueError: If the update is invalid.

        returns: None
        """
        if price < 0:
            raise PortfolioUpdateError("Price cannot be negative")

        # position = self._assets.get(symbol, {"quantity": 0, "avg_price": 0.0})
        position = self.get_position(symbol)

        new_quantity = position["quantity"] + quantity
        cash_after = self._assets["CASH"]["quantity"] - (quantity * price)

        if not self._allow_short and new_quantity < 0:
            raise PortfolioUpdateError(f"Short selling not allowed for {symbol}")

        if not self._negative_cash and cash_after < 0:
            raise PortfolioUpdateError("Insufficient cash for this transaction")

    def execute_signal(self, signal: Signal) -> None:
        """
        Execute a trading signal to update the portfolio.

        Args:
            signal: The trading signal to execute.

        Raises:
            PortfolioUpdateError: If the signal cannot be executed due to constraints.
        """
        if signal.action == MarketAction.BUY:
            self._validate_update(signal.symbol, signal.quantity, signal.price)
            self._update_position(signal.symbol, signal.quantity, signal.price)
        elif signal.action == MarketAction.SELL:
            self._validate_update(signal.symbol, -signal.quantity, signal.price)
            self._update_position(signal.symbol, -signal.quantity, signal.price)
        elif signal.action == MarketAction.HOLD:
            pass
        else:
            raise PortfolioUpdateError(f"Unknown market action: {signal.action}")

    def update_history(self, timestamp: datetime) -> None:
        """
        Record the current portfolio state at a given timestamp.

        Args:
            timestamp: The timestamp for the snapshot.
        """
        # Deep copy to ensure historical integrity
        self._history[timestamp] = self._assets.copy()

    def get_position(self, symbol: str) -> dict[str, float]:
        """
        Get the current position for a specific asset.

        Args:
            symbol: The asset symbol
        Returns:
            A dictionary with 'quantity' and 'avg_price' keys.
        """
        # return dict(self._assets.get(symbol, {"quantity": 0, "avg_price": 0.0}))
        return self._assets[symbol].copy()

    def _update_position(self, symbol: str, quantity: float, price: float) -> None:
        """
        Update the position for a given asset.

        Args:
            symbol: The asset symbol.
            quantity: The quantity to buy (positive) or sell (negative).
            price: The price per unit of the asset.
        """

        if quantity == 0:
            return  # No change in position

        p = self.get_position(symbol)
        curr_quantity = p["quantity"]
        curr_avg_price = p["avg_price"]

        if quantity > 0:  # Buying
            # buying more of the asset
            if curr_quantity >= 0:
                total_cost = (curr_quantity * curr_avg_price) + (quantity * price)
                new_quantity = curr_quantity + quantity
                new_avg_price = total_cost / new_quantity if new_quantity != 0 else 0.0

            else:  # curr_quantity < 0
                # covering a short position
                if quantity >= abs(curr_quantity):
                    # fully cover the short position and go long
                    new_quantity = curr_quantity + quantity
                    new_avg_price = price  # new avg price is the buy price
                else:
                    # partially cover the short position
                    new_quantity = curr_quantity + quantity
                    new_avg_price = curr_avg_price  # avg price remains the same

        else:  # Selling
            if curr_quantity > 0:
                # selling from a long position
                if abs(quantity) >= curr_quantity:
                    # fully sell the long position and go short
                    new_quantity = curr_quantity + quantity
                    new_avg_price = price  # new avg price is the sell price
                else:
                    # partially sell the long position
                    new_quantity = curr_quantity + quantity
                    new_avg_price = curr_avg_price  # avg price remains the same

            else:  # curr_quantity <= 0:
                # increasing a short position
                total_proceeds = (abs(curr_quantity) * curr_avg_price) + (
                    abs(quantity) * price
                )
                new_quantity = curr_quantity + quantity
                new_avg_price = (
                    total_proceeds / abs(new_quantity) if new_quantity != 0 else 0.0
                )

        # Update cash position
        self._assets["CASH"]["quantity"] -= quantity * price
        self._assets.update(
            {
                symbol: {
                    "quantity": new_quantity,
                    "avg_price": new_avg_price,
                }
            }
        )
