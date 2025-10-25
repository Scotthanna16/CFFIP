# backtester/broker.py
class Broker:
    def __init__(self, cash: float = 1_000_000):
        self.cash = cash
        self.position = 0

    def market_order(self, side: str, qty: int, price: float):

        if qty <= 0:
            raise ValueError("Quantity must be positive")

        if side == "BUY":
            if self.cash >= qty * price:
                self.cash -= qty * price
                self.position += qty
            else:
                raise Exception("Not Enough Cash")
        else:
            self.cash += price * qty
            self.position -= qty
