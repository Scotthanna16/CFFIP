"""
Configuration constants for the trading system.

This module centralizes all configuration constants used throughout
the trading system to improve maintainability and avoid magic numbers.
"""

from typing import Final

# Data download configuration
DEFAULT_OUTPUT_DIRECTORY: Final[str] = "data"
DEFAULT_START_DATE: Final[str] = "2005-01-01"
DEFAULT_END_DATE: Final[str] = "2025-01-01"
DEFAULT_BATCH_SIZE: Final[int] = 50
DEFAULT_RETRY_ATTEMPTS: Final[int] = 3
DEFAULT_DELAY_BETWEEN_BATCHES: Final[float] = 2.0  # seconds
DEFAULT_DELAY_BETWEEN_REQUESTS: Final[float] = 0.5  # seconds
DEFAULT_MIN_DATA_POINTS: Final[int] = 100

# Portfolio configuration
DEFAULT_INITIAL_CASH: Final[float] = 1_000_000

# Strategy configuration
DEFAULT_SHORT_WINDOW: Final[int] = 20
DEFAULT_LONG_WINDOW: Final[int] = 50

# Logging configuration
DEFAULT_LOG_FORMAT: Final[str] = "%(asctime)s - %(levelname)s - %(message)s"

# File extensions
PARQUET_EXTENSION: Final[str] = ".parquet"
CSV_EXTENSION: Final[str] = ".csv"
JSON_EXTENSION: Final[str] = ".json"

# HTTP configuration
DEFAULT_TIMEOUT: Final[int] = 30
DEFAULT_USER_AGENT: Final[str] = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/91.0.4472.124 Safari/537.36"
)

# Data validation thresholds
MIN_PRICE_VALUE: Final[float] = 0.01
MAX_MISSING_DATA_PCT: Final[float] = 50.0
