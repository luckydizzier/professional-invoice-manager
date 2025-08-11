#!/usr/bin/env python3
"""Tests for product and partner management features."""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt5.QtWidgets import QApplication  # noqa: E402
from main_with_management import (  # noqa: E402
    get_db,
    init_database,
    MainWindow,
)
from professional_invoice_manager.dialogs import (  # noqa: E402
    PartnerFormDialog,
    ProductFormDialog,
)


def test_management_features():
    """Ensure management components load and database is accessible."""
    init_database()
    _ = QApplication.instance() or QApplication(sys.argv)

    with get_db() as conn:
        product_count = conn.execute(
            "SELECT COUNT(*) FROM product"
        ).fetchone()[0]
        customer_count = conn.execute(
            "SELECT COUNT(*) FROM partner WHERE kind='customer'"
        ).fetchone()[0]
        supplier_count = conn.execute(
            "SELECT COUNT(*) FROM partner WHERE kind='supplier'"
        ).fetchone()[0]

    assert product_count >= 0
    assert customer_count >= 0
    assert supplier_count >= 0

    assert ProductFormDialog() is not None
    assert PartnerFormDialog() is not None
    assert MainWindow() is not None
