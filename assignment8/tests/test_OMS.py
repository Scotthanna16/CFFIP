import logging
import socket
from multiprocessing import Event
from unittest.mock import MagicMock, call, patch

import pytest

import src.order_manager as om  # adjust import path to match your project


@pytest.fixture
def mock_logger():
    with patch.object(om, "logger") as mock_logger:
        yield mock_logger


@pytest.fixture
def mock_socket():
    """Mock socket.socket to control recv() output."""
    with patch("socket.socket") as mock_socket_cls:
        mock_socket = MagicMock()
        mock_socket_cls.return_value.__enter__.return_value = mock_socket
        yield mock_socket


def make_order_bytes(*orders):
    """Helper: turn orders into properly delimited byte stream."""
    delimiter = om.DELIMITER
    joined = delimiter.join([o.encode("utf-8") for o in orders]) + delimiter
    return joined


def test_order_deserialization_and_logging(mock_socket, mock_logger):
    orders = ["BUY,10,AAPL,150.0", "SELL,5,MSFT,320.5", "BUY,1,GOOG,120.0"]
    data = make_order_bytes(*orders)
    mock_socket.recv.side_effect = [data, b""]

    omgr = om.OrderManager(host="127.0.0.1", port=9999)

    # Stop after one loop iteration
    def side_effect_gen():
        for val in [True, True, False]:
            yield val
        while True:
            yield False

    with patch("time.sleep", return_value=None):
        with patch.object(omgr, "running") as mock_running:
            mock_running.is_set.side_effect = side_effect_gen()
            omgr.run_ordermanager()

    mock_socket.connect.assert_called_once_with(("127.0.0.1", 9999))
    assert omgr.order_number == 3
