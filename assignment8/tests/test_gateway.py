import socket
import threading
import time
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.gateway import Gateway, NewsStream, PriceStream, Stream, TestStream

# ---------- FIXTURES ----------


@pytest.fixture
def test_symbols():
    return ["AAPL", "MSFT"]


@pytest.fixture
def mock_socket(monkeypatch):
    """Mock out socket.socket to prevent real networking."""
    mock = MagicMock()
    mock.accept.side_effect = BlockingIOError  # Simulate non-blocking
    mock.connect.return_value = None
    monkeypatch.setattr(socket, "socket", MagicMock(return_value=mock))
    return mock


# ---------- TESTS ----------


def test_gateway_initialization(test_symbols):
    """Ensure Gateway correctly builds its sub-streams."""
    gw = Gateway("localhost", 9000, 9001, 1.0, 1.0, test_symbols)
    assert isinstance(gw.price_stream, PriceStream)
    assert isinstance(gw.news_stream, NewsStream)
    assert gw.price_stream._port == 9000
    assert gw.news_stream._port == 9001
    assert gw.price_stream._interval == 1.0


def test_generate_message_basic():
    """Stream.generate_message should properly join and encode data."""
    s = TestStream("localhost", 9999, 0.1)
    data = ["AAPL,101", "MSFT,200"]
    encoded = s.generate_message(data)
    assert encoded == b"AAPL,101*MSFT,200*"


def test_price_stream_generate_data(monkeypatch, test_symbols):
    """Check that prices evolve and format is correct."""
    ps = PriceStream("localhost", 9999, 0.1, test_symbols)
    # Patch np.random.normal for deterministic result
    monkeypatch.setattr(np.random, "normal", lambda: 0.0)
    old_prices = ps._prices.copy()
    data = ps.generate_data()
    assert all(sym in d for sym, d in zip(test_symbols, data))
    for sym in test_symbols:
        assert ps._prices[sym] != old_prices[sym]
        assert isinstance(ps._prices[sym], float)
        assert data[0].count(",") == 1


def test_news_stream_generate_data(monkeypatch, test_symbols):
    """Ensure NewsStream generates integer sentiment values."""
    ns = NewsStream("localhost", 9998, 0.1, test_symbols)
    monkeypatch.setattr(np.random, "randint", lambda a, b: 50)
    result = ns.generate_data()
    assert all("," in msg for msg in result)
    assert all(msg.endswith("50") for msg in result)


def test_broadcast_sends_to_all(monkeypatch):
    """Ensure broadcast encodes and sends to all connected clients."""
    s = TestStream("localhost", 9997, 0.1)
    mock_client1 = MagicMock()
    mock_client2 = MagicMock()
    s._client_sockets = [mock_client1, mock_client2]
    s.broadcast(["Hello", "World"])
    msg = b"Hello*World*"
    mock_client1.sendall.assert_called_once_with(msg)
    mock_client2.sendall.assert_called_once_with(msg)


def test_broadcast_removes_dead_client(monkeypatch):
    """Clients that raise on sendall should be removed."""
    s = TestStream("localhost", 9996, 0.1)
    good_client = MagicMock()
    bad_client = MagicMock()
    bad_client.sendall.side_effect = OSError("socket dead")
    s._client_sockets = [good_client, bad_client]
    s.broadcast(["data"])
    assert good_client in s._client_sockets
    assert bad_client not in s._client_sockets


def test_cleanup_closes_resources(monkeypatch, mock_socket):
    """Ensure cleanup closes sockets and clears clients."""
    s = TestStream("localhost", 9995, 0.1)
    mock_client = MagicMock()
    s._client_sockets = [mock_client]
    s._running = True
    s._thread = threading.Thread(target=lambda: time.sleep(0.01))
    s._thread.start()
    s._cleanup()
    assert s._client_sockets == []
    assert not s._running
    mock_client.close.assert_called()
