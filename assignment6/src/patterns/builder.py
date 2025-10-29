# patterns/builder.py
import json
from src.models import PortfolioComponent
from collections import defaultdict

"""
Builder Pattern
- Problem: Construct complex portfolios with nested positions and metadata.
- Expectations:
    - Implement PortfolioBuilder with fluent methods:
        - add_position(symbol, quantity, price)
        - set_owner(name)
        - add_subportfolio(name, builder)
        - build() -> Portfolio
    - Demonstrate building from portfolio_structure.json.
"""


class Position(PortfolioComponent):
    def __init__(self, symbol: str, quantity: int, price: float):
        self.symbol = symbol
        self.quantity = quantity
        self.price = price

    def get_value(self) -> float:
        return self.quantity * self.price

    def get_positions(self) -> list:
        return [self]

    def __repr__(self):
        return f"Position(symbol={self.symbol}, quantity={self.quantity}, price={self.price})"


class PortfolioGroup(PortfolioComponent):
    def __init__(self, name: str = "unnamed"):
        self.name = name
        self.owner = None
        self.components = []

    def add_component(self, component: PortfolioComponent):
        self.components.append(component)

    def remove_component(self, component: PortfolioComponent):
        self.components.remove(component)

    def get_value(self) -> float:
        return sum(component.get_value() for component in self.components)

    def get_positions(self) -> list:
        positions = []
        for component in self.components:
            positions.extend(component.get_positions())
        return positions

    def details(self):
        positions = []
        subportfolios = []
        for component in self.components:
            if isinstance(component, Position):
                positions.append(
                    {
                        "symbol": component.symbol,
                        "quantity": component.quantity,
                        "price": component.price,
                    }
                )
            else:
                subportfolios.append(component.details())

        res = {}
        if self.owner:
            res["owner"] = self.owner
        if self.name:
            res["name"] = self.name
        if positions:
            res["positions"] = positions
        if subportfolios:
            res["sub_portfolios"] = subportfolios

        return res

    def aggregate_positions(self):
        position_by_symbol = defaultdict(list)

        position_by_symbol = defaultdict(list)
        for position in self.get_positions():
            position_by_symbol[position.symbol].append(position)

        res = {}
        for symbol, positions in position_by_symbol.items():
            total = 0
            avg = 0.0
            for position in positions:
                new_total = total + position.quantity
                if new_total * total > 0:
                    avg = (avg * total + position.price * position.quantity) / new_total
                elif new_total * total < 0:
                    avg = position.price
                elif new_total == 0:
                    avg = 0.0
                else:
                    avg = position.price
                total = new_total

            res[symbol] = {
                "total_quantity": total,
                "average_price": avg,
            }

        return res


class PortfolioBuilder:
    def __init__(self, name: str = "unnamed"):
        self.portfolio = PortfolioGroup(name)

    def add_position(self, symbol: str, quantity: int, price: float):
        position = Position(symbol, quantity, price)
        self.portfolio.add_component(position)
        return self

    def set_owner(self, name: str):
        self.portfolio.owner = name
        return self

    def add_subportfolio(self, name: str, builder: "PortfolioBuilder"):
        subportfolio = builder.build()
        subportfolio.name = name
        self.portfolio.add_component(subportfolio)
        return self

    def build(self) -> PortfolioGroup:
        return self.portfolio

    @classmethod
    def from_json(cls, filepath: str) -> "PortfolioBuilder":
        with open(filepath, "r") as f:
            data = json.load(f)

        def build_portfolio(data) -> PortfolioBuilder:
            builder = cls(data.get("name", "unnamed"))
            if "owner" in data:
                builder.set_owner(data["owner"])
            for pos in data.get("positions", []):
                builder.add_position(**pos)
            for sub in data.get("sub_portfolios", []):
                sub_builder = build_portfolio(sub)
                builder.add_subportfolio(sub.get("name", "unnamed"), sub_builder)

            return builder

        return build_portfolio(data=data)


if __name__ == "__main__":

    # builder = PortfolioBuilder("Main Portfolio").set_owner("Alice")
    # builder.add_position("AAPL", 10, 150.0).add_position("GOOGL", 5, 2800.0)

    # sub_builder = PortfolioBuilder()
    # sub_builder.add_position("TSLA", 8, 700.0).add_position("AMZN", 2, 3300.0)

    # builder.add_subportfolio("Tech Stocks", sub_builder)

    # portfolio = builder.build()

    # print(json.dumps(portfolio.details(), indent=4))
    portfolio = PortfolioBuilder.from_json("jsons/portfolio_structure.json").build()
    # print(json.dumps(portfolio.details(), indent=4))

    assert portfolio.details() == json.load(open("jsons/portfolio_structure.json"))

    print(portfolio.get_value())  # Total value of the portfolio
    print(portfolio.get_positions())  # List of all positions in the portfolio
