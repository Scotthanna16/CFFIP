import logging
from multiprocessing import Lock, shared_memory

import numpy as np

DTYPE = np.dtype([("symbol", "S10"), ("price", "f8")])

logger = logging.getLogger("SharedMemory")


class SharedPriceBook:
    """Wrapper for structured memory access"""

    def __init__(self, symbols, lock, name=None):

        self.symbols = sorted(symbols)
        self.num_symbols = len(symbols)
        self.lock = lock

        self.size = DTYPE.itemsize * self.num_symbols

        if name is None:
            self.shm = shared_memory.SharedMemory(create=True, size=self.size)
            self.name = self.shm.name
            self._creator = True
            self._init_memory()

        else:

            self.name = name
            self.shm = shared_memory.SharedMemory(name=self.name)
            self.array = np.frombuffer(
                self.shm.buf, dtype=DTYPE, count=self.num_symbols
            )
            self._creator = False
            # self.array = np.ndarray(
            #     buffer=self.shm.buf, dtype=DTYPE, shape=(self.num_symbols, 1)
            # )

    def _init_memory(self):

        # self.array = np.ndarray(
        #     buffer=self.shm.buf, dtype=DTYPE, shape=(self.num_symbols, 1)
        # )
        self.array = np.frombuffer(self.shm.buf, dtype=DTYPE, count=self.num_symbols)
        for i, symbol in enumerate(self.symbols):
            self.array["symbol"][i] = symbol.encode("utf-8")
            self.array["price"][i] = np.nan

    def update(self, symbol: str, price: float):
        """Update price for a symbol in shared memory."""
        symb = symbol.encode("utf-8")
        with self.lock:
            idx = np.where(self.array["symbol"] == symb)[0]
            if idx.size > 0:
                self.array["price"][idx[0]] = price
                logger.debug(
                    f"SharedMemory: Updated {symbol} to {price:.2f} in shared memory"
                )
            else:
                logger.warning(
                    f"Symbol '{symbol}' not found in price book, update ignored. Available symbols: {[s.decode('utf-8') for s in self.array['symbol']]}"
                )

    def read(self, symbol: str):

        symb = symbol.encode("utf-8")
        with self.lock:
            idx = np.where(self.array["symbol"] == symb)[0]
            if idx.size > 0:
                price = self.array["price"][idx[0]]
                logger.debug(f"SharedMemory: Read {symbol} = {price}")
                return price
            else:
                logger.warning(
                    f"SharedMemory: Symbol '{symbol}' not found in price book"
                )
                return None

    def close(self):
        """Release and clean up shared memory resources."""
        # Remove reference to numpy view of shared memory
        with self.lock:
            self.array = None
        # Ensure cleanup is thread-safe
        with self.lock:
            try:
                self.shm.close()
            except FileNotFoundError:
                pass
            except AttributeError:
                pass  # Shared memory already closed/detached

            # Only unlink if this process created the shared memory
            if getattr(self, "_creator", False):
                try:
                    self.shm.unlink()
                except FileNotFoundError:
                    pass  # Already unlinked or deleted
                except AttributeError:
                    pass  # Already cleaned up or never created


if __name__ == "__main__":

    lock = Lock()
    book = SharedPriceBook(symbols=["AAPL", "MSFT"], lock=lock)

    print(book.name)

    book.update("AAPL", 120.0)
    book.update("MSFT", 130.0)

    print(book.read("AAPL"))
    print(book.read("MSFT"))

    book.close()


# import numpy as np

# from multiprocessing import shared_memory, Lock


# class SharedPriceBook:
#     def __init__(self, symbols, lock, name=None):
#         self.symbols = symbols
#         self.dtype = np.dtype([("symbol", "U8"), ("price", "f8")])
#         self.shape = len(symbols)
#         self.lock = lock

#         if name is None:
#             # Create new shared memory
#             self.shm = shared_memory.SharedMemory(
#                 create=True,
#                 size=self.shape * self.dtype.itemsize,
#                 name="orderbook_shm",
#             )
#             self.owns_shm = True

#             self.data = np.ndarray(self.shape, dtype=self.dtype, buffer=self.shm.buf)
#             self.data["symbol"] = symbols
#             self.data["price"] = np.zeros(len(symbols))
#         else:
#             # Attach to existing shared memory
#             self.shm = shared_memory.SharedMemory(name=name)
#             self.owns_shm = False
#             self.data = np.ndarray(self.shape, dtype=self.dtype, buffer=self.shm.buf)

#     def update(self, symbol, price):
#         with self.lock:
#             idx = np.where(self.data["symbol"] == symbol)[0]
#             if idx.size > 0:
#                 self.data["price"][idx[0]] = price

#     def read(self, symbol):
#         with self.lock:
#             idx = np.where(self.data["symbol"] == symbol)[0]
#             if idx.size > 0:
#                 return float(self.data["price"][idx[0]])
#             return None

#     def close(self):
#         self.shm.close()
#         if self.owns_shm:
#             self.shm.unlink()


# # if __name__ == "__main__":
# #     symbols = ["AAPL", "MSFT", "GOOG"]
# #     lock = Lock()

# #     # Create shared memory in parent
# #     book = SharedPriceBook(symbols, lock)
# #     print("Initial prices:", [book.read(sym) for sym in symbols])

# #     # Test single-process updates
# #     book.update("AAPL", 150.25)
# #     print("After single-process update, AAPL =", book.read("AAPL"))
# #     book.update("AAPL", 151.25)
# #     print("After single-process update, AAPL =", book.read("AAPL"))
# #     book.close()
