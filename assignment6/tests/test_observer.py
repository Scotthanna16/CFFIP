from src.patterns.observer import SignalPublisher, AlertObserver, LoggerObserver
import io
import sys
import logging
import pytest


def test_signal_publisher_notification():
    publisher = SignalPublisher()
    alert_observer = AlertObserver(threshold=100)
    logger_observer = LoggerObserver(log_level=logging.INFO)
    out = []

    alert_observer.update = lambda signal: out.append(f"ALERT: {signal}")
    logger_observer.update = lambda signal: out.append(f"LOG: {signal}")

    publisher.attach(alert_observer)
    publisher.attach(logger_observer)

    test_signal = {"symbol": "AAPL", "price": 5000, "action": "BUY", "quantity": 100}

    publisher.notify(test_signal)

    assert (
        "ALERT: {'symbol': 'AAPL', 'price': 5000, 'action': 'BUY', 'quantity': 100}"
        in out
    )
    assert (
        "LOG: {'symbol': 'AAPL', 'price': 5000, 'action': 'BUY', 'quantity': 100}"
        in out
    )
