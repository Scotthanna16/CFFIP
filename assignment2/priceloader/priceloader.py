import yfinance as yf
import pandas as pd
import csv
import os
from typing import List, Optional, Dict, Union
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, handlers=[logging.FileHandler("trading_engine.log")]
)
logger = logging.getLogger(__name__)


class PriceLoader:
    """A clean, efficient price data loader for financial data."""

    def __init__(
        self,
        tickers: Optional[List[str]] = None,
        data_dir: str = "data",
        start_date: str = "2005-01-01",
        end_date: str = "2025-01-01",
    ):
        """Initialize the PriceLoader.

        Args:
            tickers: List of tickers to use. If None, loads from tickers.csv
            data_dir: Directory to store/load data files
            start_date: Start date for data downloads
            end_date: End date for data downloads

        # NOTE: Assumption if tickers is None is you want all sp500 tickers. Probably only use this if you are downloading all sp500 tickers.
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.start_date = start_date
        self.end_date = end_date

        if tickers is not None:
            self.tickers = tickers
        else:
            self.tickers = self._load_tickers_from_csv()

    def _load_tickers_from_csv(self) -> List[str]:
        """Load tickers from CSV file."""
        tickers_file = self.data_dir / "tickers.csv"
        if not tickers_file.exists():
            raise FileNotFoundError(f"Tickers file not found at {tickers_file}")

        with open(tickers_file, "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            return [row[0] for row in reader]

    def _get_file_path(self, ticker: str) -> Path:
        """Get the file path for a ticker's data."""
        return self.data_dir / f"{ticker}.parquet"

    def _download_single_ticker(self, ticker: str) -> bool:
        """Download data for a single ticker.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Downloading data for {ticker}...")
            df = yf.download(ticker, start=self.start_date, end=self.end_date)

            if df is None or df.empty:
                logger.warning(f"No data found for {ticker}")
                return False

            # Extract close prices
            close_prices = df["Close"] if "Close" in df.columns else df.iloc[:, 0]
            file_path = self._get_file_path(ticker)
            close_prices.to_parquet(file_path)
            logger.info(f"Successfully saved data for {ticker}")
            return True

        except Exception as e:
            logger.error(f"Failed to download data for {ticker}: {e}")
            return False

    def _load_single_ticker(
        self, ticker: str, auto_download: bool = True
    ) -> Optional[pd.Series]:
        """Safely load data for a single ticker with error handling.

        Returns:
            pd.Series or None if failed
        """
        file_path = self._get_file_path(ticker)

        if not file_path.exists():
            if auto_download:
                logger.info(f"Data for {ticker} not found locally, downloading...")
                if not self._download_single_ticker(ticker):
                    return None
            else:
                logger.warning(f"Data file for {ticker} not found at {file_path}")
                return None

        try:
            df = pd.read_parquet(file_path)
            # Convert DataFrame to Series (take first column if multiple)
            if isinstance(df, pd.DataFrame):
                return df.iloc[:, 0]  # Return first column as Series
            return df  # Already a Series
        except Exception as e:
            logger.error(f"Error reading data for {ticker}: {e}")
            return None

    def download_data(
        self, tickers: Optional[List[str]] = None, force_download: bool = False
    ) -> None:
        """Download data for specified tickers.

        Args:
            tickers: List of tickers to download. If None, uses all tickers.
            force_download: If True, download even if file exists.
        """
        if tickers is None:
            tickers = self.tickers

        for ticker in tickers:
            file_path = self._get_file_path(ticker)

            if file_path.exists() and not force_download:
                logger.info(f"Data for {ticker} already exists, skipping...")
                continue

            self._download_single_ticker(ticker)

    def load_data(
        self,
        tickers: Optional[List[str]] = None,
        auto_download: bool = False,
    ) -> pd.DataFrame:
        """Load data for multiple tickers into a single DataFrame.

        Args:
            tickers: List of tickers to load. If None, uses all tickers.
            auto_download: If True, download missing data automatically

        Returns:
            pd.DataFrame: Wide format with dates as index and tickers as columns
        """
        if tickers is None:
            tickers = self.tickers

        data = {}
        failed_tickers = []

        for ticker in tickers:
            ticker_data = self._load_single_ticker(ticker, auto_download)
            if ticker_data is not None:
                data[ticker] = ticker_data
            else:
                failed_tickers.append(ticker)

        if not data:
            raise ValueError("No data could be loaded for any tickers")

        if failed_tickers:
            logger.info(f"Failed to load data for: {failed_tickers}")

        # Combine all series into a single DataFrame with proper alignment
        df = pd.DataFrame(data)

        return df

    def get_data_info(self, ticker: Optional[str] = None) -> Union[Dict[str, int], int]:
        """Get information about loaded data.

        Args:
            ticker: Specific ticker to check. If None, checks all tickers.

        Returns:
            Dict of ticker -> length, or single length if ticker specified
        """
        if ticker is not None:
            ticker_data = self._load_single_ticker(ticker, auto_download=False)
            return len(ticker_data) if ticker_data is not None else 0

        info = {}
        for tick in self.tickers:
            ticker_data = self._load_single_ticker(tick, auto_download=False)
            info[tick] = len(ticker_data) if ticker_data is not None else 0

        return info

    def print_data_info(self, ticker: Optional[str] = None) -> None:
        """Print data information in a formatted way."""
        info = self.get_data_info(ticker)

        if ticker is not None:
            print(f"{ticker}: {info} rows")
        else:
            # info is a dict when ticker is None
            for tick, length in info.items():  # type: ignore
                status = "✓" if length > 0 else "✗"
                print(f"{status} {tick}: {length} rows")
