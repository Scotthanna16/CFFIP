from src.analytics import (
    Instrument,
    VolatilityDecorator,
    BetaDecorator,
    DrawdownDecorator,
)
from src.patterns.factory import load_instruments_from_csv
from src.data_loader import CSVAdapter


def test_volatility_decorators(sample_instrument_data):
    instruments = load_instruments_from_csv("data/instruments.csv")
    dataloader = CSVAdapter("data/market_data.csv")

    for inst in instruments:
        mydata = dataloader.get_data_prices(inst.symbol)
        inst.add_price_list(mydata)

    dec = DrawdownDecorator(
        BetaDecorator(VolatilityDecorator(instruments[0]), instruments[3].prices)
    )

    # dec = DrawdownDecorator(VolatilityDecorator(instruments[0]))
    metrics = dec.get_metrics()
    print(metrics)
    assert "volatility" in metrics
    assert "beta" in metrics
    assert "max_drawdown" in metrics
    assert isinstance(metrics["volatility"], float)
    assert isinstance(metrics["beta"], float)
    assert isinstance(metrics["max_drawdown"], float)
