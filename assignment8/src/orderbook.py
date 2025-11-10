import logging
import socket
import time
from multiprocessing import Lock

from .constants import DELIMITER
from .shared_memory_utils import SharedPriceBook

logger = logging.getLogger("OrderBook")


class OrderBook:

    def __init__(self, host, port, symbols):

        self.lock = Lock()

        self.book = SharedPriceBook(symbols=symbols, lock=self.lock)
        self.shm_name = self.book.shm.name
        self.symbols = symbols

        self.host = host
        self.port = port

    def get_name_lock(self):

        return self.shm_name, self.lock

    def run_orderbook(self):
        """Main loop: connects to price feed, receives updates, writes to shared memory."""
        # Recreate the SharedPriceBook connection in this process
        # The array view needs to be recreated in the child process
        book = SharedPriceBook(name=self.shm_name, symbols=self.symbols, lock=self.lock)

        RECONNECT_DELAY = 5.0

        try:
            while True:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((self.host, self.port))
                        logger.info(
                            f"Connected to price feed at {self.host}:{self.port}"
                        )

                        buffer = b""
                        while True:
                            data = s.recv(1024)
                            if not data:
                                logger.warning(
                                    "Connection closed by server, reconnecting..."
                                )
                                break

                            buffer += data

                            while DELIMITER in buffer:
                                packet, buffer = buffer.split(DELIMITER, 1)
                                if packet:
                                    try:
                                        symbol, price_str = packet.decode(
                                            "utf-8"
                                        ).split(",")
                                        price = float(price_str)
                                        book.update(symbol, price)
                                        logger.debug(f"Updated {symbol}: {price:.2f}")

                                    except ValueError as e:
                                        logger.warning(
                                            f"Failed to parse packet '{packet.decode('utf-8', errors='replace')}': {e}"
                                        )

                except (ConnectionRefusedError, ConnectionResetError, OSError) as e:
                    logger.error(
                        f"Connection error: {e}. Retrying in {RECONNECT_DELAY} seconds..."
                    )
                    time.sleep(RECONNECT_DELAY)

                except KeyboardInterrupt:
                    logger.info("OrderBook interrupted by user")
                    break

                except Exception as e:
                    logger.error(f"Unexpected error: {e}", exc_info=True)
                    time.sleep(RECONNECT_DELAY)

        except KeyboardInterrupt:
            logger.info("OrderBook shutdown requested")

    def stop(self):
        """Clean up resources."""
        if hasattr(self, "book") and self.book is not None:
            try:
                self.book.close()
            except Exception as e:
                logger.warning(f"Error closing book: {e}")
        logger.info("OrderBook stopped and resources cleaned up.")

    def _cleanup_book(self, book):
        """Helper to clean up book in child process."""
        if book is not None:
            try:
                book.close()
            except Exception as e:
                logger.warning(f"Error closing book in child process: {e}")


if __name__ == "__main__":

    from multiprocessing import Process
    from threading import Thread

    from .constants import HOST, PRICE_PORT
    from .gateway import PriceStream

    ob = OrderBook(host=HOST, port=PRICE_PORT, symbols=["AAPL", "MSFT"])
    ps = PriceStream(
        host=HOST,
        port=PRICE_PORT,
        interval=1.0,
        symbols=["AAPL", "MSFT"],
        delimiter=DELIMITER,
    )

    pt = Thread(target=ps.run)
    obp = Process(target=ob.run_orderbook)

    pt.start()
    obp.start()

    obp.join()
    pt.join()
