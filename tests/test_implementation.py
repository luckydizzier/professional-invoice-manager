import logging
import os
from pathlib import Path
import sqlite3
import sys
import time

from PyQt5.QtWidgets import QApplication
import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))

from main_with_management import (  # noqa: E402
    get_db,
    init_database,
    MainWindow,
)
import professional_invoice_manager.dialogs as dialogs  # noqa: E402
from professional_invoice_manager.dialogs import (  # noqa: E402
    InvoiceFormDialog,
    PartnerFormDialog,
    ProductFormDialog,
)
from professional_invoice_manager.pages import (  # noqa: E402
    InvoiceListPage,
    PartnerListPage,
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


def test_invoice_functionality():
    """Invoice table has required columns and supports inserts."""
    init_database()
    with get_db() as conn:
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


def test_load_partners_db_error(monkeypatch, caplog, app):
    def raise_error():
        raise sqlite3.Error("boom")

    warned = {}

    def fake_warning(*args, **kwargs):
        warned["called"] = True

    monkeypatch.setattr(dialogs, "get_db", raise_error)
    monkeypatch.setattr(
        dialogs.QMessageBox, "warning", staticmethod(fake_warning)
    )
    with caplog.at_level(logging.ERROR):
        dialog = InvoiceFormDialog()
    assert dialog.partner_combo.count() == 0
    assert warned.get("called")
    assert any(
        "Failed to load partners" in record.message
        for record in caplog.records
    )
