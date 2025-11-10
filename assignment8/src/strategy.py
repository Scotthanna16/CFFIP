import logging
import socket
import time
from collections import defaultdict, deque
from multiprocessing import Event
from multiprocessing import Lock as MPLock
from threading import Thread
from typing import Dict, List

import numpy as np

from .constants import BEAR_THRESHOLD, BULL_THRESHOLD, DELIMITER, HOST, NEWS_PORT
from .shared_memory_utils import DTYPE, SharedPriceBook

logger = logging.getLogger("Strategy")


class Strategy:
    def __init__(
        self,
        shm_name: str,
        shm_lock,
        freq: float,
        news_host: str,
        news_port: int,
        strat_host: str,
        strat_port: int,
        symbols: List[str],
    ):
        self.sentiment_lock = MPLock()
        self.prices = {symbol: deque(maxlen=50) for symbol in symbols}
        self.current_position = None
        self.symbols = symbols
        self.sentiment: Dict[str, int] = {symbol: 50 for symbol in symbols}
        self.symbols = symbols

        self.s_host = strat_host
        self.s_port = strat_port
        self.n_host = news_host
        self.n_port = news_port

        self.running = Event()
        self.price_book = SharedPriceBook(name=shm_name, symbols=symbols, lock=shm_lock)

        self.freq = freq

    def stop(self) -> None:
        """Signal the strategy to stop all threads."""
        self.running.clear()
        logger.info("Stop signal sent")
        try:
            self.price_book.close()
        except Exception as e:
            logger.info(f"Exception when closing book in strategy {e}")

    def watch_news(self) -> None:
        """Watch news stream and update sentiment values."""
        RECONNECT_DELAY = 5.0

        while self.running.is_set():
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.n_host, self.n_port))
                    logger.info(
                        f"Connected to news stream at {self.n_host}:{self.n_port}"
                    )
                    buffer = b""

                    while self.running.is_set():
                        data = s.recv(1024)
                        if not data:
                            logger.warning(
                                "Connection closed by news stream, reconnecting..."
                            )
                            break

                        buffer += data
                        while DELIMITER in buffer:
                            packet, buffer = buffer.split(DELIMITER, 1)
                            if packet:
                                try:
                                    symb, sentiment = packet.decode("utf-8").split(",")
                                    with self.sentiment_lock:
                                        self.sentiment[symb] = int(sentiment)
                                    logger.debug(
                                        f"Updated sentiment for {symb}: {sentiment}"
                                    )
                                except ValueError as e:
                                    logger.warning(
                                        f"Failed to parse news packet '{packet.decode('utf-8', errors='replace')}': {e}"
                                    )

            except (ConnectionRefusedError, ConnectionResetError, OSError) as e:
                logger.error(
                    f"Connection error to news stream: {e}. Retrying in {RECONNECT_DELAY} seconds..."
                )
                time.sleep(RECONNECT_DELAY)

            except Exception as e:
                logger.error(f"Unexpected error in news watcher: {e}", exc_info=True)
                time.sleep(RECONNECT_DELAY)

    def generate_signal(self, *data) -> str:
        """Placeholder for signal generation logic."""
        # {Direction},{Quantity},{SYMBOL},{Price}
        symbol, prices, sentiment = data
        if len(prices) < 50:
            logger.debug(f"Price list at {len(prices)}")
            return None
        sma = sum(prices[-20:]) / 20  # 20-period simple moving average
        lma = sum(prices[-50:]) / 50  # 50-period simple moving average
        price_sig = sma - lma

        logger.debug(f"Compute LMA ({lma}) and SMA ({sma})")

        if sentiment > BULL_THRESHOLD:
            if price_sig > 0:
                signal = f"BUY,1,{symbol},{prices[-1]}"
                logger.info(f"Generated signal: {signal}")
                if self.current_position != "LONG":
                    self.current_position = "LONG"
                    return signal
                else:
                    return None
        elif sentiment < BEAR_THRESHOLD:
            if price_sig < 0:
                signal = f"SELL,1,{symbol},{prices[-1]}"
                logger.info(f"Generated signal: {signal}")
                if self.current_position != "SHORT":
                    self.current_position = "SHORT"
                    return signal
                else:
                    return None

        return

    @staticmethod
    def send_order(order: str, conn: socket.socket, delimiter: bytes) -> None:
        """Placeholder for order execution."""
        conn.sendall(order.encode("utf-8") + delimiter)

    def run_strategy(self) -> None:
        """Main strategy loop: reads shared memory, generates signals, sends orders."""
        self.running.set()
        news_thread = Thread(target=self.watch_news, daemon=True)
        news_thread.start()
        logger.info("Strategy started, waiting for order manager connection...")

        try:
            while self.running.is_set():
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        s.bind((self.s_host, self.s_port))
                        s.listen(5)
                        logger.info(
                            f"Listening for order manager on {self.s_host}:{self.s_port}"
                        )

                        order_manager, addr = s.accept()
                        logger.info(f"Order manager connected from {addr}")

                        while self.running.is_set():
                            for symbol in self.symbols:
                                price = self.price_book.read(symbol)
                                if price is not None and not np.isnan(price):
                                    price = float(price)
                                    self.prices[symbol].append(price)
                                    with self.sentiment_lock:
                                        sentiment = self.sentiment[symbol]

                                    signal = self.generate_signal(
                                        symbol, np.array(self.prices[symbol]), sentiment
                                    )
                                    if signal:
                                        try:
                                            self.send_order(
                                                signal, order_manager, DELIMITER
                                            )
                                            logger.debug(f"Sent order signal: {signal}")
                                        except Exception as e:
                                            logger.error(f"Error sending order: {e}")
                                            break

                            time.sleep(self.freq)

                except (ConnectionResetError, OSError) as e:
                    logger.warning(
                        f"Connection error with order manager: {e}. Waiting for reconnect..."
                    )
                    time.sleep(self.freq)
                except KeyboardInterrupt:
                    logger.info("Strategy interrupted by user")
                    break
                except Exception as e:
                    logger.error(f"Error during OMS communication: {e}", exc_info=True)
                    time.sleep(self.freq)

        except KeyboardInterrupt:
            logger.info("Strategy shutdown requested")
        except Exception as e:
            logger.error(f"Error in main strategy loop: {e}", exc_info=True)
        finally:
            logger.info("Strategy main loop terminated")


if __name__ == "__main__":
    from .gateway import NewsStream

    # Start mock NewsStream
    news_stream = NewsStream(HOST, NEWS_PORT, interval=1.0, symbols=["AAPL", "MSFT"])
    news_thread = Thread(target=news_stream.run, daemon=True)
    news_thread.start()

    # Initialize Strategy
    strategy = Strategy(
        shm_name=None,
        shm_lock=None,
        freq=1.0,
        news_host=HOST,
        news_port=NEWS_PORT,
        strat_host=None,
        strat_port=None,
        symbols=["AAPL", "MSFT"],
    )

    strat_thread = Thread(target=strategy.run_strategy)
    strat_thread.start()

    # Let it run
    time.sleep(10)
    print("Stopping strategy...")
    strategy.stop()

    # Give threads time to exit
    time.sleep(2)
    print("Done.")
