# models.py
from dataclasses import dataclass
from datetime import datetime, date
import numpy as np


from abc import ABC, abstractmethod


class Instrument(ABC):

    def __init__(
        self,
        symbol: str,
        price: float | int | list[float],
        sector: str,
        issuer: str,
    ):
        self._symbol = symbol.strip().upper()
        self._prices = (
            [float(p) for p in price] if isinstance(price, list) else [float(price)]
        )
        self._sector = sector.strip()
        self._issuer = issuer.strip()

    def info(self) -> dict:
        return {
            "Symbol": self._symbol,
            "Prices": self._prices,
            "Sector": self._sector,
            "Issuer": self._issuer,
        }

    @property
    def prices(self) -> list:
        return self._prices

    def add_price(self, price: float | int):
        self._prices.append(price)

    def add_price_list(self, prices: list[float | int]):
        self._prices.extend(prices)

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def sector(self) -> str:
        return self._sector

    @property
    def issuer(self) -> str:
        return self._issuer

    def get_metrics(self) -> dict[str, str | float]:
        return {"symbol": self._symbol}

    def __repr__(self):
        return f"Instrument(symbol={self._symbol}, prices={self._prices}, sector={self._sector}, issuer={self._issuer})"


class Stock(Instrument):

    def info(self):
        info = super().info()
        info["Type"] = "Stock"
        return info

    def __repr__(self):
        return f"Stock(symbol={self._symbol}, prices={self._prices}, sector={self._sector}, issuer={self._issuer})"


class Bond(Instrument):
    def __init__(
        self,
        symbol: str,
        price: float,
        sector: str,
        issuer: str,
        maturity: str | datetime | date,
    ):
        super().__init__(symbol, price, sector, issuer)
        self._maturity = self._parse_maturity(maturity)

    def _parse_maturity(self, maturity: str | datetime | date) -> date:
        if isinstance(maturity, date):
            return maturity
        elif isinstance(maturity, datetime):
            return maturity.date()
        else:
            return datetime.strptime(maturity, "%Y-%m-%d").date()

    def info(self):
        info = super().info()
        info["Type"] = "Bond"
        info["Maturity"] = self._maturity.isoformat()
        return info

    @property
    def maturity(self):
        return self._maturity

    def __repr__(self):
        return f"Bond(symbol={self._symbol}, prices={self._prices}, sector={self._sector}, issuer={self._issuer}, maturity={self._maturity})"


class ETF(Instrument):

    def info(self):
        info = super().info()
        info["Type"] = "ETF"
        return info

    def __repr__(self):
        return f"ETF(symbol={self._symbol}, prices={self._prices}, sector={self._sector}, issuer={self._issuer})"


@dataclass(frozen=True)
class MarketDataPoint:
    """
    Represents a single market data point.

    This immutable dataclass contains timestamp, symbol, and price information
    for a specific market observation.
    """

    timestamp: datetime
    symbol: str
    price: float

    def __post_init__(self):

        if not isinstance(self.timestamp, datetime):
            raise TypeError("timestamp must be a datetime object")
        if not isinstance(self.symbol, str):
            raise TypeError("symbol must be a string")
        if not isinstance(self.price, (float, int)) or self.price <= 0:
            raise TypeError("price must be a positive float or int")

        object.__setattr__(self, "symbol", self.symbol.strip().upper())
        object.__setattr__(self, "price", float(self.price))


# Composite Design Pattern for Portfolio
class PortfolioComponent(ABC):
    """
    Abstract base class for portfolio components.
    Leaf: position
    Composite: portfolio group
    """

    @abstractmethod
    def get_value(self) -> float:
        pass

    @abstractmethod
    def get_positions(self) -> list:
        pass
