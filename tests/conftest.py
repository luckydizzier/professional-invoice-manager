import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from professional_invoice_manager.db import init_database  # noqa: E402


@pytest.fixture(autouse=True)
def in_memory_db(monkeypatch):
    original_connect = sqlite3.connect
    root_conn = original_connect("file::memory:?cache=shared", uri=True)
    root_conn.row_factory = sqlite3.Row

    def connect(*args, **kwargs):
        conn = original_connect("file::memory:?cache=shared", uri=True)
        conn.row_factory = sqlite3.Row
        return conn

    monkeypatch.setattr(sqlite3, "connect", connect)
    init_database()
    yield
    root_conn.close()
