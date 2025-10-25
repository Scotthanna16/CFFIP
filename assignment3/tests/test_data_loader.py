import pathlib
import sys

path = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(path))

import pytest
from models import MarketDataPoint
from data_loader import load_market_data


@pytest.fixture
def sample_data_points():
    return load_market_data("assignment3_market_data.csv")


def test_load_market_data(sample_data_points):
    assert isinstance(sample_data_points, list)
    assert all(isinstance(dp, MarketDataPoint) for dp in sample_data_points)
    assert len(sample_data_points) > 0
    first_dp = sample_data_points[0]
    assert hasattr(first_dp, "timestamp")
    assert hasattr(first_dp, "symbol")
    assert hasattr(first_dp, "price")
    assert isinstance(first_dp.timestamp, type(sample_data_points[0].timestamp))
    assert isinstance(first_dp.symbol, str)
    assert isinstance(first_dp.price, float)
