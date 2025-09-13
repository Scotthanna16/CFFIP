import random
class ExecutionEngine:
    def execute_trade(self, symbol, quantity, price):
        print(f"Executing trade of {symbol} with quantity {quantity} at price {price}")

class Logger:
    def execute_trade(self,symbol, quantity, price):
        print(f"Logging trade of {symbol} with quantity {quantity} at price {price}")
        super().execute_trade(symbol, quantity, price)

class Strategy:
    def execute_trade(self):
        print("Selecting trade parameters")
        pick = random.randint(0,2)
        quant = random.randint(1,1000)
        tickerlist = ["AAPL", "MSFT", "NVDA"]
        Pricelist = [234, 510, 177.8]
        super().execute_trade(tickerlist[pick], quant, Pricelist[pick])

class TradingBot(Strategy, Logger, ExecutionEngine):
    def execute_trade(self):
        print("Starting trade sequence")
        super().execute_trade()

# Test
bot = TradingBot()
bot.execute_trade()

# Inspect MRO
print(TradingBot.__mro__)