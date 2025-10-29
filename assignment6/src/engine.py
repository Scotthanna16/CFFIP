# engine.py

from .data_loader import CSVAdapter
from .patterns.strategy import Strategy
from .patterns.command import CommandInvoker, ExecuteOrderCommand
from .patterns.observer import SignalPublisher
from .patterns.builder import PortfolioGroup


class Engine:

    def __init__(
        self,
        filepath: str,
        Strategy: Strategy,
        Publisher: SignalPublisher,
        Portfolio: PortfolioGroup,
    ):
        self.__filepath = filepath
        self.__strategy = Strategy
        self.__publisher = Publisher
        self.__portfolio = Portfolio

    def run(self):
        DataLoader = CSVAdapter(self.__filepath)
        data = DataLoader.load_market_data()
        for point in data:
            signal = self.__strategy.generate_signals(point)
            if len(signal) == 1:
                command = ExecuteOrderCommand(
                    self.__portfolio, point.symbol, 1, signal[0], point.price
                )

                invoker = CommandInvoker()
                invoker.execute(command)
                self.__publisher.notify(
                    {
                        "symbol": point.symbol,
                        "price": point.price,
                        "action": signal[0],
                        "quantity": 1,
                    }
                )
