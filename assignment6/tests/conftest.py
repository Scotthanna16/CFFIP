# conftest.py
"""
Need to test:
- Validate Factory creates correct instrument types.
- Confirm Singleton behavior with shared config.
- Test Decorator-enhanced analytics output.
- Verify Observer notifications and Command execution/undo logic.
- Confirm strategy outputs match expectations for given inputs.
"""
import pytest
import csv
from src.patterns.factory import InstrumentFactory
import json
from src.patterns.builder import PortfolioBuilder
from src.patterns.strategy import MeanReversionStrategy, BreakoutStrategy
from src.models import MarketDataPoint
from datetime import datetime


@pytest.fixture
def sample_instrument_data():
    with open("data/instruments.csv", newline="") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


@pytest.fixture
def factory():
    return InstrumentFactory


@pytest.fixture
def strategy_params():
    with open("jsons/strategy_params.json", "r") as f:
        return json.load(f)


@pytest.fixture
def portfolio_structure():
    with open("jsons/portfolio_structure.json", "r") as f:
        return json.load(f)


@pytest.fixture
def empty_builder():

    builder = PortfolioBuilder("Test Portfolio").set_owner("Test Owner")

    return builder


@pytest.fixture
def mean_reversion_strategy():
    return MeanReversionStrategy.from_json("jsons/strategy_params.json")


@pytest.fixture
def sample_market_data():
    initial_date = "2024-01-01"
    symbol = "AAPL"
    prices = [100] * 20 + [200]

    data_points = []
    for i, price in enumerate(prices):
        date = f"2024-01-{i+1:02d}"
        data_points.append(
            MarketDataPoint(
                timestamp=datetime.fromisoformat(date), symbol=symbol, price=price
            )
        )
    return data_points


@pytest.fixture
def breakout_strategy_params():
    with open("jsons/strategy_params.json", "r") as f:
        return json.load(f)["BreakoutStrategy"]


@pytest.fixture
def breakout_strategy():

    return BreakoutStrategy.from_json("jsons/strategy_params.json")
