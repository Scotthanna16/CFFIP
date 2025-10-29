from ..models import Instrument, Stock, ETF, Bond
from datetime import datetime
from ..data_loader import CSVAdapter
import csv


# patterns/factory.py
"""
Factory Pattern
- Problem: Instantiate different instrument types (Stock, Bond, ETF) from raw data.
- Expectations:
    - Implement InstrumentFactory.create_instrument(data: dict) -> Instrument.
    - Support at least three instrument types with appropriate attributes.
    - Demonstrate instantiation from instruments.csv.
"""


class InstrumentFactory:

    @staticmethod
    def create_instrument(data: dict) -> Instrument:

        # common fields
        try:
            instr_type = data["type"].strip().lower()
            symbol = data["symbol"]
            price = data["price"]
            sector = data["sector"]
            issuer = data["issuer"]
        except KeyError as e:
            raise ValueError(f"Missing required instrument field: {e}")

        if instr_type == "stock":
            return Stock(symbol, price, sector, issuer)

        elif instr_type == "bond":
            try:
                maturity = data["maturity"]
                return Bond(symbol, price, sector, issuer, maturity)
            except KeyError:
                raise ValueError("Missing maturity field for Bond instrument")
            except Exception as e:
                raise ValueError(f"Error creating Bond instrument: {e}")

        elif instr_type == "etf":
            try:
                return ETF(symbol, price, sector, issuer)
            except Exception as e:
                raise ValueError(f"Error creating ETF instrument: {e}")

        else:
            raise ValueError(f"Unknown instrument type: {data['type']}")


def load_instruments_from_csv(path: str):
    instruments = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            instrument = InstrumentFactory.create_instrument(row)
            instruments.append(instrument)
    return instruments
