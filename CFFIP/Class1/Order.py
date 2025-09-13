class Order:
    def __init__(self, symbol, quant, price, side):
        self.symbol = symbol
        self.quantity = quant
        self.price = price
        self.side = side
    
    def value(self):
        return self.quantity*self.price

    def summary(self):
        string = self.side + " " + str(self.quantity) + " shares of "+str(self.symbol)+ " at $" +str(self.price)  +" each. Total: $" + str(self.quantity*self.price)
        return string
    

