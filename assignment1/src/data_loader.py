import csv
from datetime import datetime
from src.models import MarketDataPoint


def load_market_data(file_path: str) -> list[MarketDataPoint]:
    data_points = []
    with open(file_path, "r") as file:
        reader = csv.DictReader(file, fieldnames=["timestamp", "symbol", "price"])
        next(reader)  # Skip header row
        for row in reader:
            timestamp = datetime.fromisoformat(row["timestamp"])
            symbol = row["symbol"]
            price = float(row["price"])
            data_point = MarketDataPoint(timestamp, symbol, price)
            data_points.append(data_point)

    return data_points
