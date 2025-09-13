class Trader:
    def __init__(self, name, capital):
        self.name = name
        self.capital = capital 
    
    def greet(self):
        print(f"Hello, I’m {self.name} with ${self.capital}")



class AlgoTrader(Trader):

    def __init__(self, name, capital, strategy):
        super().__init__(name, capital)
        self.strategy = strategy
    
    def greet(self):
        print(f"Hello, I’m {self.name} with ${self.capital} and I trade using {self.strategy}")

    def run_strategy(self):
        print(f"Running {self.strategy} strategy")


t1 = Trader("Scott", 1000)

t1.greet()

T2 = AlgoTrader("Will", 1000, "Arbitrage")

T2.greet()

T2.run_strategy()