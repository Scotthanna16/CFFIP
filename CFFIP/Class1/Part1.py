class Order:
    def __init__(self, symbol, quant, price, side):
        self.symbol = symbol
        self.quantitiy = quant
        self.price = price
        self.side = side
    
    def value(self):
        return self.quantitiy*self.price

    def summary(self):
        string = self.side + " " + str(self.quantitiy) + " shares of "+str(self.symbol)+ " at $" +str(self.price)  +" each. Total: $" + str(self.quantitiy*self.price)
        return string
    