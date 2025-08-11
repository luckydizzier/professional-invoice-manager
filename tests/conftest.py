import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))
import main_with_management  # noqa: E402


@pytest.fixture(autouse=True)
def temporary_database(monkeypatch, tmp_path):
    db_path = tmp_path / "test.db"

    def _get_db():
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    monkeypatch.setattr(main_with_management, "get_db", _get_db)
    main_with_management.init_database()
    yield
