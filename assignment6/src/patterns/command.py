# patterns/command.py
"""
Command Pattern
- Problem: Encapsulate order execution and support undo/redo.
- Expectations:
    - Define Command.execute() and Command.undo().
    - Implement:
        - ExecuteOrderCommand: executes trade
        - UndoOrderCommand: reverses trade
    - Use CommandInvoker to manage command history.
    - Demonstrate trade lifecycle: signal → execution → undo → redo.
"""


from abc import ABC, abstractmethod
from .builder import PortfolioGroup, Position


class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass


class ExecuteOrderCommand(Command):
    def __init__(self, portfolio: PortfolioGroup, symbol, qty, action, price):
        self.portfolio = portfolio
        self.symbol = symbol
        self.qty = qty
        self.action = action
        self.price = price

        direction = 1 if action == "BUY" else -1

        self.position = Position(symbol, direction * qty, price)

    def execute(self):
        self.portfolio.add_component(self.position)

    def undo(self):
        self.portfolio.remove_component(self.position)


class CommandInvoker:
    def __init__(self):
        self.history = []
        self.redo_stack = []

    def execute(self, command: Command):
        command.execute()
        self.history.append(command)
        self.redo_stack.clear()

    def undo(self):
        if not self.history:
            return

        command = self.history.pop()
        command.undo()
        self.redo_stack.append(command)

    def redo(self):
        if not self.redo_stack:

            return
        command = self.redo_stack.pop()
        command.execute()
        self.history.append(command)


if __name__ == "__main__":
    invoker = CommandInvoker()

    portfolio = PortfolioGroup("My Portfolio")

    orders = [
        ExecuteOrderCommand(portfolio, "AAPL", 10, "BUY", 150.0),
        ExecuteOrderCommand(portfolio, "AAPL", 5, "SELL", 155.0),
        ExecuteOrderCommand(portfolio, "AAPL", 5, "SELL", 155.0),
        ExecuteOrderCommand(portfolio, "AAPL", 5, "SELL", 155.0),
        ExecuteOrderCommand(portfolio, "AAPL", 10, "BUY", 150.0),
        ExecuteOrderCommand(portfolio, "AAPL", 10, "BUY", 150.0),
        ExecuteOrderCommand(portfolio, "AAPL", 5, "BUY", 1000.0),
    ]

    for order in orders:
        invoker.execute(order)

    print(portfolio.aggregate_positions())

    # print(portfolio.details())

    # invoker.undo()
    # print(portfolio.details())
    # invoker.redo()

    # print(portfolio.get_positions())
