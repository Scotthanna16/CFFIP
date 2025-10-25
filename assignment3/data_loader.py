import csv
from datetime import datetime
from models import MarketDataPoint

"""
Runtime Complexity of O(n) because reading the CSV is linear in the number of rows, and append is amortized O(1).

Space Complexity of O(n) where n is the number of data points.
"""


def load_market_data(
    file_path: str = "assignment3_market_data.csv",
) -> list[MarketDataPoint]:
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


def load_market_data_generator(
    file_path: str = "assignment3_market_data.csv",
):
    with open(file_path, "r") as file:
        reader = csv.DictReader(file, fieldnames=["timestamp", "symbol", "price"])
        next(reader)  # Skip header row
        for row in reader:
            timestamp = datetime.fromisoformat(row["timestamp"])
            symbol = row["symbol"]
            price = float(row["price"])
            data_point = MarketDataPoint(timestamp, symbol, price)
            yield data_point


# print(load_market_data())
