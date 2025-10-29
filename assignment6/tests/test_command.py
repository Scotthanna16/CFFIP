from src.patterns.command import Command, CommandInvoker, ExecuteOrderCommand
from src.patterns.builder import PortfolioGroup, Position


def test_addOrder():

    invoker = CommandInvoker()

    portfolio = PortfolioGroup("My Portfolio")

    buy_command = ExecuteOrderCommand(portfolio, "AAPL", 10, "BUY", 150.0)
    buy_command2 = ExecuteOrderCommand(portfolio, "MSFT", 10, "BUY", 150.0)
    invoker.execute(buy_command)
    invoker.execute(buy_command2)

    assert portfolio.details() == {
        "name": "My Portfolio",
        "positions": [
            {"symbol": "AAPL", "quantity": 10, "price": 150.0},
            {"symbol": "MSFT", "quantity": 10, "price": 150.0},
        ],
    }


def test_undoOrder():
    invoker = CommandInvoker()

    portfolio = PortfolioGroup("My Portfolio")

    buy_command = ExecuteOrderCommand(portfolio, "AAPL", 10, "BUY", 150.0)
    buy_command2 = ExecuteOrderCommand(portfolio, "MSFT", 10, "BUY", 150.0)
    invoker.execute(buy_command)
    invoker.execute(buy_command2)
    assert portfolio.details() == {
        "name": "My Portfolio",
        "positions": [
            {"symbol": "AAPL", "quantity": 10, "price": 150.0},
            {"symbol": "MSFT", "quantity": 10, "price": 150.0},
        ],
    }
    invoker.undo()
    assert portfolio.details() == {
        "name": "My Portfolio",
        "positions": [{"symbol": "AAPL", "quantity": 10, "price": 150.0}],
    }


def test_redoOrder():
    invoker = CommandInvoker()

    portfolio = PortfolioGroup("My Portfolio")

    buy_command = ExecuteOrderCommand(portfolio, "AAPL", 10, "BUY", 150.0)
    buy_command2 = ExecuteOrderCommand(portfolio, "MSFT", 10, "BUY", 150.0)
    invoker.execute(buy_command)
    invoker.execute(buy_command2)

    assert portfolio.details() == {
        "name": "My Portfolio",
        "positions": [
            {"symbol": "AAPL", "quantity": 10, "price": 150.0},
            {"symbol": "MSFT", "quantity": 10, "price": 150.0},
        ],
    }
    invoker.undo()
    assert portfolio.details() == {
        "name": "My Portfolio",
        "positions": [{"symbol": "AAPL", "quantity": 10, "price": 150.0}],
    }

    invoker.redo()
    assert portfolio.details() == {
        "name": "My Portfolio",
        "positions": [
            {"symbol": "AAPL", "quantity": 10, "price": 150.0},
            {"symbol": "MSFT", "quantity": 10, "price": 150.0},
        ],
    }
