#!/usr/bin/env python3
"""Quick test to verify VAT summary works with the main application."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt5.QtWidgets import QApplication  # noqa: E402
from main_with_management import MainWindow, init_database  # noqa: E402


def test_application_launch_with_vat_summary():
    """Application launches and exposes VAT summary components."""
    init_database()

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    main_window = MainWindow()
    page = main_window.invoice_list_page

    # Simulate the original object hierarchy
    class Window:
        pass
    window = Window()
    window.invoice_page = page

    detail_widget = window.invoice_page.detail_widget
    assert hasattr(detail_widget, "vat_table")
    assert detail_widget.vat_table.columnCount() > 0
    assert hasattr(detail_widget, "update_vat_summary")
