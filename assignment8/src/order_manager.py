import logging
import socket
import time
from multiprocessing import Event

from .constants import DELIMITER, HOST, STRATEGY_PORT

logger = logging.getLogger("OrderManager")


class OrderManager:
    def __init__(self, host=HOST, port=STRATEGY_PORT):
        self.order_number = 0
        self.host = host
        self.port = port
        self.running = Event()

    def run_ordermanager(self):
        """Main loop: connects to strategy, receives orders, processes them."""
        RECONNECT_DELAY = 3.0

        self.running.set()
        logger.info(f"Order manager starting, connecting to {self.host}:{self.port}")

        try:
            while self.running.is_set():
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((self.host, self.port))
                        logger.info(f"Connected to strategy at {self.host}:{self.port}")

                        buf = b""
                        while self.running.is_set():
                            try:
                                data = s.recv(1024)
                                if not data:
                                    logger.warning(
                                        "Connection closed by strategy, reconnecting..."
                                    )
                                    break

                                buf += data
                                # Order format: "{Direction},{Quantity},{SYMBOL},{Price}"
                                while DELIMITER in buf:
                                    msg, buf = buf.split(DELIMITER, 1)
                                    try:
                                        direction, quantity, symbol, price = msg.decode(
                                            "utf-8"
                                        ).split(",")
                                        self.order_number += 1
                                        logger.info(
                                            f"Order #{self.order_number}: {direction} {quantity} {symbol} @ {price}"
                                        )
                                    except ValueError as e:
                                        logger.warning(
                                            f"Failed to parse order '{msg.decode('utf-8', errors='replace')}': {e}"
                                        )
                            except Exception as e:
                                logger.error(f"Error receiving data: {e}")
                                break

                except (ConnectionRefusedError, ConnectionResetError, OSError) as e:
                    logger.warning(
                        f"Connection failed: {e}. Retrying in {RECONNECT_DELAY} seconds..."
                    )
                    time.sleep(RECONNECT_DELAY)
                except KeyboardInterrupt:
                    logger.info("Order manager interrupted by user")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error: {e}", exc_info=True)
                    time.sleep(RECONNECT_DELAY)

        except KeyboardInterrupt:
            logger.info("Order manager shutdown requested")

    def stop(self):
        self.running.clear()
