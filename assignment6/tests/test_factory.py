from src.models import Stock, Bond, ETF


def test_create_stock(factory):
    data = {
        "type": "stock",
        "symbol": "AAPL",
        "price": 150.0,
        "sector": "Technology",
        "issuer": "Apple Inc.",
    }
    instrument = factory.create_instrument(data)
    assert isinstance(instrument, Stock)
    assert instrument.symbol == "AAPL"
    assert instrument.prices[-1] == 150.0
    assert instrument.sector == "Technology"
    assert instrument.issuer == "Apple Inc."


def test_create_bond(factory):
    data = {
        "type": "bond",
        "symbol": "US10Y",
        "price": 100.0,
        "sector": "Government",
        "issuer": "US Treasury",
        "maturity": "2031-12-31",
    }
    instrument = factory.create_instrument(data)
    assert isinstance(instrument, Bond)
    assert instrument.symbol == "US10Y"
    assert instrument.prices[-1] == 100.0
    assert instrument.sector == "Government"
    assert instrument.issuer == "US Treasury"
    assert instrument.maturity.isoformat() == "2031-12-31"


def test_create_etf(factory):
    data = {
        "type": "etf",
        "symbol": "SPY",
        "price": 400.0,
        "sector": "Index",
        "issuer": "SPDR",
    }
    instrument = factory.create_instrument(data)
    assert isinstance(instrument, ETF)
    assert instrument.symbol == "SPY"
    assert instrument.prices[-1] == 400.0
    assert instrument.sector == "Index"
    assert instrument.issuer == "SPDR"


def test_invalid_instrument_type(factory):
    data = {
        "type": "crypto",
        "symbol": "BTC",
        "price": 50000.0,
        "sector": "Digital Assets",
        "issuer": "Bitcoin",
    }
    try:
        factory.create_instrument(data)
    except ValueError as e:
        assert str(e) == "Unknown instrument type: crypto"


def test_missing_required_field(factory):
    data = {
        "type": "stock",
        "price": 150.0,
        "sector": "Technology",
        "issuer": "Apple Inc.",
    }
    try:
        factory.create_instrument(data)
    except ValueError as e:
        assert "Missing required instrument field" in str(e)


def test_missing_bond_maturity(factory):
    data = {
        "type": "bond",
        "symbol": "US10Y",
        "price": 100.0,
        "sector": "Government",
        "issuer": "US Treasury",
    }
    try:
        factory.create_instrument(data)
    except ValueError as e:
        assert str(e) == "Missing maturity field for Bond instrument"


def test_load_instruments_from_csv(sample_instrument_data, factory):
    instruments = []
    for row in sample_instrument_data:
        instrument = factory.create_instrument(row)
        instruments.append(instrument)

    assert len(instruments) == len(sample_instrument_data)
    assert isinstance(instruments[0], Stock)
    assert isinstance(instruments[1], Stock)
    assert isinstance(instruments[2], Bond)
    assert isinstance(instruments[3], ETF)
