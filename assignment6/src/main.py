# main.py

from .patterns.strategy import MeanReversionStrategy, BreakoutStrategy
from .patterns.observer import SignalPublisher, AlertObserver, LoggerObserver
from .patterns.builder import PortfolioGroup
from .engine import Engine
from .patterns.singleton import Config
import json
from .patterns.factory import load_instruments_from_csv, CSVAdapter
from .reporting import display_Instrument_analytics

# reporting.py
from .models import Instrument
from .analytics import VolatilityDecorator, BetaDecorator, DrawdownDecorator

# import enum stuff
from enum import Enum

strategies = {
    "MeanReversionStrategy": MeanReversionStrategy,
    "BreakoutStrategy": BreakoutStrategy,
}

if __name__ == "__main__":

    cfg = Config()
    data_path = cfg.data_path + "market_data.csv"
    # strategy = BreakoutStrategy.from_json("jsons/strategy_params.json")
    strategy = strategies["BreakoutStrategy"].from_json("jsons/strategy_params.json")

    publisher = SignalPublisher()
    Alert = AlertObserver(500)
    Logger = LoggerObserver(cfg.log_level)
    publisher.attach(Alert)
    publisher.attach(Logger)
    Portfolio = PortfolioGroup("genius")
    engine = Engine(data_path, strategy, publisher, Portfolio)
    engine.run()

    instruments = load_instruments_from_csv("data/instruments.csv")
    dataloader = CSVAdapter("data/market_data.csv")

    for inst in instruments:
        mydata = dataloader.get_data_prices(inst.symbol)
        inst.add_price_list(mydata)

    del instruments[2]
    for i in range(len(instruments)):
        metrics = display_Instrument_analytics(instruments[i], instruments[2].prices)
        print(metrics)
    print(Portfolio.aggregate_positions())
