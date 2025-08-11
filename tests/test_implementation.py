import os
import sqlite3
import sys
from pathlib import Path
import time

import pytest
from PyQt5.QtWidgets import QApplication

sys.path.append(str(Path(__file__).resolve().parent.parent))

import main_with_management as mwm  # noqa: E402
from main_with_management import (  # noqa: E402
    InvoiceFormDialog,
    InvoiceListPage,
    MainWindow,
    PartnerFormDialog,
    PartnerListPage,
    ProductFormDialog,
    ProductListPage,
)


@pytest.fixture(scope="module")
def app():
    """Provide a shared QApplication instance."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture()
def isolated_db(tmp_path, monkeypatch):
    """Return a temporary database and patch ``mwm.get_db`` to use it.

    Each test receives its own SQLite file under ``tmp_path`` to keep
    database state isolated. This fixture is not safe for concurrent
    tests unless a fresh database is provided for each test run.
    """
    db_file = tmp_path / "test.db"

    def _get_db():
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        return conn

    monkeypatch.setattr(mwm, "get_db", _get_db)
    return db_file


def test_invoice_functionality(isolated_db):
    """Invoice table has required columns and supports inserts."""
    mwm.init_database()
    with mwm.get_db() as conn:
        cursor = conn.execute("PRAGMA table_info(invoice)")
        columns = [row[1] for row in cursor.fetchall()]
        for col in [
            "id",
            "number",
            "direction",
            "partner_id",
            "created_utc",
        ]:
            assert col in columns

        invoice_count = conn.execute(
            "SELECT COUNT(*) FROM invoice"
        ).fetchone()[0]
        assert invoice_count >= 0

        partner = conn.execute("SELECT id FROM partner LIMIT 1").fetchone()
        assert partner is not None

        test_number = f"TEST-{int(time.time())}"
        conn.execute(
            "INSERT INTO invoice (number, direction, partner_id, created_utc) "
            "VALUES (?, ?, ?, ?)",
            (test_number, "sale", partner["id"], int(time.time())),
        )
        conn.commit()
        inserted = conn.execute(
            "SELECT COUNT(*) FROM invoice WHERE number = ?",
            (test_number,),
        ).fetchone()[0]
        assert inserted == 1
        conn.execute("DELETE FROM invoice WHERE number = ?", (test_number,))
        conn.commit()


def test_all_dialog_classes(app):
    """Dialog classes can be instantiated."""
    assert InvoiceFormDialog() is not None
    assert ProductFormDialog() is not None
    assert PartnerFormDialog() is not None


def test_main_window_functionality(app):
    """MainWindow exposes required methods."""
    window = MainWindow()
    required_methods = [
        "new_invoice",
        "new_product",
        "new_customer",
        "new_supplier",
        "show_list",
        "show_products",
        "show_customers",
        "show_suppliers",
    ]
    for name in required_methods:
        assert hasattr(window, name)


def test_management_pages(app):
    """Management pages instantiate without errors."""
    assert ProductListPage() is not None
    assert PartnerListPage("customer") is not None
    assert PartnerListPage("supplier") is not None
    assert InvoiceListPage() is not None
