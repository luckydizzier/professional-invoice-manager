# Qt5 (PyQt5) GUI számlakezelő – billentyű-only (Enter/Esc/Ins/Del/←→↑↓)
# Egyszerű, egyfájlos demó: SQLite + Repo/Service réteg + Qt5 UI oldalak
# Funkciók: számlalistázás, új számla varázsló (irány + partner), tételek, ÁFA bontás, mentés

import sys
import sqlite3
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple

import os
if not os.path.exists("invoice_qt5.db"):
    with open("invoice_qt5.db", "w") as f:
        pass  # create empty file if it doesn't exist

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QPushButton,
    QHeaderView
)

DB_PATH = "invoice_qt5.db"

# -------------------- UTILITIES --------------------

def format_date(timestamp: int) -> str:
    """Convert UTC timestamp to formatted date string"""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")

# -------------------- DB + MIGRÁCIÓ --------------------

def init_db(conn: sqlite3.Connection) -> None:
    c = conn
    c.execute("PRAGMA foreign_keys=ON;")
    c.execute("PRAGMA journal_mode=WAL;")
    c.execute("PRAGMA synchronous=NORMAL;")
    c.executescript(
        """
        CREATE TABLE IF NOT EXISTS partner (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            kind TEXT NOT NULL CHECK(kind IN ('customer','supplier')),
            tax_id TEXT,
            address TEXT
        );
        CREATE TABLE IF NOT EXISTS product (
            id INTEGER PRIMARY KEY,
            sku TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            unit_price_cents INTEGER NOT NULL,
            vat_rate INTEGER NOT NULL DEFAULT 27
        );
        CREATE TABLE IF NOT EXISTS invoice (
            id INTEGER PRIMARY KEY,
            number TEXT NOT NULL UNIQUE,
            partner_id INTEGER NOT NULL REFERENCES partner(id),
            direction TEXT NOT NULL CHECK(direction IN ('sale','purchase')),
            created_utc INTEGER NOT NULL,
            notes TEXT
        );
        CREATE TABLE IF NOT EXISTS invoice_item (
            id INTEGER PRIMARY KEY,
            invoice_id INTEGER NOT NULL REFERENCES invoice(id) ON DELETE CASCADE,
            product_id INTEGER NOT NULL REFERENCES product(id),
            qty INTEGER NOT NULL,
            unit_price_cents INTEGER NOT NULL,
            vat_rate INTEGER NOT NULL
        );
        """
    )
    seed_data(c)
    conn.commit()


def seed_data(c: sqlite3.Connection) -> None:
    if c.execute("SELECT COUNT(*) FROM product").fetchone()[0] == 0:
        products = [
            ("SKU001", "Kenyér 1kg", 69900, 5),
            ("SKU002", "Tej 1l", 39900, 18),
            ("SKU003", "Kolbász 1kg", 299900, 27),
            ("SKU004", "Kakaóscsiga", 34900, 27),
            ("SKU005", "Rostos üdítő 1l", 59900, 27),
        ]
        c.executemany(
            "INSERT INTO product(sku,name,unit_price_cents,vat_rate) VALUES(?,?,?,?)",
            products,
        )
    if c.execute("SELECT COUNT(*) FROM partner").fetchone()[0] == 0:
        partners = [
            ("Lakossági Vevő", "customer", None, None),
            ("Teszt Kft.", "customer", "12345678-1-42", "1111 Bp, Fő u. 1."),
            ("Minta Beszállító Zrt.", "supplier", "87654321-2-13", "7626 Pécs, Utca 2."),
        ]
        c.executemany(
            "INSERT INTO partner(name,kind,tax_id,address) VALUES(?,?,?,?)",
            partners,
        )

# -------------------- REPO --------------------

class Repo:
    def __init__(self, conn: sqlite3.Connection):
        self.c = conn

    # partner
    def list_partners(self, kind: Optional[str] = None) -> List[Dict]:
        if kind:
            cur = self.c.execute("SELECT id,name,kind,tax_id,address FROM partner WHERE kind=? ORDER BY id ASC", (kind,))
        else:
            cur = self.c.execute("SELECT id,name,kind,tax_id,address FROM partner ORDER BY id ASC")
        return [{"id":r[0],"name":r[1],"kind":r[2],"tax_id":r[3],"address":r[4]} for r in cur]

    def add_partner(self, name: str, kind: str) -> int:
        cur = self.c.execute("INSERT INTO partner(name,kind) VALUES(?,?)", (name, kind))
        return cur.lastrowid

    # product
    def list_products(self) -> List[Dict]:
        cur = self.c.execute("SELECT id,sku,name,unit_price_cents,vat_rate FROM product ORDER BY id ASC")
        return [{"id":r[0],"sku":r[1],"name":r[2],"unit":r[3],"vat":r[4]} for r in cur]

    # invoice
    def list_invoices(self) -> List[Dict]:
        cur = self.c.execute(
            "SELECT i.id,i.number,p.name,i.direction,i.created_utc FROM invoice i JOIN partner p ON p.id=i.partner_id ORDER BY i.created_utc DESC"
        )
        return [{"id":r[0],"number":r[1],"partner":r[2],"direction":r[3],"created":r[4]} for r in cur]

    def create_invoice(self, number: str, partner_id: int, direction: str) -> int:
        cur = self.c.execute(
            "INSERT INTO invoice(number,partner_id,direction,created_utc,notes) VALUES(?,?,?,?,?)",
            (number, partner_id, direction, int(time.time()), ""),
        )
        return cur.lastrowid

    def delete_invoice(self, inv_id: int) -> None:
        self.c.execute("DELETE FROM invoice WHERE id=?", (inv_id,))

    # items
    def list_items(self, inv_id: int) -> List[Dict]:
        cur = self.c.execute(
            "SELECT ii.id,p.sku,p.name,ii.qty,ii.unit_price_cents,ii.vat_rate FROM invoice_item ii JOIN product p ON p.id=ii.product_id WHERE ii.invoice_id=? ORDER BY ii.id ASC",
            (inv_id,),
        )
        return [{"id":r[0],"sku":r[1],"name":r[2],"qty":r[3],"unit":r[4],"vat":r[5]} for r in cur]

    def add_item(self, inv_id: int, product_id: int, qty: int) -> None:
        p = self.c.execute("SELECT unit_price_cents,vat_rate FROM product WHERE id=?", (product_id,)).fetchone()
        if not p: raise ValueError("product not found")
        self.c.execute(
            "INSERT INTO invoice_item(invoice_id,product_id,qty,unit_price_cents,vat_rate) VALUES(?,?,?,?,?)",
            (inv_id, product_id, qty, p[0], p[1]),
        )

    def set_item_qty(self, item_id: int, qty: int) -> None:
        self.c.execute("UPDATE invoice_item SET qty=? WHERE id=?", (qty, item_id))

    def delete_item(self, item_id: int) -> None:
        self.c.execute("DELETE FROM invoice_item WHERE id=?", (item_id,))

# -------------------- SERVICE --------------------

class Service:
    def __init__(self, repo: Repo):
        self.r = repo

    def totals(self, inv_id: int) -> Dict:
        lines = self.r.list_items(inv_id)
        per_rate: Dict[int, Dict[str,int]] = {}
        net = 0
        for it in lines:
            ln = it["qty"] * it["unit"]
            net += ln
            per_rate.setdefault(it["vat"], {"base":0,"vat":0})["base"] += ln
        vat_total = 0
        for rate,d in per_rate.items():
            v = int(round(d["base"]*rate/100))
            d["vat"] = v
            vat_total += v
        return {"net":net, "vat":vat_total, "gross":net+vat_total, "rates":per_rate}

# -------------------- DIALOGOK --------------------

class ConfirmDialog(QDialog):
    def __init__(self, text: str, title: str = "Megerősítés", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
            }
            QLabel {
                color: #212529;
                font-size: 14px;
                font-weight: 500;
                padding: 10px;
                background-color: transparent;
            }
            QLabel#message {
                font-size: 16px;
                color: #495057;
                margin-bottom: 10px;
            }
            QLabel#instructions {
                font-size: 12px;
                color: #6c757d;
                font-style: italic;
                border-top: 1px solid #e9ecef;
                padding-top: 10px;
                margin-top: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Icon and message container
        message_container = QHBoxLayout()
        
        # Warning icon (using Unicode symbol)
        icon_label = QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 24px; margin-right: 10px;")
        icon_label.setAlignment(Qt.AlignTop)
        message_container.addWidget(icon_label)
        
        # Message text
        message_label = QLabel(text)
        message_label.setObjectName("message")
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        message_container.addWidget(message_label, 1)
        
        layout.addLayout(message_container)
        
        # Instructions
        instructions = QLabel("Enter = Igen (Yes)    •    Esc = Nem (No)")
        instructions.setObjectName("instructions")
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)
        
        self.setMinimumSize(350, 150)
        self.resize(420, 180)

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.accept()
        elif e.key() == Qt.Key_Escape:
            self.reject()
        elif e.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            # ignore navigation in confirm
            e.ignore()
        else:
            e.ignore()

class ListSelectDialog(QDialog):
    """Professional list selection dialog with modern styling and clear UX."""
    def __init__(self, title: str, headers: List[str], rows: List[Dict], fmt_row, on_new=None, on_delete=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.rows = rows
        self.fmt_row = fmt_row
        self.on_new = on_new
        self.on_delete = on_delete
        
        # Modern styling
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 8px;
            }
            QLabel {
                color: #374151;
                font-size: 14px;
                font-weight: 500;
                background-color: transparent;
            }
            QLabel#title {
                font-size: 18px;
                font-weight: 600;
                color: #111827;
                margin-bottom: 10px;
            }
            QLabel#instructions {
                font-size: 12px;
                color: #6b7280;
                background-color: #f9fafb;
                padding: 12px;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                margin-bottom: 15px;
            }
            QTableWidget {
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                background-color: #ffffff;
                gridline-color: #f3f4f6;
                selection-background-color: #dbeafe;
                selection-color: #1e40af;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #f3f4f6;
            }
            QTableWidget::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #374151;
                font-weight: 600;
                font-size: 12px;
                padding: 10px 12px;
                border: none;
                border-bottom: 2px solid #e5e7eb;
                border-right: 1px solid #e5e7eb;
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title_label = QLabel(title)
        title_label.setObjectName("title")
        layout.addWidget(title_label)
        
        # Instructions with better formatting
        instructions_text = self._build_instructions_text()
        instructions = QLabel(instructions_text)
        instructions.setObjectName("instructions")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Table
        self.table = QTableWidget(0, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        self.setMinimumSize(600, 400)
        self.resize(800, 500)
        self.populate()

    def _build_instructions_text(self) -> str:
        """Build instruction text based on available actions."""
        instructions = ["Enter = Kiválasztás", "Esc = Mégse", "↑↓ = Navigáció"]
        
        if self.on_new:
            instructions.append("Insert = Új elem")
        if self.on_delete:
            instructions.append("Delete = Törlés")
            
        return "  •  ".join(instructions)

    def populate(self):
        self.table.setRowCount(0)
        for r in self.rows:
            cols = self.fmt_row(r)
            row = self.table.rowCount(); self.table.insertRow(row)
            for c, text in enumerate(cols):
                it = QTableWidgetItem(text)
                it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row, c, it)
        if self.rows:
            self.table.selectRow(0)

    def current_index(self) -> int:
        sels = self.table.selectionModel().selectedRows()
        return sels[0].row() if sels else -1

    def keyPressEvent(self, e):
        key = e.key()
        if key in (Qt.Key_Return, Qt.Key_Enter):
            self.accept()
        elif key == Qt.Key_Escape:
            self.reject()
        elif key == Qt.Key_Insert and self.on_new:
            new_rows = self.on_new()
            if new_rows is not None:
                self.rows = new_rows
                self.populate()
                self.table.selectRow(max(0, self.table.rowCount()-1))
        elif key == Qt.Key_Delete and self.on_delete:
            idx = self.current_index()
            if 0 <= idx < len(self.rows):
                r = self.rows[idx]
                cdlg = ConfirmDialog("Biztosan törölni szeretnéd ezt az elemet?", "Elem Törlése")
                if cdlg.exec_() == QDialog.Accepted:
                    new_rows = self.on_delete(r)
                    if new_rows is not None:
                        self.rows = new_rows
                        self.populate()
                        self.table.selectRow(min(idx, max(0, self.table.rowCount()-1)))
        elif key in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right):
            super().keyPressEvent(e)
        else:
            e.ignore()

# -------------------- OLDALAK --------------------

class InvoiceListPage(QWidget):
    def __init__(self, repo: Repo, parent=None):
        super().__init__(parent)
        self.repo = repo
        
        # Professional styling
        self.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
                font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
            }
            QLabel {
                color: #374151;
                font-size: 14px;
                background-color: transparent;
            }
            QLabel#header {
                font-size: 24px;
                font-weight: 600;
                color: #111827;
                margin-bottom: 8px;
            }
            QLabel#instructions {
                font-size: 13px;
                color: #6b7280;
                background-color: #ffffff;
                padding: 12px 16px;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                margin-bottom: 16px;
            }
            QTableWidget {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background-color: #ffffff;
                gridline-color: #f3f4f6;
                selection-background-color: #dbeafe;
                selection-color: #1e40af;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 12px 16px;
                border-bottom: 1px solid #f3f4f6;
            }
            QTableWidget::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
                font-weight: 500;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #374151;
                font-weight: 600;
                font-size: 13px;
                padding: 12px 16px;
                border: none;
                border-bottom: 2px solid #e5e7eb;
                border-right: 1px solid #e5e7eb;
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header = QLabel("📄 Számlák")
        header.setObjectName("header")
        layout.addWidget(header)
        
        # Instructions with better formatting
        instructions = QLabel("Insert = Új számla  •  Delete = Törlés  •  Enter = Megnyitás  •  Esc = Kilépés")
        instructions.setObjectName("instructions")
        layout.addWidget(instructions)
        
        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["📅 Dátum", "📋 Számlaszám", "👤 Partner", "📊 Irány"]) 
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        self.refresh()

    def refresh(self):
        rows = self.repo.list_invoices()
        self.table.setRowCount(0)
        for inv in rows:
            row = self.table.rowCount(); self.table.insertRow(row)
            vals = [
                format_date(inv['created']), 
                inv['number'], 
                inv['partner'], 
                'ELADÁS' if inv['direction']=='sale' else 'VÉTEL'
            ]
            for c, text in enumerate(vals):
                it = QTableWidgetItem(text)
                it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row, c, it)
        if rows:
            self.table.selectRow(0)

    def selected_invoice_id(self) -> Optional[int]:
        idxs = self.table.selectionModel().selectedRows()
        if not idxs:
            return None
        row = idxs[0].row()
        invs = self.repo.list_invoices()
        if 0 <= row < len(invs):
            return invs[row]['id']
        return None

    def keyPressEvent(self, e):
        self.parent().keyPressEvent(e)  # delegate to MainWindow for handling

class DirectionPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.direction = 'sale'  # sale/purchase
        
        # Professional styling
        self.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
                font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
            }
            QLabel {
                color: #374151;
                background-color: transparent;
            }
            QLabel#header {
                font-size: 28px;
                font-weight: 600;
                color: #111827;
                margin-bottom: 16px;
                text-align: center;
            }
            QLabel#instructions {
                font-size: 16px;
                color: #6b7280;
                background-color: #ffffff;
                padding: 20px 24px;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                margin: 20px 0;
                text-align: center;
            }
            QLabel#current {
                font-size: 18px;
                font-weight: 500;
                color: #059669;
                background-color: #d1fae5;
                padding: 16px 20px;
                border: 2px solid #a7f3d0;
                border-radius: 8px;
                margin: 20px 0;
                text-align: center;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setAlignment(Qt.AlignCenter)
        
        # Header
        header = QLabel("🔄 Számla Típusa")
        header.setObjectName("header")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Instructions
        instructions = QLabel("← Szállítói számla  •  → Vevői számla  •  Enter = Tovább  •  Esc = Mégse")
        instructions.setObjectName("instructions")
        layout.addWidget(instructions)
        
        # Current selection display
        self.state = QLabel("📊 Aktuális: Vevői számla (Eladás)")
        self.state.setObjectName("current")
        layout.addWidget(self.state)
        
        # Add some spacing at the bottom
        layout.addStretch()

    def keyPressEvent(self, e):
        mw: MainWindow = self.parent().parent()
        if e.key() == Qt.Key_Left:
            self.direction = 'purchase'
            self.state.setText("📈 Aktuális: Szállítói számla (Beszerzés)")
        elif e.key() == Qt.Key_Right:
            self.direction = 'sale'
            self.state.setText("📊 Aktuális: Vevői számla (Eladás)")
        elif e.key() in (Qt.Key_Return, Qt.Key_Enter):
            mw.direction_chosen(self.direction)
        elif e.key() == Qt.Key_Escape:
            mw.cancel_new_invoice()
        else:
            e.ignore()

class ItemsPage(QWidget):
    def __init__(self, repo: Repo, service: Service, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.service = service
        self.inv_id: Optional[int] = None
        self.cursor = 0
        
        # Professional styling
        self.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
                font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
            }
            QLabel {
                color: #374151;
                background-color: transparent;
            }
            QLabel#header {
                font-size: 24px;
                font-weight: 600;
                color: #111827;
                margin-bottom: 8px;
            }
            QLabel#instructions {
                font-size: 13px;
                color: #6b7280;
                background-color: #ffffff;
                padding: 12px 16px;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                margin-bottom: 16px;
            }
            QLabel#totals {
                font-size: 16px;
                font-weight: 600;
                color: #059669;
                background-color: #d1fae5;
                padding: 16px 20px;
                border: 2px solid #a7f3d0;
                border-radius: 8px;
                margin-top: 16px;
                text-align: center;
            }
            QTableWidget {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background-color: #ffffff;
                gridline-color: #f3f4f6;
                selection-background-color: #dbeafe;
                selection-color: #1e40af;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 12px 16px;
                border-bottom: 1px solid #f3f4f6;
            }
            QTableWidget::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
                font-weight: 500;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #374151;
                font-weight: 600;
                font-size: 13px;
                padding: 12px 16px;
                border: none;
                border-bottom: 2px solid #e5e7eb;
                border-right: 1px solid #e5e7eb;
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header = QLabel("🛒 Számla Tételek")
        header.setObjectName("header")
        layout.addWidget(header)
        
        # Instructions
        instructions = QLabel("Insert = Új tétel  •  Delete = Törlés  •  ←/→/Enter = Mennyiség -/+1/+1  •  Esc = Tovább")
        instructions.setObjectName("instructions")
        layout.addWidget(instructions)
        
        # Table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["🏷️ SKU","📦 Megnevezés","📊 Menny.","💰 Egysár","📈 ÁFA%","💵 Nettó"]) 
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        # Totals
        self.totals = QLabel("💰 Összesen: Nettó 0 Ft  •  ÁFA 0 Ft  •  Bruttó 0 Ft")
        self.totals.setObjectName("totals")
        layout.addWidget(self.totals)

    def set_invoice(self, inv_id: int):
        self.inv_id = inv_id
        self.refresh()

    def refresh(self):
        if self.inv_id is None:
            return
        items = self.repo.list_items(self.inv_id)
        self.table.setRowCount(0)
        for it in items:
            row = self.table.rowCount(); self.table.insertRow(row)
            net = it['qty'] * it['unit']
            vals = [it['sku'], it['name'], str(it['qty']), f"{it['unit']/100:.2f}", str(it['vat']), f"{net/100:.2f}"]
            for c, text in enumerate(vals):
                item = QTableWidgetItem(text)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row, c, item)
        if items:
            self.table.selectRow(0)
        t = self.service.totals(self.inv_id)
        self.totals.setText(f"💰 Összesen: Nettó {t['net']/100:.2f} Ft  •  ÁFA {t['vat']/100:.2f} Ft  •  Bruttó {t['gross']/100:.2f} Ft")

    def selected_item_id(self) -> Optional[int]:
        idxs = self.table.selectionModel().selectedRows()
        if not idxs: return None
        row = idxs[0].row()
        items = self.repo.list_items(self.inv_id)
        if 0 <= row < len(items):
            return items[row]['id']
        return None

    def keyPressEvent(self, e):
        mw: MainWindow = self.parent().parent()
        key = e.key()
        if key == Qt.Key_Insert:
            mw.add_item_via_selector()
        elif key == Qt.Key_Delete:
            itid = self.selected_item_id()
            if itid is not None:
                dlg = ConfirmDialog("Biztosan törölni szeretnéd ezt a tételt?", "Tétel Törlése")
                if dlg.exec_() == QDialog.Accepted:
                    with mw.conn:
                        mw.repo.delete_item(itid)
                    self.refresh()
        elif key in (Qt.Key_Left,):
            itid = self.selected_item_id()
            if itid is not None:
                items = mw.repo.list_items(self.inv_id)
                idx = self.table.currentRow()
                new_q = max(0, items[idx]['qty'] - 1)
                with mw.conn:
                    mw.repo.set_item_qty(itid, new_q)
                self.refresh()
        elif key in (Qt.Key_Right, Qt.Key_Return, Qt.Key_Enter):
            itid = self.selected_item_id()
            if itid is not None:
                items = mw.repo.list_items(self.inv_id)
                idx = self.table.currentRow()
                new_q = items[idx]['qty'] + 1
                with mw.conn:
                    mw.repo.set_item_qty(itid, new_q)
                self.refresh()
        elif key == Qt.Key_Escape:
            mw.to_review()
        elif key in (Qt.Key_Up, Qt.Key_Down):
            super().keyPressEvent(e)
        else:
            e.ignore()

class ReviewPage(QWidget):
    def __init__(self, service: Service, repo: Repo, parent=None):
        super().__init__(parent)
        self.svc = service
        self.repo = repo
        self.inv_id: Optional[int] = None
        
        # Professional styling
        self.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
                font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
            }
            QLabel {
                color: #374151;
                background-color: transparent;
            }
            QLabel#header {
                font-size: 28px;
                font-weight: 600;
                color: #111827;
                margin-bottom: 16px;
                text-align: center;
            }
            QLabel#instructions {
                font-size: 16px;
                color: #6b7280;
                background-color: #ffffff;
                padding: 16px 20px;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                margin-bottom: 24px;
                text-align: center;
            }
            QLabel#summary {
                font-size: 18px;
                font-weight: 600;
                color: #059669;
                background-color: #d1fae5;
                padding: 20px 24px;
                border: 2px solid #a7f3d0;
                border-radius: 12px;
                margin: 12px 0;
            }
            QLabel#details {
                font-size: 14px;
                color: #4b5563;
                background-color: #ffffff;
                padding: 20px 24px;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                margin: 12px 0;
                line-height: 1.6;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setAlignment(Qt.AlignCenter)
        
        # Header
        header = QLabel("✅ Számla Ellenőrzés")
        header.setObjectName("header")
        layout.addWidget(header)
        
        # Instructions
        instructions = QLabel("Enter = Mentés és Befejezés  •  Esc = Vissza a Tételekhez")
        instructions.setObjectName("instructions")
        layout.addWidget(instructions)
        
        # Summary sections
        self.net = QLabel("")
        self.net.setObjectName("summary")
        layout.addWidget(self.net)
        
        self.vat = QLabel("")
        self.vat.setObjectName("summary")
        layout.addWidget(self.vat)
        
        self.gross = QLabel("")
        self.gross.setObjectName("summary")
        layout.addWidget(self.gross)
        
        self.details = QLabel("")
        self.details.setObjectName("details")
        layout.addWidget(self.details)
        
        # Add stretch to center content
        layout.addStretch()

    def set_invoice(self, inv_id: int):
        self.inv_id = inv_id
        t = self.svc.totals(inv_id)
        self.net.setText(f"💰 Nettó: {t['net']/100:.2f} Ft")
        self.vat.setText(f"📈 ÁFA: {t['vat']/100:.2f} Ft")
        self.gross.setText(f"💵 Bruttó: {t['gross']/100:.2f} Ft")
        lines = []
        for rate, d in sorted(t['rates'].items()):
            lines.append(f"📊 {rate}% ÁFA: Alap {d['base']/100:.2f} Ft → ÁFA {d['vat']/100:.2f} Ft")
        self.details.setText("📋 ÁFA Bontás:\n\n" + ("\n".join(lines) if lines else "❌ Nincsenek tételek"))

    def keyPressEvent(self, e):
        mw: MainWindow = self.parent().parent()
        if e.key() in (Qt.Key_Return, Qt.Key_Enter):
            dlg = ConfirmDialog("Szeretnéd menteni és befejezni ezt a számlát?", "Számla Mentése")
            if dlg.exec_() == QDialog.Accepted:
                mw.finish_and_back_to_list()
        elif e.key() == Qt.Key_Escape:
            mw.back_to_items()
        else:
            e.ignore()

# -------------------- MAIN WINDOW / ÁLLAPOTGÉP --------------------

class MainWindow(QMainWindow):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__()
        self.conn = conn
        self.repo = Repo(conn)
        self.service = Service(self.repo)
        self.setWindowTitle("Számlakezelő – Qt5 billentyű-only")
        self.resize(QSize(960, 640))

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.page_list = InvoiceListPage(self.repo)
        self.page_dir = DirectionPage()
        self.page_items = ItemsPage(self.repo, self.service)
        self.page_review = ReviewPage(self.service, self.repo)

        self.stack.addWidget(self.page_list)
        self.stack.addWidget(self.page_dir)
        self.stack.addWidget(self.page_items)
        self.stack.addWidget(self.page_review)

        self.current_direction = 'sale'
        self.current_partner_id: Optional[int] = None
        self.current_inv_id: Optional[int] = None

        self.show_list()

    # ---------- NAV ----------
    def show_list(self):
        self.page_list.refresh()
        self.stack.setCurrentWidget(self.page_list)

    def start_new_invoice(self):
        dlg = ConfirmDialog("Szeretnél új számlát létrehozni?", "Új Számla")
        if dlg.exec_() == QDialog.Accepted:
            self.current_direction = 'sale'
            self.current_partner_id = None
            self.current_inv_id = None
            self.stack.setCurrentWidget(self.page_dir)
        else:
            return

    def direction_chosen(self, direction: str):
        self.current_direction = direction
        # partner selector
        kind = 'customer' if direction == 'sale' else 'supplier'
        def fmt_row(r):
            return [r['name'], 'Vevő' if r['kind']=='customer' else 'Szállító']
        def on_new():
            pid = self.repo.add_partner("Új partner", kind)
            self.conn.commit()
            return self.repo.list_partners(kind)
        def on_del(r):
            self.conn.execute("DELETE FROM partner WHERE id=?", (r['id'],))
            self.conn.commit()
            return self.repo.list_partners(kind)
        dlg = ListSelectDialog("Partner kiválasztása", ["Név","Típus"], self.repo.list_partners(kind), fmt_row, on_new=on_new, on_delete=on_del)
        if dlg.exec_() == QDialog.Accepted:
            idx = dlg.current_index()
            rows = self.repo.list_partners(kind)
            if 0 <= idx < len(rows):
                self.current_partner_id = rows[idx]['id']
                number = f"INV{int(time.time())}"
                with self.conn:
                    self.current_inv_id = self.repo.create_invoice(number, self.current_partner_id, self.current_direction)
                self.page_items.set_invoice(self.current_inv_id)
                self.stack.setCurrentWidget(self.page_items)
        else:
            # back to direction page
            self.stack.setCurrentWidget(self.page_dir)

    def cancel_new_invoice(self):
        self.show_list()

    def add_item_via_selector(self):
        def fmt_row(r):
            return [r['sku'], r['name'], f"{r['unit']/100:.2f} Ft", f"ÁFA {r['vat']}%"]
        products = self.repo.list_products()
        dlg = ListSelectDialog("Termék kiválasztása", ["SKU","Név","Egysár","ÁFA"], products, fmt_row)
        if dlg.exec_() == QDialog.Accepted and self.current_inv_id is not None:
            idx = dlg.current_index()
            if 0 <= idx < len(products):
                with self.conn:
                    self.repo.add_item(self.current_inv_id, products[idx]['id'], 1)
                self.page_items.refresh()

    def to_review(self):
        if self.current_inv_id is None:
            return
        self.page_review.set_invoice(self.current_inv_id)
        self.stack.setCurrentWidget(self.page_review)

    def back_to_items(self):
        if self.current_inv_id is None:
            return
        self.page_items.set_invoice(self.current_inv_id)
        self.stack.setCurrentWidget(self.page_items)

    def finish_and_back_to_list(self):
        # Már DB-ben van minden; csak vissza a listához
        self.current_direction = 'sale'
        self.current_partner_id = None
        self.current_inv_id = None
        self.show_list()

    # ---------- KEY HANDLING (globális) ----------
    def keyPressEvent(self, e):
        w = self.stack.currentWidget()
        if w is self.page_list:
            key = e.key()
            if key == Qt.Key_Insert:
                self.start_new_invoice()
            elif key == Qt.Key_Delete:
                inv_id = self.page_list.selected_invoice_id()
                if inv_id is not None:
                    dlg = ConfirmDialog("Biztosan törölni szeretnéd ezt a számlát?\n\nEz a művelet nem visszavonható!", "Számla Törlése")
                    if dlg.exec_() == QDialog.Accepted:
                        with self.conn:
                            self.repo.delete_invoice(inv_id)
                        self.page_list.refresh()
            elif key in (Qt.Key_Return, Qt.Key_Enter):
                inv_id = self.page_list.selected_invoice_id()
                if inv_id is not None:
                    self.current_inv_id = inv_id
                    self.page_items.set_invoice(inv_id)
                    self.stack.setCurrentWidget(self.page_items)
            elif key == Qt.Key_Escape:
                dlg = ConfirmDialog("Biztosan ki szeretnél lépni az alkalmazásból?", "Kilépés")
                if dlg.exec_() == QDialog.Accepted:
                    self.close()
            else:
                super().keyPressEvent(e)
        else:
            # Delegáljuk az aktuális oldalnak (ItemsPage/DirectionPage/ReviewPage saját keyPressEvent-et kezel)
            super().keyPressEvent(e)

# -------------------- ENTRY --------------------

def main():
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    app = QApplication(sys.argv)
    mw = MainWindow(conn)
    mw.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
