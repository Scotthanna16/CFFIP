"""gateway.py: provides price and news streams over TCP sockets"""

import logging
import socket
import threading
import time
from abc import ABC, abstractmethod
from multiprocessing import Lock as MPLock

import numpy as np

from .constants import DELIMITER, HOST, NEWS_PORT, PRICE_PORT, MEAN, VOL

from enum import Enum


logger = logging.getLogger("Gateway")


class TimeDelta(Enum):
    SECOND = 1.0
    MINUTE = 60.0
    HOUR = 3600.0
    DAY = 3600 * 6.5
    YEAR = 3600 * 6.5 * 252


class Gateway:

    def __init__(
        self,
        host: str,
        price_port,
        news_port: int,
        price_interval: float,
        news_interval: float,
        symbols: list[str],
        delimiter="*",
        simulated_time_delta: float = 1.0,
    ):

        self.symbols = symbols
        self.price_stream = PriceStream(
            host,
            price_port,
            price_interval,
            symbols,
            delimiter,
            simulated_time_delta=simulated_time_delta,
        )
        self.news_stream = NewsStream(
            host, news_port, news_interval, symbols, delimiter
        )

    def run_gateway(self):
        # Run both servers in parallel threads
        threading.Thread(target=self.price_stream.run, daemon=True).start()
        threading.Thread(target=self.news_stream.run, daemon=True).start()

        logger.info(
            f"Running two streams: prices ({PRICE_PORT}) and sentiment ({NEWS_PORT})"
        )
        try:
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Gateway shutdown requested")
            self.stop()

    def stop(self):
        """Cleanly stop both price and news streams."""
        logger.info("Gateway: Initiating shutdown of both streams.")
        if hasattr(self, "price_stream") and self.price_stream:
            self.price_stream.stop()
        if hasattr(self, "news_stream") and self.news_stream:
            self.news_stream.stop()
        logger.info("Gateway: Shutdown complete.")

    # def gen_price(self, prices):
    #     for symbol in self.symbols:
    #         prices[symbol] *= random.choice([0.99, 1.01])
    #     return prices

    # def gen_sentiment(self):
    #     sents = {}
    #     for symbol in self.symbols:
    #         sents[symbol] = random.randint(0, 100)
    #     return sents

    # def gen_price_message(self, prices):
    #     submessages = [
    #         f"{symbol},{prices[symbol]}*".encode() for symbol in self.symbols
    #     ]
    #     message = b"".join(submessages)
    #     return message

    # def gen_sent_message(self, sents):
    #     submessages = [f"{symbol},{sents[symbol]}*".encode() for symbol in self.symbols]
    #     message = b"".join(submessages)
    #     return message

    # def prices(self):
    #     prices = {}
    #     for symbol in self.symbols:
    #         prices[symbol] = random.randint(100, 200)
    #     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     server_socket.bind(("localhost", 9000))
    #     server_socket.listen()
    #     print("Price gateway running on port 9000...")
    #     conn, addr = server_socket.accept()
    #     print("Client connected:", addr)
    #     running = True
    #     while running:

    #         prices = self.gen_price(prices)
    #         message = self.gen_price_message(prices)
    #         conn.sendall(message)
    #         time.sleep(0.1)

    # def sentiment(self):
    #     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     server_socket.bind(("localhost", 9001))
    #     server_socket.listen()
    #     print("Sentiment gateway running on port 9001...")
    #     conn, addr = server_socket.accept()
    #     print("Client connected:", addr)
    #     running = True
    #     running = True
    #     while running:

    #         sentiments = self.gen_sentiment()
    #         message = self.gen_sent_message(sentiments)
    #         conn.sendall(message)
    #         time.sleep(0.1)


class Stream(ABC):
    """Abstract base class for different types of streams."""

    def __init__(self, host: str, port: int, interval: float, delimiter="*"):
        self._host = host
        self._port = port
        self._interval = interval
        self._running = False
        self._lock = MPLock()
        self._delim = delimiter
        # socket setup
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )  # Allow address reuse
        self._server_socket.bind((self._host, self._port))
        self._server_socket.listen(5)  # Increased backlog
        # clients
        self._client_sockets = []
        # accept thread
        self._thread = None

    @abstractmethod
    def generate_data(self) -> list[str]:
        pass

    def generate_message(self, data: list[str]) -> bytes:
        """Encodes your data into bytes"""
        return (self._delim.join(data) + self._delim).encode()

    def accept_clients(self):
        while self._running:
            try:
                conn, addr = self._server_socket.accept()
                logger.info(f"{self.__class__.__name__}: Client connected from {addr}")
                with self._lock:
                    self._client_sockets.append(conn)
            except OSError as e:
                if not self._running:
                    logger.debug(
                        f"{self.__class__.__name__}: Server socket closed; exiting accept loop"
                    )
                    break
                else:
                    logger.error(
                        f"{self.__class__.__name__}: Unexpected error in accept: {e}"
                    )
                    raise
            except Exception as e:
                logger.error(f"{self.__class__.__name__}: Error in accept loop: {e}")

    def broadcast(self, data: list):
        message = self.generate_message(data)
        with self._lock:
            for conn in self._client_sockets.copy():
                try:
                    conn.sendall(message)
                except Exception as e:
                    logger.warning(
                        f"{self.__class__.__name__}: Error sending to client, removing: {e}"
                    )
                    self._client_sockets.remove(conn)
                    try:
                        conn.close()
                    except OSError:
                        pass

    def _cleanup(self):
        self._running = False
        # Attempt self-connection to unblock accept loop
        try:
            temp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_client.connect((self._host, self._port))
            temp_client.close()
        except OSError:
            pass  # Ignore if socket is already closed
        # Join the accept thread
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
            if self._thread.is_alive():
                logger.warning(
                    f"{self.__class__.__name__}: Accept thread did not join in time"
                )
        # Close client sockets
        with self._lock:
            for conn in self._client_sockets[:]:
                try:
                    conn.shutdown(socket.SHUT_RDWR)
                    conn.close()
                except OSError:
                    pass
            self._client_sockets.clear()
        # Close server socket
        if self._server_socket:
            try:
                self._server_socket.shutdown(socket.SHUT_RDWR)
                self._server_socket.close()
                logger.info(f"{self.__class__.__name__}: Server socket closed")
            except OSError:
                logger.debug(f"{self.__class__.__name__}: Server socket already closed")

    def run(self):
        self._running = True
        self._thread = threading.Thread(target=self.accept_clients, daemon=True)
        self._thread.start()
        logger.info(
            f"{self.__class__.__name__}: Stream started on {self._host}:{self._port}"
        )
        try:
            while self._running:
                data = self.generate_data()
                self.broadcast(data)
                time.sleep(self._interval)
        except KeyboardInterrupt:
            logger.info(f"{self.__class__.__name__}: Stream interrupted by user")
        except Exception as e:
            logger.error(
                f"{self.__class__.__name__}: Exception in run loop: {e}", exc_info=True
            )
        finally:
            self.stop()

    def stop(self):
        """Clean up sockets, threads, and resources for the stream."""
        self._running = False
        # Close all client connections
        with self._lock:
            for conn in self._client_sockets[:]:
                try:
                    conn.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                try:
                    conn.close()
                except OSError:
                    pass
            self._client_sockets.clear()
        # Close the server socket
        if hasattr(self, "_server_socket") and self._server_socket:
            try:
                self._server_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                self._server_socket.close()
                logger.info(
                    f"{self.__class__.__name__}: Server socket closed by cleanup"
                )
            except OSError:
                logger.debug(
                    f"{self.__class__.__name__}: Server socket already closed (cleanup)"
                )
        # Join the accept thread if running
        if hasattr(self, "_thread") and self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
            if self._thread.is_alive():
                logger.warning(
                    f"{self.__class__.__name__}: Accept thread did not join in time (cleanup)"
                )


class TestStream(Stream):
    def generate_data(self) -> list[str]:
        return ["Hello, World!"]


class PriceStream(Stream):
    """Concrete implementation of a price stream.

    Args:
        host: Host address for the stream
        port: Port number for the stream
        interval: Physical time (real-world seconds) between price updates
        symbols: List of symbols to generate prices for
        delimiter: Message delimiter
        simulated_time_delta: Simulated time (in seconds) that passes per update.
                            This controls the scaling of volatility and drift.
                            Default is 1.0 (1 simulated second per update).
                            Example: if interval=1.0 and simulated_time_delta=60.0,
                            then each physical second represents 1 simulated minute.
    """

    def __init__(
        self,
        host: str,
        port: int,
        interval: float,
        symbols: list[str],
        delimiter="*",
        simulated_time_delta: float = 1.0,
    ):
        super().__init__(host, port, interval, delimiter)
        self._prices = {symbol: 100.0 for symbol in symbols}
        self._simulated_time_delta = simulated_time_delta

        # Calculate annualized time conversion
        # ann_to_dt = trading seconds in a year (252 trading days * 6.5 hours * 3600 seconds)
        ann_to_dt = 252 * 6.5 * 60 * 60  # trading seconds in a year

        # Scale volatility: volatility scales with sqrt(time)
        # If simulated_time_delta seconds pass per update, we need to scale by sqrt(simulated_time_delta / ann_to_dt)
        volatility_scale = np.sqrt(simulated_time_delta / ann_to_dt)
        self._volatilities = {symbol: VOL * volatility_scale for symbol in symbols}

        # Scale drift: drift scales linearly with time
        # If simulated_time_delta seconds pass per update, we need to scale by simulated_time_delta / ann_to_dt
        drift_scale = simulated_time_delta / ann_to_dt
        self._drifts = {symbol: MEAN * drift_scale for symbol in symbols}

    def generate_data(self) -> list[str]:

        new_prices = {}
        for symbol, price in self._prices.items():
            new_price = (
                1
                + self._drifts[symbol]
                + self._volatilities[symbol] * np.random.normal()
            ) * price

            new_prices[symbol] = new_price

        self._prices = new_prices

        return [f"{symbol},{price:.2f}" for symbol, price in new_prices.items()]


class NewsStream(Stream):
    """Concrete implementation of a news stream."""

    def __init__(
        self, host: str, port: int, interval: float, symbols: list[str], delimiter="*"
    ):
        super().__init__(host, port, interval, delimiter)
        self.symbols = symbols

    def generate_data(self):
        return [f"{symbol},{np.random.randint(0, 100)}" for symbol in self.symbols]


if __name__ == "__main__":

    from .constants import HOST, NEWS_PORT, PRICE_PORT

    gateway = Gateway(
        host=HOST,
        price_port=PRICE_PORT,
        price_interval=1.0,
        news_port=NEWS_PORT,
        news_interval=1.0,
        symbols=["AAPL", "MSFT", "GOOG"],
    )
    gateway.run_gateway()
