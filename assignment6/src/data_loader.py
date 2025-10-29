# data_loader.py
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from src.models import MarketDataPoint
import csv


class YahooFinanceAdapter:

    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_data(self, symbol: str) -> MarketDataPoint:
        with open(self.file_path, "r") as f:
            data = json.load(f)
        if data["ticker"] != symbol:
            raise ValueError(f"Symbol {symbol} not found in Yahoo data")
        return MarketDataPoint(
            symbol=data["ticker"],
            price=float(data["last_price"]),
            timestamp=datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00")),
        )


class CSVAdapter:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_market_data(self) -> list[MarketDataPoint]:
        data_points = []
        with open(self.file_path, "r") as file:
            reader = csv.DictReader(file, fieldnames=["timestamp", "symbol", "price"])
            next(reader)  # Skip header row
            for row in reader:
                timestamp = datetime.fromisoformat(row["timestamp"])
                symbol = row["symbol"]
                price = float(row["price"])
                data_point = MarketDataPoint(timestamp, symbol, price)
                data_points.append(data_point)

        return data_points

    def get_data_prices(self, ticker) -> list[float]:
        data_prices = []
        with open(self.file_path, "r") as file:
            reader = csv.DictReader(file, fieldnames=["timestamp", "symbol", "price"])
            next(reader)  # Skip header row
            for row in reader:
                if row["symbol"] == ticker:

                    price = float(row["price"])

                    data_prices.append(price)

        return data_prices


class BloombergXMLAdapter:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_data(self, symbol: str) -> MarketDataPoint:
        tree = ET.parse(self.file_path)
        root = tree.getroot()

        xml_symbol = root.find("symbol")
        if xml_symbol is None or xml_symbol.text is None:
            raise ValueError("No symbol found in Bloomberg data")
        xml_symbol = xml_symbol.text
        if xml_symbol != symbol:
            raise ValueError(f"Symbol {symbol} not found in Bloomberg data")

        price = root.find("price")
        if price is None or price.text is None:
            raise ValueError("No price found in Bloomberg data")

        price = float(price.text)

        timestamp = root.find("timestamp")
        if timestamp is None or timestamp.text is None:
            raise ValueError("No timestamp found in Bloomberg data")
        timestamp = datetime.fromisoformat(timestamp.text.replace("Z", "+00:00"))

        return MarketDataPoint(symbol=xml_symbol, price=price, timestamp=timestamp)


if __name__ == "__main__":
    yahoo_adapter = YahooFinanceAdapter("data/external_data_yahoo.json")
    bloomberg_adapter = BloombergXMLAdapter("data/external_data_bloomberg.xml")
    csvadapter = CSVAdapter("data/market_data.csv")
    # data = csvadapter.get_data("AAPL")

    yahoo_point = yahoo_adapter.get_data("AAPL")
    bloomberg_point = bloomberg_adapter.get_data("MSFT")

    print("Yahoo Finance: ", yahoo_point)
    print("Bloomberg XML: ", bloomberg_point)
    # print(data)
