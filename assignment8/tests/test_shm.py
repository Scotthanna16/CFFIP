from multiprocessing import Lock, Process, shared_memory

import numpy as np
import pytest

from src.shared_memory_utils import DTYPE, SharedPriceBook


@pytest.fixture
def symbols():
    return ["AAPL", "MSFT"]


@pytest.fixture
def lock():
    return Lock()


# ---------- BASIC CREATION ----------


def test_init_creates_shared_memory(symbols, lock):
    """Newly created SharedPriceBook should initialize with NaN prices."""
    book = SharedPriceBook(symbols, lock)
    assert book.num_symbols == len(symbols)
    assert all(sym.encode("utf-8") in book.array["symbol"] for sym in symbols)
    assert np.all(np.isnan(book.array["price"]))
    assert hasattr(book, "_creator") and book._creator is True
    book.close()


# ---------- UPDATE & READ ----------


def test_update_and_read(symbols, lock):
    """Prices should update and read correctly."""
    book = SharedPriceBook(symbols, lock)
    book.update("AAPL", 123.45)
    price = book.read("AAPL")
    assert price == pytest.approx(123.45, rel=1e-6)

    # Unknown symbol returns None
    assert book.read("GOOG") is None
    book.close()


# ---------- ATTACH TO EXISTING SHM ----------


def test_attach_existing_shared_memory(symbols, lock):
    """Attaching to an existing memory name should reflect updates."""
    # Creator
    book1 = SharedPriceBook(symbols, lock)
    name = book1.name

    # Attach second instance
    book2 = SharedPriceBook(symbols, lock, name=name)

    book1.update("MSFT", 200.0)
    assert book2.read("MSFT") == pytest.approx(200.0)

    # Cleanup both
    book2.close()
    book1.close()


# ---------- CONCURRENCY SAFETY ----------


def test_update_with_lock(symbols):
    """Ensure Lock properly synchronizes access."""
    lock = Lock()
    book = SharedPriceBook(symbols, lock)

    # Simulate two sequential updates under same lock
    book.update("AAPL", 100.0)
    book.update("AAPL", 150.0)
    assert book.read("AAPL") == pytest.approx(150.0)

    book.close()


# ---------- CLEANUP ----------


def test_close_unlinks_shared_memory(symbols, lock):
    """After close, shared memory should be unlinked and closed."""
    book = SharedPriceBook(symbols, lock)
    name = book.name
    book.close()

    # Attempt to attach should fail because it's unlinked
    with pytest.raises(FileNotFoundError):
        shared_memory.SharedMemory(name=name)


# ---------- EDGE CASES ----------


def test_update_unknown_symbol_logs_warning(symbols, lock, caplog):
    """Updating unknown symbol logs a warning but doesn’t raise."""
    book = SharedPriceBook(symbols, lock)
    with caplog.at_level("WARNING"):
        book.update("FAKE", 999.9)
    assert "not found in price book" in caplog.text
    book.close()


def test_read_unknown_symbol_returns_none(symbols, lock):
    """Reading symbol not present should return None."""
    book = SharedPriceBook(symbols, lock)
    assert book.read("FAKE") is None
    book.close()


def _child_process(name, symbols, price):
    """Child process attaches to shared memory and writes a value."""
    lock = Lock()  # independent Lock (won’t deadlock)
    book = SharedPriceBook(symbols, lock, name=name)
    book.update("MSFT", price)
    book.close()


def test_shared_memory_across_processes(symbols, lock):
    """
    Ensure that changes made in a separate process are visible
    in the parent process through shared memory.
    """
    book_parent = SharedPriceBook(symbols, lock)
    name = book_parent.name

    # Spawn a child process to modify the shared memory
    p = Process(target=_child_process, args=(name, symbols, 250.5))
    p.start()
    p.join(timeout=5)
    assert p.exitcode == 0

    # Parent should see updated value
    updated_value = book_parent.read("MSFT")
    assert updated_value == pytest.approx(250.5, rel=1e-6)

    book_parent.close()
