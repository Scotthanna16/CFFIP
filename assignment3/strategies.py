from models import MarketDataPoint, Signal, MarketAction, Strategy, SignalList

"""
Time Complexity Analysis: 
- Naive MA has a time complexity of O(n) because it recalculates the sum of the prices every time, which requires
traversing the list
- Optimized MA has a time complexity of O(1) because it keeps a running total of the prices, therefore it
only has to do an addition and division operation to find the MA
- Windowed MA has a time complexity of O(1) because it keeps a running total of the prices in the window, therefore it
only has to do an addition, subtraction, and division operation to find the MA


Space Complexity Analysis:
- Naive MA has a space complexity of O(n) because it must keep track of every price tick for every stock
- Optimized MA has a space complexity of O(1) because it keeps a runing sum of the prices and the number of ticks 
seen for that stock, therefore it only has to store 2 number for each stock
- Windowed MA has a space complexity of O(k) where k is the window size because it has to keep k price ticks for 
each stock
"""


class NaiveMovingAverageStrategy(Strategy):
    """
    Space Complexity is O(n) because you store each price for each ticker
    """

    def __init__(self):
        self.__prices = {}

    """
    Runtime Complexity is O(n)
    """

    def generate_signals(self, tick: MarketDataPoint) -> SignalList:
        # Worst case runtime for append is O(n)
        if tick.symbol not in self.__prices:
            self.__prices[tick.symbol] = [tick.price]
        else:
            self.__prices[tick.symbol].append(tick.price)
        # Finding the moving average is O(n) because to sum you need to traverse entire list
        if tick.price > sum(self.__prices[tick.symbol]) / len(
            self.__prices[tick.symbol]
        ):
            return [
                Signal(
                    action=MarketAction.BUY,
                    symbol=tick.symbol,
                    quantity=1,
                    price=tick.price,
                )
            ]
        elif tick.price < sum(self.__prices[tick.symbol]) / len(
            self.__prices[tick.symbol]
        ):
            return [
                Signal(
                    action=MarketAction.SELL,
                    symbol=tick.symbol,
                    quantity=1,
                    price=tick.price,
                )
            ]
        else:
            return [
                Signal(
                    action=MarketAction.HOLD,
                    symbol=tick.symbol,
                    quantity=0,
                    price=tick.price,
                )
            ]


class OptimizedNaiveMovingAverageStrategy(Strategy):
    """
    Space Complexity is O(1) because you only store the running total for each ticker, and the number
    of prices
    """

    def __init__(self):
        self.__prices = {}

    """
    Runtime Complexity is O(1)
    """

    def generate_signals(self, tick: MarketDataPoint) -> SignalList:
        # Both of these operation have O(1) time complexity
        if tick.symbol not in self.__prices:
            self.__prices[tick.symbol] = [tick.price, 1]
        else:
            self.__prices[tick.symbol][0] += tick.price
            self.__prices[tick.symbol][1] += 1

        total = self.__prices[tick.symbol][0]
        length = self.__prices[tick.symbol][1]

        signals = []

        # Finding the moving average is O(1) now because you can access the sum in O(1)
        if tick.price > total / length:
            signals.append(
                Signal(
                    action=MarketAction.BUY,
                    symbol=tick.symbol,
                    quantity=1,
                    price=tick.price,
                )
            )
        elif tick.price < total / length:
            signals.append(
                Signal(
                    action=MarketAction.SELL,
                    symbol=tick.symbol,
                    quantity=1,
                    price=tick.price,
                )
            )
        else:
            signals.append(
                Signal(
                    action=MarketAction.HOLD,
                    symbol=tick.symbol,
                    quantity=0,
                    price=tick.price,
                )
            )

        return signals


class PriceDict:
    """maintains a dictionary of prices for each ticker symbol with a fixed window size."""

    def __init__(self, window=10):
        self.__prices = {}
        self.__index = {}
        self.__window = window
        self.__sums = {}

    """
    Because the list of prices for each ticker is of fixed size, insertion only takes O(1)
    """

    def add_price(self, symbol: str, price: float):
        if symbol not in self.__prices:
            self.__prices[symbol] = [price] + [0] * (self.__window - 1)
            self.__index[symbol] = 0
            self.__sums[symbol] = price
        else:
            # update the running sum by adding the new price and subtracting the price being replaced
            self.__index[symbol] = (index := self.__index[symbol] + 1)
            self.__sums[symbol] += price - self.__prices[symbol][index % self.__window]
            self.__prices[symbol][index % self.__window] = price

    """
    Taking the sum is O(1) because the window is of fixed size
    """

    def get_moving_average(self, symbol: str) -> float:
        if symbol not in self.__prices:
            raise ValueError(f"No prices for symbol: {symbol}")
        return self.__sums[symbol] / min(self.__index[symbol] + 1, self.__window)

    """
    Getting the length is O(1) as it is just accessing a integer in a dictionary
    """

    def get_len(self, symbol: str) -> int:
        if symbol not in self.__prices:
            raise ValueError(f"No prices for symbol: {symbol}")
        return min(self.__index[symbol] + 1, self.__window)


class WindowedMovingAverageStrategy(Strategy):
    """
    Space complexity is O(k) where k is the window size, because for each ticker you only need
    to store k prices
    """

    def __init__(self, window=10):

        self.__prices = PriceDict(window=window)  # keep track of prices
        self.__window = window

    def generate_signals(self, tick: MarketDataPoint) -> SignalList:

        signals = []
        # Runs in O(1)
        self.__prices.add_price(tick.symbol, tick.price)
        # Runs in O(1)
        if self.__prices.get_len(tick.symbol) >= self.__window:

            # Runs in O(1)
            avg = self.__prices.get_moving_average(tick.symbol)

            direction = (
                MarketAction.BUY
                if tick.price > avg
                else MarketAction.SELL if tick.price < avg else MarketAction.HOLD
            )

            signals.append(
                Signal(
                    action=direction,
                    symbol=tick.symbol,
                    quantity=1,
                    price=tick.price,
                )
            )
        else:
            signals.append(
                Signal(
                    action=MarketAction.HOLD,
                    symbol=tick.symbol,
                    quantity=0,
                    price=tick.price,
                )
            )

        return signals


from collections import deque


class DequePriceDict:
    """maintains a dictionary of prices for each ticker symbol with a fixed window size."""

    def __init__(self, window=10):
        self.__prices = {}
        self.__window = window
        self.__sums = {}

    def add_price(self, symbol: str, price: float):
        if symbol not in self.__prices:
            self.__prices[symbol] = deque([price], maxlen=self.__window)
            self.__sums[symbol] = price
        else:
            price_data = self.__prices[symbol]
            if len(price_data) == self.__window:
                self.__sums[symbol] -= price_data[0]
            # with deque, this removes the oldest price if at maxlen
            price_data.append(price)
            self.__sums[symbol] += price

    def get_moving_average(self, symbol: str) -> float:
        if symbol not in self.__prices:
            raise ValueError(f"No prices for symbol: {symbol}")
        return self.__sums[symbol] / len(self.__prices[symbol])

    def get_len(self, symbol: str) -> int:
        if symbol not in self.__prices:
            raise ValueError(f"No prices for symbol: {symbol}")
        return len(self.__prices[symbol])


class OptimizedWindowedMovingAverageStrategy(Strategy):
    """Optimized version using deque for O(1) operations and O(k) space."""

    def __init__(self, window=10):
        self.__prices = DequePriceDict(window=window)
        self.__window = window

    def generate_signals(self, tick: MarketDataPoint) -> SignalList:
        signals = []
        self.__prices.add_price(tick.symbol, tick.price)
        if self.__prices.get_len(tick.symbol) >= self.__window:
            avg = self.__prices.get_moving_average(tick.symbol)
            direction = (
                MarketAction.BUY
                if tick.price > avg
                else MarketAction.SELL if tick.price < avg else MarketAction.HOLD
            )
            signals.append(
                Signal(
                    action=direction,
                    symbol=tick.symbol,
                    quantity=1,
                    price=tick.price,
                )
            )
        else:
            signals.append(
                Signal(
                    action=MarketAction.HOLD,
                    symbol=tick.symbol,
                    quantity=0,
                    price=tick.price,
                )
            )
        return signals
