"""Tests for VAT summary calculations and widget."""

from collections import defaultdict
import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402
from main_with_management import (  # noqa: E402
    InvoiceDetailWidget,
    get_db,
    init_database,
)


def _compute_vat_breakdown(items):
    breakdown = defaultdict(lambda: {"net": 0.0, "vat": 0.0, "gross": 0.0})
    for item in items:
        quantity = item["qty"]
        unit_price = item["unit_price_cents"] / 100.0
        rate = item["vat_rate"]
        line_net = quantity * unit_price
        line_vat = line_net * rate / 100.0
        breakdown[rate]["net"] += line_net
        breakdown[rate]["vat"] += line_vat
        breakdown[rate]["gross"] += line_net + line_vat
    return dict(breakdown)


def test_vat_summary():
    init_database()

    items = [
        {"qty": 2, "unit_price_cents": 100000, "vat_rate": 27},
        {"qty": 1, "unit_price_cents": 50000, "vat_rate": 18},
        {"qty": 3, "unit_price_cents": 200000, "vat_rate": 27},
        {"qty": 1, "unit_price_cents": 75000, "vat_rate": 5},
    ]
    breakdown = _compute_vat_breakdown(items)
    expected = {
        27: {"net": 8000.0, "vat": 2160.0, "gross": 10160.0},
        18: {"net": 500.0, "vat": 90.0, "gross": 590.0},
        5: {"net": 750.0, "vat": 37.5, "gross": 787.5},
    }
    assert breakdown == expected

    assert hasattr(InvoiceDetailWidget, "update_vat_summary")


def test_database_vat_data():
    with get_db() as conn:
        invoice = conn.execute(
            """
            SELECT i.id, COUNT(ii.id) AS item_count
            FROM invoice i
            LEFT JOIN invoice_item ii ON i.id = ii.invoice_id
            GROUP BY i.id
            HAVING item_count > 0
            LIMIT 1
            """
        ).fetchone()
        if not invoice:
            pytest.skip("No invoices with items found")

        items = conn.execute(
            """
            SELECT ii.qty, ii.unit_price_cents, ii.vat_rate
            FROM invoice_item ii
            WHERE ii.invoice_id = ?
            """,
            (invoice["id"],),
        ).fetchall()

    breakdown = _compute_vat_breakdown(items)
    assert breakdown
    assert all(data["gross"] > 0 for data in breakdown.values())
