from src.patterns.builder import PortfolioBuilder


def test_portfolio_from_json(portfolio_structure):
    builder = PortfolioBuilder.from_json("jsons/portfolio_structure.json")
    portfolio = builder.build()

    assert portfolio.details() == portfolio_structure


def test_aggregate_positions():
    builder = PortfolioBuilder.from_json("jsons/portfolio_structure.json")
    portfolio = builder.build()

    aggregated = portfolio.aggregate_positions()

    expected = {
        "AAPL": {"total_quantity": 100, "average_price": 172.35},
        "MSFT": {"total_quantity": 50, "average_price": 328.10},
        "SPY": {"total_quantity": 20, "average_price": 430.50},
    }

    assert aggregated == expected


def test_aggregate_positions_multiple_same_symbol_long_short(empty_builder):
    builder = empty_builder
    builder.add_position("AAPL", 1, 100.0)
    builder.add_position("AAPL", 1, 150.0)
    portfolio = builder.build()

    sub_builder = empty_builder
    sub_builder.add_position("AAPL", -3, 125.0)

    aggregated = portfolio.aggregate_positions()

    expected = {
        "AAPL": {"total_quantity": -1, "average_price": 125.0},
    }

    assert aggregated == expected


def test_aggregate_positions_multiple_same_symbol_short_long(empty_builder):
    builder = empty_builder
    builder.add_position("AAPL", -1, 100)
    builder.add_position("AAPL", -1, 150)
    portfolio = builder.build()

    sub_builder = empty_builder
    sub_builder.add_position("AAPL", 3, 125)

    aggregated = portfolio.aggregate_positions()

    expected = {
        "AAPL": {"total_quantity": 1, "average_price": 125.0},
    }

    assert aggregated == expected
