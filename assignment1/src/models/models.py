# models.py
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict


@dataclass(frozen=True)
class MarketDataPoint:
    timestamp: datetime
    symbol: str
    price: float


class OrderError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ExecutionError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class Order:
    def __init__(self, action, symbol, quantity, price, status):
        self.__symbol = symbol.upper()
        self.__price = price
        self.__quantity = quantity
        self.__status = status
        self.__action = action.upper()

    @property
    def action(self):
        return self.__action

    @classmethod
    def from_signal(cls, signal):
        if signal.action.upper() not in ["BUY", "SELL"]:
            raise OrderError("Action must be either 'BUY' or 'SELL'")

        if signal.quantity <= 0:
            raise OrderError("Quantity must be a positive integer")

        if signal.price < 0:
            raise OrderError("Price cannot be a negative number")

        # if portfolio:

        #     if signal.action.upper() == "BUY":
        #         total_cost = signal.quantity * signal.price
        #         if total_cost > portfolio._Portfolio__cash:
        #             raise ExecutionError("Insufficient cash to execute the buy order")

        #     elif signal.action.upper() == "SELL":
        #         current_position = portfolio._Portfolio__portfolio[signal.symbol][
        #             "quantity"
        #         ]
        #         if current_position <= 0:
        #             raise ExecutionError("No holdings to sell for the given symbol")
        #         if signal.quantity > abs(current_position):
        #             raise ExecutionError(
        #                 "Attempting to sell more than current holdings"
        #             )

        return cls(
            action=signal.action,
            symbol=signal.symbol,
            quantity=signal.quantity,
            price=signal.price,
            status="FILLED",
        )

    @action.setter
    def action(self, new_action):
        self.__action = new_action

    @property
    def symbol(self):
        return self.__symbol

    @symbol.setter
    def symbol(self, new_symbol):
        self.__symbol = new_symbol

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, new_price):
        if new_price < 0:
            raise OrderError("Price cannot be a negative number")
        self.__price = new_price

    @property
    def quantity(self):
        return self.__quantity

    @quantity.setter
    def quantity(self, new_quant):
        if new_quant <= 0:
            raise OrderError("Quantity must be a positive number")
        self.__quantity = new_quant

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status):
        if new_status == "Unfilled":
            raise OrderError("Order was unable to be filled")
        self.__status = new_status

    def __repr__(self):
        return f"Order(action={self.__action}, symbol={self.__symbol}, quantity={self.__quantity}, price={self.__price}, status={self.__status})"


class Portfolio:
    """
    Store open positions in a dictionary. symbol, quantity, and average price.
    """

    def __init__(self, initial_cash: float = 1_000_000):
        self.__portfolio = defaultdict(lambda: {"quantity": 0, "avg_price": 0})
        self.__cash = float(initial_cash)

    def add_order(self, order: Order):
        def sign(x: int) -> int:
            return (x > 0) - (x < 0)  # returns 1, -1, or 0

        symbol_data = self.__portfolio[order.symbol]
        qty, avg_price = symbol_data["quantity"], symbol_data["avg_price"]
        position = sign(qty)
        volume_cost = order.quantity * order.price

        match position:
            case 0:  # No position
                symbol_data["avg_price"] = order.price
                if order.action == "BUY":
                    symbol_data["quantity"] += order.quantity
                    self.__cash -= volume_cost
                elif order.action == "SELL":
                    symbol_data["quantity"] -= order.quantity
                    self.__cash += volume_cost

            case 1:  # Long position
                if order.action == "BUY":
                    new_quantity = qty + order.quantity
                    new_avg_price = (qty * avg_price + volume_cost) / new_quantity
                    symbol_data["quantity"] = new_quantity
                    symbol_data["avg_price"] = new_avg_price
                    self.__cash -= volume_cost

                elif order.action == "SELL":
                    if order.quantity == qty:  # Closing entire long
                        symbol_data.update({"quantity": 0, "avg_price": 0})
                        self.__cash += volume_cost
                    elif order.quantity > qty:  # Overselling
                        symbol_data["quantity"] = qty - order.quantity
                        symbol_data["avg_price"] = order.price
                        self.__cash += volume_cost
                    else:  # Partial sell
                        symbol_data["quantity"] -= order.quantity
                        self.__cash += volume_cost

            case -1:  # Short position
                if order.action == "BUY":
                    abs_qty = abs(qty)
                    if order.quantity == abs_qty:  # Closing entire short
                        symbol_data.update({"quantity": 0, "avg_price": 0})
                        self.__cash -= volume_cost
                    elif order.quantity > abs_qty:  # Overbuying
                        symbol_data["quantity"] = qty + order.quantity
                        symbol_data["avg_price"] = order.price
                        self.__cash -= volume_cost
                    else:  # Partial cover
                        symbol_data["quantity"] += order.quantity
                        self.__cash -= volume_cost

                elif order.action == "SELL":
                    new_quantity = qty - order.quantity
                    new_avg_price = (qty * avg_price - volume_cost) / new_quantity
                    symbol_data["quantity"] = new_quantity
                    symbol_data["avg_price"] = new_avg_price
                    self.__cash += volume_cost

    @property
    def positions(self):

        pos = {
            symbol: f"{self.__portfolio[symbol]["quantity"]} @ {self.__portfolio[symbol]["avg_price"]}"
            for symbol in self.__portfolio
        }
        pos["Cash"] = f"{self.__cash:.2f}"
        return pos

    def display(self):
        print(self.__portfolio)
        print(self.__cash)

    def snapshot(self) -> dict:
        """
        Return a numeric snapshot port for reporting
        Structure:
        { 'AAPL': {'quantity': 10, 'avg_price': 100.0}, ..., 'Cash': 12345.67 }
        """
        snap = {
            symbol: {
                "quantity": self.__portfolio[symbol]["quantity"],
                "avg_price": self.__portfolio[symbol]["avg_price"],
            }
            for symbol in self.__portfolio
        }
        snap["Cash"] = float(self.__cash)
        return snap


@dataclass(frozen=True)
class Signal:
    action: str  # "buy" or "sell"
    symbol: str
    quantity: int
    price: float


# O1 = Order('Buy', "AAPL", 10, 100, 'filled')

# P = Portfolio()
# P.add_order(O1)
# P.display() # Should print: {'AAPL': {'quantity': 10, 'avg_price': 100}}

# O2 = Order('Buy', "AAPL", 10, 200, 'filled')

# P.add_order(O2)
# P.display() # Should print: {'AAPL': {'quantity': 20, 'avg_price': 150.0}}

# O3 = Order('Buy', "MSFT", 10, 200, 'filled')

# P.add_order(O3)
# P.display() # Should print: {'AAPL': {'quantity': 20, 'avg_price': 150.0}, 'MSFT': {'quantity': 10, 'avg_price': 200}}

# print(P.total_Value()) #Should print 5000

# O4 = Order("Sell", "AAPL", 10, 100, 'filled')

# P.add_order(O4)
# P.display() # Should print: {'AAPL': {'quantity': 10, 'avg_price': 200.0}, 'MSFT': {'quantity': 10, 'avg_price': 200}}

# print(P.total_Value()) #Should print 4000
