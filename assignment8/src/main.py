import logging
import signal
import sys
import time
from multiprocessing import Process

from .constants import (
    HOST,
    INTERVAL,
    LOG_DATEFMT,
    LOG_FILE,
    LOG_FORMAT,
    LOG_LEVEL,
    NEWS_PORT,
    PRICE_PORT,
    SIMULATED_TIME_DELTA,
    STRATEGY_PORT,
    SYMBOLS,
)
from .gateway import Gateway
from .order_manager import OrderManager
from .orderbook import OrderBook
from .strategy import Strategy

# Configure consistent logging format across all components
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    datefmt=LOG_DATEFMT,
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)

logger = logging.getLogger("Main")

# Global references for signal handlers
_components = {}
_processes = []


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    signal_name = signal.Signals(signum).name
    logger.info(f"Received {signal_name}, initiating graceful shutdown...")

    # Stop all components
    if "gateway" in _components:
        logger.info("Stopping gateway...")
        _components["gateway"].stop()

    if "orderbook" in _components:
        logger.info("Stopping orderbook...")
        _components["orderbook"].stop()

    if "strategy" in _components:
        logger.info("Stopping strategy...")
        _components["strategy"].stop()

    if "order_manager" in _components:
        logger.info("Stopping order manager...")
        _components["order_manager"].stop()

    # Terminate processes with timeout
    logger.info("Waiting for processes to terminate (timeout: 10s)...")
    for process in _processes:
        if process.is_alive():
            process.terminate()

    # Wait for processes to finish, ensuring OrderBook (shared memory creator) closes last
    # This helps ensure proper cleanup order - Strategy should close before OrderBook
    # Process order matches funcs: [gateway, orderbook, strategy, order_manager]
    process_names = ["gateway", "orderbook", "strategy", "order_manager"]
    process_map = {name: proc for name, proc in zip(process_names, _processes)}

    # Wait for non-creator processes first (Strategy uses shared memory but doesn't create it)
    for name in ["gateway", "order_manager", "strategy"]:
        if name in process_map:
            proc = process_map[name]
            proc.join(timeout=10.0)
            if proc.is_alive():
                logger.warning(f"Process {name} did not terminate, forcing kill...")
                proc.kill()
                proc.join()

    # Small delay to allow Strategy to fully release shared memory connection
    time.sleep(0.2)

    # Finally wait for OrderBook (the shared memory creator) to close and unlink
    if "orderbook" in process_map:
        proc = process_map["orderbook"]
        proc.join(timeout=10.0)
        if proc.is_alive():
            logger.warning("OrderBook process did not terminate, forcing kill...")
            proc.kill()
            proc.join()

    # Additional delay to allow final cleanup
    time.sleep(0.1)

    logger.info("Shutdown complete")

    sys.exit(0)


if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        gateway = Gateway(
            host=HOST,
            price_port=PRICE_PORT,
            price_interval=INTERVAL,
            news_port=NEWS_PORT,
            news_interval=INTERVAL,
            symbols=SYMBOLS,
            simulated_time_delta=SIMULATED_TIME_DELTA,
        )
        _components["gateway"] = gateway

        orderbook = OrderBook(HOST, PRICE_PORT, symbols=SYMBOLS)
        _components["orderbook"] = orderbook

        shm_name, lock = orderbook.get_name_lock()

        strategy = Strategy(
            shm_name,
            lock,
            freq=INTERVAL,
            news_host=HOST,
            news_port=NEWS_PORT,
            strat_host=HOST,
            strat_port=STRATEGY_PORT,
            symbols=SYMBOLS,
        )
        _components["strategy"] = strategy

        order_manager = OrderManager(host=HOST, port=STRATEGY_PORT)
        _components["order_manager"] = order_manager

        funcs = [
            gateway.run_gateway,
            orderbook.run_orderbook,
            strategy.run_strategy,
            order_manager.run_ordermanager,
        ]
        _processes = [Process(target=func) for func in funcs]

        logger.info("Starting all processes...")
        for i, process in enumerate(_processes):
            process.start()
            logger.info(f"Started process {i+1}/{len(_processes)}")
            time.sleep(1)  # Stagger process starts

        logger.info("All processes started. System running. Press Ctrl+C to shutdown.")

        # Wait for all processes
        for i, process in enumerate(_processes):
            process.join()
            logger.info(f"Process {i+1} terminated")

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        signal_handler(signal.SIGTERM, None)
