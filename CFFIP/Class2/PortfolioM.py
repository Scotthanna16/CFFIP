class Trade:
    def __init__(self, symbol, quantity, price):
        self.symbol = symbol
        self.quantity = quantity
        self.price = price

    def value(self):
        return self.quantity * self.price

class Portfolio:
    def __init__(self):
        self.trades = []

    def total_value(self):
        total = 0
        for trade in self.trades:
            total += trade.value()
        return total

    def __add__(self, other):
        np = Portfolio()
        np.trades = self.trades + other.trades  # combine flat
        return np

    def __iadd__(self, trade):
        self.trades.append(trade)
        return self

    def __eq__(self, other):
        return self.total_value() == other.total_value()

    def __str__(self):
        print(f"Total Portfolio Value: {self.total_value()}")
        return ""



t1 = Trade("AAPL", 100, 150)
t2 = Trade("MSFT", 50, 300)
t3 = Trade("GOOG", 20, 1000)

p1 = Portfolio()
p2 = Portfolio()

p1 += t1
p2 += t2
p2 += t3

print(p1)           # Portfolio value: $15,000.00  
print(p2)           # Portfolio value: $35,000.00  
print(p1 == p2)     # False

p3 = p1 + p2
print(p3)           # Portfolio value: $50,000.00