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
    



class OrderBook:
    def __init__(self):
        self.bids = []
        self.asks = []

    def add_order(self, order):
        if order.side == "BUY":
            self.bids.append(order)
            self.bids = sorted(self.bids, key = lambda order:order.price)
        else:
            self.asks.append(order)
            self.asks = sorted(self.asks, key = lambda order:order.price)
            

    # def get_orders_by_symbol(self, symbol):
    #     # Your code here
    #     orderlist = []
    #     for order in self.orders:
    #         if order.symbol == symbol:
    #             orderlist.append(order)
    #     return orderlist 

    # def total_volume(self, side):
    #     # Your code here
    #     ordernum = 0
    #     for order in self.orders:
    #         if order.side ==side:
    #             ordernum+=order.quantity
    #     return ordernum

    def display_orders(self):
        print("Bids: ")
        for order in self.bids:
            print(f"Buy {order.quantity} of {order.symbol} at {order.price}")
        
        print("Asks: ")
        for order in self.asks:
            print(f"Sell {order.quantity} of {order.symbol} at {order.price}")


o1 = Order("AAPL", 100, 175.50, "BUY")
o2 = Order("AAPL", 50, 176.00, "SELL")
o3 = Order("MSFT", 200, 290.00, "BUY")

book = OrderBook()
book.add_order(o1)
book.add_order(o2)
book.add_order(o3)

book.display_orders()