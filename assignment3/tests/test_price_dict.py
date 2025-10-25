import pathlib, sys
import pytest

path = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(path))


from strategies import PriceDict


@pytest.fixture
def empty_price_dict():
    return PriceDict(window=5)


@pytest.fixture
def price_dict():
    p_dict = PriceDict(window=5)
    prices = [150.0, 152.0, 151.0, 153.0, 154.0]
    for price in prices:
        p_dict.add_price("AAPL", price)
    return p_dict


def test_add_price_new_symbol(empty_price_dict):
    empty_price_dict.add_price("AAPL", 150.0)
    assert "AAPL" in empty_price_dict._PriceDict__prices
    assert empty_price_dict._PriceDict__prices["AAPL"] == [150.0, 0, 0, 0, 0]
    assert empty_price_dict._PriceDict__index["AAPL"] == 0


def test_add_price_existing_symbol(price_dict):

    assert price_dict._PriceDict__prices["AAPL"] == [150.0, 152.0, 151.0, 153.0, 154.0]
    assert price_dict._PriceDict__index["AAPL"] == 4

    # Add another price to test the circular buffer behavior
    price_dict.add_price("AAPL", 156.0)
    assert price_dict._PriceDict__prices["AAPL"] == [156.0, 152.0, 151.0, 153.0, 154.0]
    assert price_dict._PriceDict__index["AAPL"] == 5

    for _ in range(4):
        price_dict.add_price("AAPL", 158.0)

    assert price_dict._PriceDict__prices["AAPL"] == [156.0, 158.0, 158.0, 158.0, 158.0]
    assert price_dict._PriceDict__index["AAPL"] == 9


def test_price_dict_sum(price_dict):
    # Initial sum after adding 5 prices
    assert price_dict._PriceDict__sums["AAPL"] == 760.0  # 150 + 152 + 151 + 153 + 154

    # Add a new price and check the updated sum
    price_dict.add_price("AAPL", 156.0)
    assert price_dict._PriceDict__sums["AAPL"] == 766.0  # 152 + 151 + 153 + 154 + 156

    # Add more prices to test circular behavior
    for _ in range(4):
        price_dict.add_price("AAPL", 158.0)

    assert price_dict._PriceDict__sums["AAPL"] == 788.0  # 156 + 158 + 158 + 158 + 158


def test_get_moving_average(price_dict):
    assert price_dict.get_moving_average("AAPL") == 152.0  # 760 / 5

    price_dict.add_price("AAPL", 156.0)
    assert price_dict.get_moving_average("AAPL") == 153.2  # 766 / 5

    for _ in range(4):
        price_dict.add_price("AAPL", 158.0)

    assert price_dict.get_moving_average("AAPL") == 157.6  # 788 / 5
