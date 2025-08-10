"""
Refactored Invoice Management Application
Professional architecture with external styling and comprehensive features
"""

import sys
import sqlite3
import time
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout,
    QLabel, QTableWidget, QTableWidgetItem, QDialog, QMenuBar, QMenu,
    QAction, QStatusBar, QMessageBox, QHeaderView, QFileDialog,
    QAbstractItemView
)
from PyQt5.QtGui import QFont

# Import our modules
from config import config
from style_manager import style_manager
from forms import ProductFormDialog, PartnerFormDialog, SettingsDialog


class StyleDialog(QDialog):
    """Base dialog with proper styling"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(420, 180)


class ConfirmDialog(StyleDialog):
    """Professional confirmation dialog"""
    
    def __init__(self, text: str, title: str = "Megerősítés", parent=None):
        super().__init__(title, parent)
        self.setObjectName("confirmDialog")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Icon and message
        message_layout = QVBoxLayout()
        
        icon_label = QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 24px; text-align: center;")
        message_layout.addWidget(icon_label)
        
        message_label = QLabel(text)
        message_label.setObjectName("message")
        message_label.setWordWrap(True)
        message_layout.addWidget(message_label)
        
        layout.addLayout(message_layout)
        
        # Instructions
        instructions = QLabel("Enter = Igen (Yes)    •    Esc = Nem (No)")
        instructions.setObjectName("instructions")
        layout.addWidget(instructions)
    
    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.accept()
        elif e.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(e)


class ListSelectDialog(StyleDialog):
    """Professional list selection dialog"""
    
    def __init__(self, title: str, headers: List[str], rows: List[Dict], 
                 fmt_row, on_new=None, on_delete=None, parent=None):
        super().__init__(title, parent)
        self.setObjectName("listSelectDialog")
        self.rows = rows
        self.fmt_row = fmt_row
        self.on_new = on_new
        self.on_delete = on_delete
        
        self.resize(800, 500)
        self.setup_ui(headers)
        self.populate()
    
    def setup_ui(self, headers):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title_label = QLabel(self.windowTitle())
        title_label.setObjectName("title")
        layout.addWidget(title_label)
        
        # Instructions
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
    
    def _build_instructions_text(self) -> str:
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
            row = self.table.rowCount()
            self.table.insertRow(row)
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


# Utility functions
def format_date(timestamp: int) -> str:
    """Convert UTC timestamp to formatted date string"""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")


def init_db(conn: sqlite3.Connection) -> None:
    """Initialize database with tables"""
    c = conn
    c.execute("PRAGMA foreign_keys=ON;")
    c.execute("PRAGMA journal_mode=WAL;")
    c.execute("PRAGMA synchronous=NORMAL;")
    c.executescript("""
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
    """)
    seed_data(c)
    conn.commit()


def seed_data(c: sqlite3.Connection) -> None:
    """Seed database with initial data"""
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


class Repository:
    """Data access layer"""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
    
    # Partner methods
    def list_partners(self, kind: Optional[str] = None) -> List[Dict]:
        if kind:
            cur = self.conn.execute(
                "SELECT id,name,kind,tax_id,address FROM partner WHERE kind=? ORDER BY name ASC", 
                (kind,)
            )
        else:
            cur = self.conn.execute(
                "SELECT id,name,kind,tax_id,address FROM partner ORDER BY name ASC"
            )
        return [{"id":r[0],"name":r[1],"kind":r[2],"tax_id":r[3],"address":r[4]} for r in cur]
    
    def add_partner(self, name: str, kind: str, tax_id: str = None, address: str = None) -> int:
        cur = self.conn.execute(
            "INSERT INTO partner(name,kind,tax_id,address) VALUES(?,?,?,?)", 
            (name, kind, tax_id, address)
        )
        return cur.lastrowid
    
    def update_partner(self, partner_id: int, name: str, tax_id: str = None, address: str = None) -> None:
        self.conn.execute(
            "UPDATE partner SET name=?, tax_id=?, address=? WHERE id=?",
            (name, tax_id, address, partner_id)
        )
    
    def delete_partner(self, partner_id: int) -> None:
        self.conn.execute("DELETE FROM partner WHERE id=?", (partner_id,))
    
    # Product methods
    def list_products(self) -> List[Dict]:
        cur = self.conn.execute(
            "SELECT id,sku,name,unit_price_cents,vat_rate FROM product ORDER BY name ASC"
        )
        return [{"id":r[0],"sku":r[1],"name":r[2],"unit_price_cents":r[3],"vat_rate":r[4]} for r in cur]
    
    def add_product(self, sku: str, name: str, unit_price_cents: int, vat_rate: int) -> int:
        cur = self.conn.execute(
            "INSERT INTO product(sku,name,unit_price_cents,vat_rate) VALUES(?,?,?,?)",
            (sku, name, unit_price_cents, vat_rate)
        )
        return cur.lastrowid
    
    def update_product(self, product_id: int, sku: str, name: str, unit_price_cents: int, vat_rate: int) -> None:
        self.conn.execute(
            "UPDATE product SET sku=?, name=?, unit_price_cents=?, vat_rate=? WHERE id=?",
            (sku, name, unit_price_cents, vat_rate, product_id)
        )
    
    def delete_product(self, product_id: int) -> None:
        self.conn.execute("DELETE FROM product WHERE id=?", (product_id,))
    
    # Invoice methods
    def list_invoices(self) -> List[Dict]:
        cur = self.conn.execute("""
            SELECT i.id,i.number,p.name,i.direction,i.created_utc 
            FROM invoice i 
            JOIN partner p ON p.id=i.partner_id 
            ORDER BY i.created_utc DESC
        """)
        return [{"id":r[0],"number":r[1],"partner":r[2],"direction":r[3],"created":r[4]} for r in cur]
    
    def create_invoice(self, number: str, partner_id: int, direction: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO invoice(number,partner_id,direction,created_utc,notes) VALUES(?,?,?,?,?)",
            (number, partner_id, direction, int(time.time()), ""),
        )
        return cur.lastrowid
    
    def delete_invoice(self, inv_id: int) -> None:
        self.conn.execute("DELETE FROM invoice WHERE id=?", (inv_id,))
    
    # Invoice item methods
    def list_items(self, inv_id: int) -> List[Dict]:
        cur = self.conn.execute("""
            SELECT ii.id,p.sku,p.name,ii.qty,ii.unit_price_cents,ii.vat_rate 
            FROM invoice_item ii 
            JOIN product p ON p.id=ii.product_id 
            WHERE ii.invoice_id=? ORDER BY ii.id ASC
        """, (inv_id,))
        return [{"id":r[0],"sku":r[1],"name":r[2],"qty":r[3],"unit":r[4],"vat":r[5]} for r in cur]
    
    def add_item(self, inv_id: int, product_id: int, qty: int) -> None:
        p = self.conn.execute(
            "SELECT unit_price_cents,vat_rate FROM product WHERE id=?", 
            (product_id,)
        ).fetchone()
        if not p:
            raise ValueError("product not found")
        self.conn.execute(
            "INSERT INTO invoice_item(invoice_id,product_id,qty,unit_price_cents,vat_rate) VALUES(?,?,?,?,?)",
            (inv_id, product_id, qty, p[0], p[1]),
        )
    
    def set_item_qty(self, item_id: int, qty: int) -> None:
        self.conn.execute("UPDATE invoice_item SET qty=? WHERE id=?", (qty, item_id))
    
    def delete_item(self, item_id: int) -> None:
        self.conn.execute("DELETE FROM invoice_item WHERE id=?", (item_id,))
    
    def ensure_schema(self) -> None:
        """Ensure database schema exists"""
        # This is already implemented in the original code
        # The schema creation is handled during initialization
        pass


class BusinessService:
    """Business logic layer"""
    
    def __init__(self, repo: Repository):
        self.repo = repo
    
    def calculate_totals(self, inv_id: int) -> Dict:
        """Calculate invoice totals"""
        lines = self.repo.list_items(inv_id)
        per_rate: Dict[int, Dict[str,int]] = {}
        net = 0
        
        for item in lines:
            line_total = item["qty"] * item["unit"]
            net += line_total
            rate = item["vat"]
            if rate not in per_rate:
                per_rate[rate] = {"base": 0, "vat": 0}
            per_rate[rate]["base"] += line_total
        
        vat_total = 0
        for rate, data in per_rate.items():
            vat_amount = int(round(data["base"] * rate / 100))
            data["vat"] = vat_amount
            vat_total += vat_amount
        
        return {
            "net": net, 
            "vat": vat_total, 
            "gross": net + vat_total, 
            "rates": per_rate
        }
    
    def generate_invoice_number(self) -> str:
        """Generate a unique invoice number"""
        prefix = config.get("business.invoice_number_prefix", "INV")
        timestamp = int(time.time())
        return f"{prefix}{timestamp}"


class InvoiceListPage(QWidget):
    """Main invoice list page"""
    
    def __init__(self, repo: Repository, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header = QLabel("📄 Számlák")
        header.setObjectName("header")
        layout.addWidget(header)
        
        # Instructions
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
    
    def refresh(self):
        rows = self.repo.list_invoices()
        self.table.setRowCount(0)
        for inv in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
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
        self.parent().keyPressEvent(e)


class DirectionPage(QWidget):
    """Invoice direction selection page"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.direction = 'sale'
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(48, 48, 48, 48)
        
        # Header
        header = QLabel("🔄 Számla Típusa")
        header.setObjectName("largeHeader")
        layout.addWidget(header)
        
        # Instructions
        instructions = QLabel("← Szállítói számla  •  → Vevői számla  •  Enter = Tovább  •  Esc = Mégse")
        instructions.setObjectName("instructions")
        layout.addWidget(instructions)
        
        # Current selection
        self.state = QLabel("📊 Aktuális: Vevői számla (Eladás)")
        self.state.setObjectName("current")
        layout.addWidget(self.state)
        
        layout.addStretch()
    
    def keyPressEvent(self, e):
        mw = self.parent().parent()
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
    """Invoice items management page"""
    
    def __init__(self, repo: Repository, service: BusinessService, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.service = service
        self.inv_id: Optional[int] = None
        self.setup_ui()
    
    def setup_ui(self):
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
            row = self.table.rowCount()
            self.table.insertRow(row)
            net = it['qty'] * it['unit']
            vals = [it['sku'], it['name'], str(it['qty']), 
                   f"{it['unit']/100:.2f}", str(it['vat']), f"{net/100:.2f}"]
            for c, text in enumerate(vals):
                item = QTableWidgetItem(text)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row, c, item)
        
        if items:
            self.table.selectRow(0)
        
        t = self.service.calculate_totals(self.inv_id)
        self.totals.setText(f"💰 Összesen: Nettó {t['net']/100:.2f} Ft  •  ÁFA {t['vat']/100:.2f} Ft  •  Bruttó {t['gross']/100:.2f} Ft")
    
    def selected_item_id(self) -> Optional[int]:
        idxs = self.table.selectionModel().selectedRows()
        if not idxs:
            return None
        row = idxs[0].row()
        items = self.repo.list_items(self.inv_id)
        if 0 <= row < len(items):
            return items[row]['id']
        return None
    
    def keyPressEvent(self, e):
        mw = self.parent().parent()
        key = e.key()
        if key == Qt.Key_Insert:
            mw.add_item_via_selector()
        elif key == Qt.Key_Delete:
            item_id = self.selected_item_id()
            if item_id is not None:
                dlg = ConfirmDialog("Biztosan törölni szeretnéd ezt a tételt?", "Tétel Törlése")
                if dlg.exec_() == QDialog.Accepted:
                    with mw.conn:
                        mw.repo.delete_item(item_id)
                    self.refresh()
        elif key in (Qt.Key_Left,):
            item_id = self.selected_item_id()
            if item_id is not None:
                items = mw.repo.list_items(self.inv_id)
                idx = self.table.currentRow()
                new_q = max(0, items[idx]['qty'] - 1)
                with mw.conn:
                    mw.repo.set_item_qty(item_id, new_q)
                self.refresh()
        elif key in (Qt.Key_Right, Qt.Key_Return, Qt.Key_Enter):
            item_id = self.selected_item_id()
            if item_id is not None:
                items = mw.repo.list_items(self.inv_id)
                idx = self.table.currentRow()
                new_q = items[idx]['qty'] + 1
                with mw.conn:
                    mw.repo.set_item_qty(item_id, new_q)
                self.refresh()
        elif key == Qt.Key_Escape:
            mw.to_review()
        elif key in (Qt.Key_Up, Qt.Key_Down):
            super().keyPressEvent(e)
        else:
            e.ignore()


class ReviewPage(QWidget):
    """Invoice review page"""
    
    def __init__(self, service: BusinessService, repo: Repository, parent=None):
        super().__init__(parent)
        self.service = service
        self.repo = repo
        self.inv_id: Optional[int] = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(48, 48, 48, 48)
        
        # Header
        header = QLabel("✅ Számla Ellenőrzés")
        header.setObjectName("largeHeader")
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
        
        layout.addStretch()
    
    def set_invoice(self, inv_id: int):
        self.inv_id = inv_id
        t = self.service.calculate_totals(inv_id)
        self.net.setText(f"💰 Nettó: {t['net']/100:.2f} Ft")
        self.vat.setText(f"📈 ÁFA: {t['vat']/100:.2f} Ft")
        self.gross.setText(f"💵 Bruttó: {t['gross']/100:.2f} Ft")
        
        lines = []
        for rate, d in sorted(t['rates'].items()):
            lines.append(f"📊 {rate}% ÁFA: Alap {d['base']/100:.2f} Ft → ÁFA {d['vat']/100:.2f} Ft")
        self.details.setText("📋 ÁFA Bontás:\n\n" + ("\n".join(lines) if lines else "❌ Nincsenek tételek"))
    
    def keyPressEvent(self, e):
        mw = self.parent().parent()
        if e.key() in (Qt.Key_Return, Qt.Key_Enter):
            dlg = ConfirmDialog("Szeretnéd menteni és befejezni ezt a számlát?", "Számla Mentése")
            if dlg.exec_() == QDialog.Accepted:
                mw.finish_and_back_to_list()
        elif e.key() == Qt.Key_Escape:
            mw.back_to_items()
        else:
            e.ignore()


class MainWindow(QMainWindow):
    """Main application window with menu system"""
    
    def __init__(self):
        super().__init__()
        self.conn = None
        self.repo = None
        self.service = None
        self.inv_id = None
        self.direction = None
        self.setup_database()
        self.setup_ui()
        self.setup_menus()
        self.load_styles()
        self.to_list()
    
    def setup_database(self):
        """Initialize database connection and services"""
        try:
            db_path = config.get("database.path", "invoices.db")
            self.conn = sqlite3.connect(db_path)
            self.conn.row_factory = sqlite3.Row
            self.repo = Repository(self.conn)
            self.service = BusinessService(self.repo)
            self.repo.ensure_schema()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to open database: {str(e)}")
            sys.exit(1)
    
    def setup_ui(self):
        """Setup main UI components"""
        self.setWindowTitle("📄 Számlázó Rendszer v2.0")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Central widget with stacked pages
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Initialize pages
        self.list_page = InvoiceListPage(self.repo, self)
        self.direction_page = DirectionPage(self)
        self.items_page = ItemsPage(self.repo, self.service, self)
        self.review_page = ReviewPage(self.service, self.repo, self)
        
        self.stack.addWidget(self.list_page)
        self.stack.addWidget(self.direction_page)
        self.stack.addWidget(self.items_page)
        self.stack.addWidget(self.review_page)
        
        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Készen")
    
    def setup_menus(self):
        """Setup comprehensive menu system"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("📁 &Fájl")
        
        new_action = QAction("📄 &Új számla", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_invoice)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        backup_action = QAction("💾 &Biztonsági mentés", self)
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)
        
        restore_action = QAction("📂 &Visszaállítás", self)
        restore_action.triggered.connect(self.restore_database)
        file_menu.addAction(restore_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 &Kilépés", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Products Menu
        products_menu = menubar.addMenu("📦 &Termékek")
        
        add_product_action = QAction("➕ &Új termék", self)
        add_product_action.triggered.connect(self.add_product)
        products_menu.addAction(add_product_action)
        
        list_products_action = QAction("📋 &Termékek listája", self)
        list_products_action.triggered.connect(self.list_products)
        products_menu.addAction(list_products_action)
        
        # Partners Menu
        partners_menu = menubar.addMenu("👥 &Partnerek")
        
        add_partner_action = QAction("➕ &Új partner", self)
        add_partner_action.triggered.connect(self.add_partner)
        partners_menu.addAction(add_partner_action)
        
        list_partners_action = QAction("📋 &Partnerek listája", self)
        list_partners_action.triggered.connect(self.list_partners)
        partners_menu.addAction(list_partners_action)
        
        # Reports Menu
        reports_menu = menubar.addMenu("📊 &Jelentések")
        
        planned_action = QAction("📅 &Tervezett", self)
        planned_action.triggered.connect(self.planned_reports)
        reports_menu.addAction(planned_action)
        
        # Settings Menu
        settings_menu = menubar.addMenu("⚙️ &Beállítások")
        
        config_action = QAction("🔧 &Konfiguráció", self)
        config_action.triggered.connect(self.open_settings)
        settings_menu.addAction(config_action)
        
        db_path_action = QAction("🗃️ &Adatbázis útvonal", self)
        db_path_action.triggered.connect(self.change_db_path)
        settings_menu.addAction(db_path_action)
        
        # Help Menu
        help_menu = menubar.addMenu("❓ &Súgó")
        
        about_action = QAction("ℹ️ &Névjegy", self)
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)
    
    def load_styles(self):
        """Load external CSS styles"""
        from style_manager import style_manager
        try:
            style_manager.apply_styles(self)
            self.status.showMessage("Stílusok betöltve")
        except Exception as e:
            self.status.showMessage(f"Stílus hiba: {str(e)}")
    
    # Navigation methods
    def to_list(self):
        """Navigate to invoice list"""
        self.list_page.refresh()
        self.stack.setCurrentWidget(self.list_page)
        self.status.showMessage("Számlák listája")
    
    def new_invoice(self):
        """Start new invoice creation"""
        self.stack.setCurrentWidget(self.direction_page)
        self.status.showMessage("Számla típus választása")
    
    def direction_chosen(self, direction: str):
        """Handle direction selection"""
        self.direction = direction
        number = self.service.generate_invoice_number()
        
        # Create invoice record
        with self.conn:
            self.inv_id = self.repo.create_invoice(
                number=number,
                direction=direction,
                partner_id=1  # Default partner for now
            )
        
        self.items_page.set_invoice(self.inv_id)
        self.stack.setCurrentWidget(self.items_page)
        self.status.showMessage(f"Számla tételek - {number}")
    
    def cancel_new_invoice(self):
        """Cancel invoice creation"""
        if self.inv_id:
            with self.conn:
                self.repo.delete_invoice(self.inv_id)
            self.inv_id = None
        self.to_list()
    
    def add_item_via_selector(self):
        """Add item via product selector"""
        products = self.repo.list_products()
        if not products:
            QMessageBox.information(self, "Nincs termék", "Először adj hozzá termékeket a rendszerhez!")
            return
        
        dialog = ListSelectDialog(
            title="Termék Választás",
            items=[(p['id'], f"{p['sku']} - {p['name']} ({p['unit']/100:.2f} Ft)") 
                   for p in products],
            parent=self
        )
        
        if dialog.exec_() == QDialog.Accepted:
            product_id = dialog.selected_value()
            if product_id:
                with self.conn:
                    self.repo.add_item(self.inv_id, product_id, 1)
                self.items_page.refresh()
    
    def to_review(self):
        """Navigate to review page"""
        self.review_page.set_invoice(self.inv_id)
        self.stack.setCurrentWidget(self.review_page)
        self.status.showMessage("Számla ellenőrzése")
    
    def back_to_items(self):
        """Return to items page"""
        self.stack.setCurrentWidget(self.items_page)
        self.status.showMessage("Számla tételek")
    
    def finish_and_back_to_list(self):
        """Finish invoice and return to list"""
        self.inv_id = None
        self.direction = None
        self.to_list()
    
    # Menu action handlers
    def add_product(self):
        """Add new product"""
        from forms import ProductFormDialog
        dialog = ProductFormDialog(self.repo, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.status.showMessage("Termék hozzáadva")
    
    def list_products(self):
        """Show products list"""
        products = self.repo.list_products()
        dialog = ListSelectDialog(
            title="Termékek Listája",
            items=[(p['id'], f"{p['sku']} - {p['name']} - {p['unit']/100:.2f} Ft") 
                   for p in products],
            parent=self,
            on_edit=self.edit_product,
            on_delete=self.delete_product
        )
        dialog.exec_()
    
    def edit_product(self, product_id: int):
        """Edit product"""
        from forms import ProductFormDialog
        dialog = ProductFormDialog(self.repo, product_id=product_id, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.status.showMessage("Termék módosítva")
    
    def delete_product(self, product_id: int):
        """Delete product"""
        if ConfirmDialog("Biztosan törölni szeretnéd ezt a terméket?", "Termék Törlése", self).exec_() == QDialog.Accepted:
            with self.conn:
                self.repo.delete_product(product_id)
            self.status.showMessage("Termék törölve")
    
    def add_partner(self):
        """Add new partner"""
        from forms import PartnerFormDialog
        dialog = PartnerFormDialog(self.repo, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.status.showMessage("Partner hozzáadva")
    
    def list_partners(self):
        """Show partners list"""
        partners = self.repo.list_partners()
        dialog = ListSelectDialog(
            title="Partnerek Listája",
            items=[(p['id'], f"{p['name']} - {p['address'] or 'Nincs cím'}") 
                   for p in partners],
            parent=self,
            on_edit=self.edit_partner,
            on_delete=self.delete_partner
        )
        dialog.exec_()
    
    def edit_partner(self, partner_id: int):
        """Edit partner"""
        from forms import PartnerFormDialog
        dialog = PartnerFormDialog(self.repo, partner_id=partner_id, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.status.showMessage("Partner módosítva")
    
    def delete_partner(self, partner_id: int):
        """Delete partner"""
        if ConfirmDialog("Biztosan törölni szeretnéd ezt a partnert?", "Partner Törlése", self).exec_() == QDialog.Accepted:
            with self.conn:
                self.repo.delete_partner(partner_id)
            self.status.showMessage("Partner törölve")
    
    def planned_reports(self):
        """Show planned reports"""
        QMessageBox.information(self, "Tervezett", "A jelentések funkció még fejlesztés alatt áll.")
    
    def open_settings(self):
        """Open settings dialog"""
        from forms import SettingsDialog
        dialog = SettingsDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.status.showMessage("Beállítások mentve")
            # Reload styles if changed
            self.load_styles()
    
    def change_db_path(self):
        """Change database path"""
        path, _ = QFileDialog.getSaveFileName(
            self, "Adatbázis fájl választása", 
            config.get("database.path", "invoices.db"),
            "SQLite Database (*.db)"
        )
        if path:
            config.set("database.path", path)
            config.save()
            QMessageBox.information(self, "Adatbázis útvonal", 
                                   f"Az új adatbázis útvonal érvényesítéséhez indítsd újra az alkalmazást.\n\nÚj útvonal: {path}")
    
    def backup_database(self):
        """Backup database"""
        path, _ = QFileDialog.getSaveFileName(
            self, "Biztonsági mentés mentése", 
            f"backup_{int(time.time())}.db",
            "SQLite Database (*.db)"
        )
        if path:
            try:
                import shutil
                current_db = config.get("database.path", "invoices.db")
                shutil.copy2(current_db, path)
                QMessageBox.information(self, "Biztonsági mentés", f"Mentés sikeres: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Hiba", f"Mentés sikertelen: {str(e)}")
    
    def restore_database(self):
        """Restore database"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Adatbázis visszaállítása", "",
            "SQLite Database (*.db)"
        )
        if path:
            if ConfirmDialog("Ez felülírja a jelenlegi adatbázist. Biztos vagy benne?", 
                           "Adatbázis Visszaállítása", self).exec_() == QDialog.Accepted:
                try:
                    import shutil
                    current_db = config.get("database.path", "invoices.db")
                    shutil.copy2(path, current_db)
                    QMessageBox.information(self, "Visszaállítás", 
                                         "Visszaállítás sikeres. Indítsd újra az alkalmazást.")
                except Exception as e:
                    QMessageBox.critical(self, "Hiba", f"Visszaállítás sikertelen: {str(e)}")
    
    def about(self):
        """Show about dialog"""
        QMessageBox.about(self, "Névjegy", 
                         "📄 Számlázó Rendszer v2.0\n\n"
                         "Professzionális számlázó alkalmazás\n"
                         "PyQt5 alapú grafikus felülettel\n\n"
                         "Fejlesztő: AI Assistant\n"
                         "© 2024")
    
    def keyPressEvent(self, e):
        """Global key handling"""
        if e.key() == Qt.Key_F1:
            self.about()
        elif e.key() == Qt.Key_F5:
            self.to_list()
        elif e.key() == Qt.Key_F10:
            self.new_invoice()
        else:
            super().keyPressEvent(e)
    
    def closeEvent(self, e):
        """Handle application close"""
        if self.conn:
            self.conn.close()
        e.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Invoice Manager v2.0")
    app.setApplicationVersion("2.0")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
