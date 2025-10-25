# engine.py
from src.models import (
    Order,
    OrderError,
    ExecutionError,
    MarketDataPoint,
    Signal,
    Portfolio,
)
from src.strategies import Strategy

from src.reporting import Report

from numpy import random


class Engine:
    def __init__(self, initial_cash: float = 1_000_000):
        self.__portfolio = Portfolio(initial_cash)
        self.__report = Report()
        # seed for reproducible simulated failures in tests
        self._rng = random.default_rng()

    def execute_trade(self, signal: Signal):
        try:
            # Skip HOLD signals (no action needed)
            if signal.action.upper() == "HOLD" or signal.quantity == 0:
                self.report.add_trade_log(None, "HOLD signal - no action taken")
                return None, "HOLD signal - no action taken"

            # create/validate order from signal (may raise OrderError)
            order = Order.from_signal(signal)

            # validate against portfolio/cash constraints
            if order.quantity <= 0:
                raise OrderError("Order quantity must be positive")

            # simulate occasional execution failure (5% chance)
            if self._rng.random() < 0.05:
                raise ExecutionError("Simulated execution failure")

            # apply order to portfolio (may change portfolio state)
            self.__portfolio.add_order(order)

            return order, "Order executed successfully"

        except OrderError as e:
            return None, f"Order creation failed: {getattr(e, 'message', e)}"
        except ExecutionError as e:
            return None, f"Order execution failed: {getattr(e, 'message', e)}"
        except Exception as e:
            return None, f"Unexpected error: {e}"

    def run(self, strategy: Strategy, market_data: list[MarketDataPoint]):

        # ensure data is processed in timestamp order
        ordered = sorted(market_data, key=lambda x: x.timestamp)

        for tick in ordered:
            signals = strategy.generate_signals(tick)

            for signal in signals:
                trade, log = self.execute_trade(signal)

                # log the attempt/result in the report (report handles None trades)
                self.__report.execute_trade(trade, log, self.__portfolio)

                # continue processing regardless of success/failure
                yield trade, log

        # finalize report outputs (CSV files used by the notebook)
        # self.__report.create_trade_data()
        # self.__report.create_portfolio_data()

    @property
    def report(self):

        return self.__report
