# constants.py

DELIMITER = b"*"
PRICE_PORT = 9999
NEWS_PORT = 9998
STRATEGY_PORT = 9997
HOST = "127.0.0.1"  # localhost
SYMBOLS = ["AAPL", "MSFT", "GOOG"]
INTERVAL = 0.01
BULL_THRESHOLD = 75
BEAR_THRESHOLD = 25

# PRICE GEN PARAMS (annualized)
MEAN = 0.1
VOL = 0.5

# TIME SCALING PARAMS
# INTERVAL: Physical time (real-world seconds) between price updates
# SIMULATED_TIME_DELTA: Simulated time (in seconds) that passes per update
#   Example: INTERVAL=1.0, SIMULATED_TIME_DELTA=60.0 means each physical second
#   represents 1 simulated minute of market time
SIMULATED_TIME_DELTA = 3600.0  # Default: 1 simulated second per update


# LOGGING
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s"
LOG_DATEFMT = "%H:%M:%S"
LOG_FILE = "out.log"
LOG_LEVEL = "INFO"
