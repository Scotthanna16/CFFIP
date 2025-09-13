import time
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


def benchmark_insert(n):
    book = OrderBook()
    start = time.perf_counter()
    for i in range(n):
        o = Order("AAPL", i + 1, 150 + (i % 100) * 0.01, "BUY")
        book.add_order(o)
    end = time.perf_counter()
    print(f"{n:>8} orders → {end - start:.4f} seconds")

# Run benchmarks
for size in [100, 10_000, 100_000, 1_000_000]:
    benchmark_insert(size)