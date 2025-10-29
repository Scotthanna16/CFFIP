# patterns/observer.py
"""
Observer Pattern
- Problem: Notify external modules when signals are generated.
- Expectations:
    - Implement SignalPublisher with .attach(observer) and .notify(signal).
    - Define Observer.update(signal: dict).
    - Implement:
        - LoggerObserver: logs signals
        - AlertObserver: alerts on large trades
    - Demonstrate dynamic observer registration and notification.
"""
from abc import ABC, abstractmethod
import logging


class Observer(ABC):
    @abstractmethod
    def update(self, signal: dict):
        pass


class SignalPublisher:
    def __init__(self):
        self._observers = []

    def attach(self, observer: Observer):
        self._observers.append(observer)

    def detach(self, observer: Observer):
        self._observers.remove(observer)

    def notify(self, signal: dict):
        for observer in self._observers:
            observer.update(signal)


class LoggerObserver(Observer):

    def __init__(self, log_level: int = logging.INFO):
        self.log_level = log_level

    def update(self, signal: dict):
        logging.log(self.log_level, f"Received signal: {signal}")


class AlertObserver(Observer):

    def __init__(self, threshold: float, log_level: int = logging.WARNING):
        self.threshold = threshold
        self._alert_level = log_level

    def update(self, signal: dict):
        if signal.get("price", 0) * signal.get("quantity", 0) >= self.threshold:
            logging.log(
                self._alert_level, f"ALERT: Significant signal received: {signal}"
            )
