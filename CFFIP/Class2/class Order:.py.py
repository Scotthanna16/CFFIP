class Order:
    def __init__(self, symbol, price, side, quantity):
        self.symbol = symbol
        self.price = price
        self.side = side
        self.quantity = quantity


    def display(self):
        return f"Order({self.symbol}, {self.price}, {self.side}, {self.quantity})"

    def __eq__(self,other):
        return self.price ==other.price and self.quantity == other.quantity and self.symbol == other.symbol and self.side == other.side

class FOKOrder(Order):
    def __init__(self, symbol, price, side, quantity,sa):
        super().__init__(symbol, price, side, quantity)
        self.spec_att = sa

    def display(self):
        a = super().display()
        return f"FOKOrder({self.symbol}, {self.price}, {self.side}, {self.quantity}) " + a

    def __eq__(self, other):
        return super().__eq__(other) and self.spec_att == other.spec_att




fok = FOKOrder("AAPL", 10, 'bid', 100, 'Scott')
fok2 = FOKOrder("AAPL", 10, 'bid', 100, 'Scott')

print(fok.display())
print(fok == fok2)
