# patterns/singleton.py
"""
Singleton Pattern

- Problem: Centralize system configuration (e.g., logging level, strategy parameters).
- Expectations:
    - Implement a Singleton Config class.
    - Load settings from config.json.
    - Ensure all modules access the same instance.
"""

import json
import os
from threading import Lock

# logging level enum
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL


class Config:
    _instance = None
    _lock = Lock()

    def __new__(cls, config_file="jsons/config.json"):
        # Ensure only one instance is created
        if not cls._instance:
            with cls._lock:
                if not cls._instance:  # Double-checked locking
                    cls._instance = super(Config, cls).__new__(cls)
                    cls._instance._load(config_file)
        return cls._instance

    def _load(self, config_file):

        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found")

        with open(config_file, "r") as f:
            data = json.load(f)

        self.log_level = data.get("log_level", "INFO")
        # map string log level to logging module constants
        self.log_level = {
            "DEBUG": DEBUG,
            "INFO": INFO,
            "WARNING": WARNING,
            "ERROR": ERROR,
            "CRITICAL": CRITICAL,
        }.get(self.log_level.upper(), INFO)
        self.data_path = data.get("data_path", "./data/")
        self.report_path = data.get("report_path", "./reports/")
        self.default_strategy = data.get("default_strategy", "MeanReversionStrategy")

    def __repr__(self):
        return (
            f"Config(log_level={self.log_level}, data_path={self.data_path}, "
            f"report_path={self.report_path}, default_strategy={self.default_strategy})"
        )


if __name__ == "__main__":
    cfg1 = Config()
    cfg2 = Config()

    print(cfg1 is cfg2)
    print(cfg1.log_level)
