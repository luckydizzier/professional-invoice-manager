#!/usr/bin/env python3
"""
Professional Invoice Manager v2.1 - Clean Working Version
Fixed all Qt constants issues and improved error handling
"""

import sys
import sqlite3
import time
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QDialog, QHeaderView,
    QMessageBox, QComboBox, QLineEdit, QSpinBox, QMenuBar, QAction, QStatusBar,
    QAbstractItemView, QShortcut, QDialogButtonBox, QFormLayout, QGroupBox,
    QTextEdit, QDoubleSpinBox
)
from PyQt5.QtGui import QKeySequence

# Load configuration with fallback
try:
    from config import config
except ImportError:
    class SimpleConfig:
        def get(self, key, default=None):
            if key == "database.path":
                return "invoice_qt5.db"
            elif key == "ui.window_width":
                return 1200
            elif key == "ui.window_height":
                return 800
            return default
        
        @property
        def window_size(self):
            return (1200, 800)
    
    config = SimpleConfig()


def format_date(timestamp_or_str):
    """Format datetime string or timestamp"""
    try:
        if isinstance(timestamp_or_str, int):
            return datetime.fromtimestamp(timestamp_or_str).strftime('%Y-%m-%d %H:%M')
        elif isinstance(timestamp_or_str, str):
            if 'T' in timestamp_or_str:
                dt = datetime.fromisoformat(timestamp_or_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(timestamp_or_str, '%Y-%m-%d %H:%M:%S')
            return dt.strftime('%Y-%m-%d %H:%M')
        else:
            return str(timestamp_or_str)
    except:
        return str(timestamp_or_str)


def get_db():
    """Get database connection"""
    db_path = config.get("database.path", "invoice_qt5.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database with correct schema"""
    with get_db() as conn:
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.executescript("""
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
        
        # Seed data if empty
        if conn.execute("SELECT COUNT(*) FROM product").fetchone()[0] == 0:
            products = [
                ("SKU001", "Kenyér 1kg", 69900, 5),
                ("SKU002", "Tej 1l", 39900, 18),
                ("SKU003", "Kolbász 1kg", 299900, 27),
                ("SKU004", "Kakaóscsiga", 34900, 27),
                ("SKU005", "Rostos üdítő 1l", 59900, 27),
            ]
            conn.executemany(
                "INSERT INTO product(sku,name,unit_price_cents,vat_rate) VALUES(?,?,?,?)",
                products,
            )
        
        if conn.execute("SELECT COUNT(*) FROM partner").fetchone()[0] == 0:
            partners = [
                ("Lakossági Vevő", "customer", None, None),
                ("Teszt Kft.", "customer", "12345678-1-42", "1111 Bp, Fő u. 1."),
                ("Minta Beszállító Zrt.", "supplier", "87654321-2-13", "7626 Pécs, Utca 2."),
            ]
            conn.executemany(
                "INSERT INTO partner(name,kind,tax_id,address) VALUES(?,?,?,?)",
                partners,
            )
        
        conn.commit()


class SimpleDialog(QDialog):
    """Simple, working dialog base class"""
    
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(400, 200)


class ProductFormDialog(QDialog):
    """Product management dialog"""
    
    def __init__(self, product_data=None, parent=None):
        super().__init__(parent)
        self.product_data = product_data
        self.setWindowTitle("🛍️ Termék" + (" szerkesztése" if product_data else " hozzáadása"))
        self.setModal(True)
        self.resize(450, 350)
        self.setup_ui()
        
        if product_data:
            self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QVBoxLayout()
        
        # SKU
        sku_layout = QHBoxLayout()
        sku_layout.addWidget(QLabel("📋 SKU:"))
        self.sku_edit = QLineEdit()
        self.sku_edit.setPlaceholderText("pl. SKU001")
        sku_layout.addWidget(self.sku_edit)
        form_layout.addLayout(sku_layout)
        
        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("🏷️ Név:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Termék neve")
        name_layout.addWidget(self.name_edit)
        form_layout.addLayout(name_layout)
        
        # Price in HUF (easier for users)
        price_layout = QHBoxLayout()
        price_layout.addWidget(QLabel("💰 Ár (HUF):"))
        self.price_edit = QLineEdit()
        self.price_edit.setPlaceholderText("pl. 1299")
        price_layout.addWidget(self.price_edit)
        form_layout.addLayout(price_layout)
        
        # VAT rate
        vat_layout = QHBoxLayout()
        vat_layout.addWidget(QLabel("📊 ÁFA (%):"))
        self.vat_spin = QSpinBox()
        self.vat_spin.setRange(0, 50)
        self.vat_spin.setValue(27)
        self.vat_spin.setSuffix("%")
        vat_layout.addWidget(self.vat_spin)
        form_layout.addLayout(vat_layout)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Set focus
        self.sku_edit.setFocus()
    
    def load_data(self):
        """Load existing product data"""
        if self.product_data:
            self.sku_edit.setText(self.product_data.get('sku', ''))
            self.name_edit.setText(self.product_data.get('name', ''))
            # Convert cents to HUF
            price_cents = self.product_data.get('unit_price_cents', 0)
            price_huf = price_cents / 100
            self.price_edit.setText(str(int(price_huf)))
            self.vat_spin.setValue(self.product_data.get('vat_rate', 27))
    
    def get_data(self):
        """Get form data"""
        try:
            price_huf = float(self.price_edit.text() or "0")
            price_cents = int(price_huf * 100)
        except ValueError:
            price_cents = 0
        
        return {
            'sku': self.sku_edit.text().strip(),
            'name': self.name_edit.text().strip(),
            'unit_price_cents': price_cents,
            'vat_rate': self.vat_spin.value()
        }
    
    def accept(self):
        """Validate and accept"""
        data = self.get_data()
        
        if not data['sku']:
            QMessageBox.warning(self, "Hiba", "A SKU mező kitöltése kötelező!")
            self.sku_edit.setFocus()
            return
        
        if not data['name']:
            QMessageBox.warning(self, "Hiba", "A név mező kitöltése kötelező!")
            self.name_edit.setFocus()
            return
        
        if data['unit_price_cents'] <= 0:
            QMessageBox.warning(self, "Hiba", "Az ár nagyobb kell legyen nullánál!")
            self.price_edit.setFocus()
            return
        
        super().accept()


class PartnerFormDialog(QDialog):
    """Partner (customer/supplier) management dialog"""
    
    def __init__(self, partner_data=None, partner_type="customer", parent=None):
        super().__init__(parent)
        self.partner_data = partner_data
        self.partner_type = partner_type
        
        type_text = "Vevő" if partner_type == "customer" else "Beszállító"
        self.setWindowTitle(f"👤 {type_text}" + (" szerkesztése" if partner_data else " hozzáadása"))
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
        
        if partner_data:
            self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QVBoxLayout()
        
        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("🏢 Név:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Partner neve")
        name_layout.addWidget(self.name_edit)
        form_layout.addLayout(name_layout)
        
        # Tax ID
        tax_layout = QHBoxLayout()
        tax_layout.addWidget(QLabel("🆔 Adószám:"))
        self.tax_edit = QLineEdit()
        self.tax_edit.setPlaceholderText("12345678-1-42")
        tax_layout.addWidget(self.tax_edit)
        form_layout.addLayout(tax_layout)
        
        # Address
        addr_layout = QVBoxLayout()
        addr_layout.addWidget(QLabel("🏠 Cím:"))
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("1111 Budapest, Példa utca 1.")
        addr_layout.addWidget(self.address_edit)
        form_layout.addLayout(addr_layout)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Set focus
        self.name_edit.setFocus()
    
    def load_data(self):
        """Load existing partner data"""
        if self.partner_data:
            self.name_edit.setText(self.partner_data.get('name', ''))
            self.tax_edit.setText(self.partner_data.get('tax_id', '') or '')
            self.address_edit.setText(self.partner_data.get('address', '') or '')
    
    def get_data(self):
        """Get form data"""
        return {
            'name': self.name_edit.text().strip(),
            'kind': self.partner_type,
            'tax_id': self.tax_edit.text().strip() or None,
            'address': self.address_edit.text().strip() or None
        }
    
    def accept(self):
        """Validate and accept"""
        data = self.get_data()
        
        if not data['name']:
            QMessageBox.warning(self, "Hiba", "A név mező kitöltése kötelező!")
            self.name_edit.setFocus()
            return
        
        super().accept()


class ManagementListPage(QWidget):
    """Base class for product/partner management pages"""
    
    def __init__(self, title, headers, parent=None):
        super().__init__(parent)
        self.title = title
        self.headers = headers
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header = QLabel(self.title)
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Instructions
        instructions = QLabel("Enter = Szerkesztés  •  Delete = Törlés  •  Insert = Új  •  F5 = Frissítés  •  Escape = Vissza")
        instructions.setStyleSheet("font-size: 12px; color: #7f8c8d; margin-bottom: 15px;")
        layout.addWidget(instructions)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ Új hozzáadása")
        self.add_btn.clicked.connect(self.add_item)
        button_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("✏️ Szerkesztés")
        self.edit_btn.clicked.connect(self.edit_item)
        button_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑️ Törlés")
        self.delete_btn.clicked.connect(self.delete_item)
        button_layout.addWidget(self.delete_btn)
        
        button_layout.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Frissítés")
        self.refresh_btn.clicked.connect(self.refresh)
        button_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(button_layout)
        
        # Table
        self.table = QTableWidget(0, len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.verticalHeader().setVisible(False)
        
        # Set table properties
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        
        # Set header resize mode
        header = self.table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.Stretch)
        
        # Style the table
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                selection-background-color: #3498db;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e9ecef;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Setup keyboard navigation
        self.table.setFocus()
        self.table.installEventFilter(self)
        
        layout.addWidget(self.table)
    
    def eventFilter(self, obj, event):
        """Handle keyboard events"""
        if obj == self.table and event.type() == event.KeyPress:
            key = event.key()
            
            if key == Qt.Key_F5:
                self.refresh()
                return True
            elif key in (Qt.Key_Return, Qt.Key_Enter):
                self.edit_item()
                return True
            elif key == Qt.Key_Delete:
                self.delete_item()
                return True
            elif key == Qt.Key_Insert:
                self.add_item()
                return True
            elif key == Qt.Key_Escape:
                self.parent().show_list()  # Go back to invoice list
                return True
        
        return super().eventFilter(obj, event)
    
    def add_item(self):
        """Override in subclasses"""
        pass
    
    def edit_item(self):
        """Override in subclasses"""
        pass
    
    def delete_item(self):
        """Override in subclasses"""
        pass
    
    def refresh(self):
        """Override in subclasses"""
        pass


class ProductListPage(ManagementListPage):
    """Product management page"""
    
    def __init__(self, parent=None):
        super().__init__("🛍️ Termékek Kezelése", 
                        ["📋 SKU", "🏷️ Név", "💰 Ár (HUF)", "📊 ÁFA (%)"], 
                        parent)
        self.refresh()
    
    def refresh(self):
        """Refresh product list"""
        try:
            with get_db() as conn:
                rows = conn.execute("""
                    SELECT id, sku, name, unit_price_cents, vat_rate 
                    FROM product 
                    ORDER BY name
                """).fetchall()
                
                self.table.setRowCount(0)
                for product in rows:
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    
                    # Convert cents to HUF for display
                    price_huf = product['unit_price_cents'] / 100
                    
                    vals = [
                        product['sku'],
                        product['name'],
                        f"{price_huf:,.0f} Ft",
                        f"{product['vat_rate']}%"
                    ]
                    
                    for c, text in enumerate(vals):
                        item = QTableWidgetItem(text)
                        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                        # Store the ID in the first column
                        if c == 0:
                            item.setData(Qt.UserRole, product['id'])
                        self.table.setItem(row, c, item)
                
                if rows:
                    self.table.selectRow(0)
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Termékek betöltése sikertelen: {str(e)}")
    
    def add_item(self):
        """Add new product"""
        dialog = ProductFormDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                with get_db() as conn:
                    conn.execute("""
                        INSERT INTO product (sku, name, unit_price_cents, vat_rate)
                        VALUES (?, ?, ?, ?)
                    """, (data['sku'], data['name'], data['unit_price_cents'], data['vat_rate']))
                    conn.commit()
                self.refresh()
                QMessageBox.information(self, "Siker", "Termék sikeresen hozzáadva!")
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Hiba", "Ez a SKU már létezik!")
            except Exception as e:
                QMessageBox.warning(self, "Hiba", f"Termék hozzáadása sikertelen: {str(e)}")
    
    def edit_item(self):
        """Edit selected product"""
        if self.table.currentRow() < 0:
            QMessageBox.information(self, "Figyelem", "Kérem válasszon ki egy terméket!")
            return
        
        # Get product ID from the selected row
        id_item = self.table.item(self.table.currentRow(), 0)
        if not id_item:
            return
        
        product_id = id_item.data(Qt.UserRole)
        
        try:
            with get_db() as conn:
                product = conn.execute("""
                    SELECT id, sku, name, unit_price_cents, vat_rate 
                    FROM product WHERE id = ?
                """, (product_id,)).fetchone()
                
                if product:
                    product_data = dict(product)
                    dialog = ProductFormDialog(product_data, parent=self)
                    if dialog.exec_() == QDialog.Accepted:
                        data = dialog.get_data()
                        conn.execute("""
                            UPDATE product 
                            SET sku=?, name=?, unit_price_cents=?, vat_rate=?
                            WHERE id=?
                        """, (data['sku'], data['name'], data['unit_price_cents'], 
                             data['vat_rate'], product_id))
                        conn.commit()
                        self.refresh()
                        QMessageBox.information(self, "Siker", "Termék sikeresen módosítva!")
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Hiba", "Ez a SKU már létezik!")
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Termék módosítása sikertelen: {str(e)}")
    
    def delete_item(self):
        """Delete selected product"""
        if self.table.currentRow() < 0:
            QMessageBox.information(self, "Figyelem", "Kérem válasszon ki egy terméket!")
            return
        
        # Get product name for confirmation
        name_item = self.table.item(self.table.currentRow(), 1)
        if not name_item:
            return
        
        product_name = name_item.text()
        
        reply = QMessageBox.question(self, "Megerősítés", 
                                   f"Biztosan törölni szeretné ezt a terméket?\n\n'{product_name}'",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Get product ID
            id_item = self.table.item(self.table.currentRow(), 0)
            product_id = id_item.data(Qt.UserRole)
            
            try:
                with get_db() as conn:
                    conn.execute("DELETE FROM product WHERE id = ?", (product_id,))
                    conn.commit()
                self.refresh()
                QMessageBox.information(self, "Siker", "Termék sikeresen törölve!")
            except Exception as e:
                QMessageBox.warning(self, "Hiba", f"Termék törlése sikertelen: {str(e)}")


class PartnerListPage(ManagementListPage):
    """Partner management page"""
    
    def __init__(self, partner_type="customer", parent=None):
        self.partner_type = partner_type
        type_title = "👥 Vevők Kezelése" if partner_type == "customer" else "🏭 Beszállítók Kezelése"
        super().__init__(type_title, 
                        ["🏢 Név", "🆔 Adószám", "🏠 Cím"], 
                        parent)
        self.refresh()
    
    def refresh(self):
        """Refresh partner list"""
        try:
            with get_db() as conn:
                rows = conn.execute("""
                    SELECT id, name, tax_id, address 
                    FROM partner 
                    WHERE kind = ?
                    ORDER BY name
                """, (self.partner_type,)).fetchall()
                
                self.table.setRowCount(0)
                for partner in rows:
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    
                    vals = [
                        partner['name'],
                        partner['tax_id'] or '-',
                        partner['address'] or '-'
                    ]
                    
                    for c, text in enumerate(vals):
                        item = QTableWidgetItem(text)
                        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                        # Store the ID in the first column
                        if c == 0:
                            item.setData(Qt.UserRole, partner['id'])
                        self.table.setItem(row, c, item)
                
                if rows:
                    self.table.selectRow(0)
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Partnerek betöltése sikertelen: {str(e)}")
    
    def add_item(self):
        """Add new partner"""
        dialog = PartnerFormDialog(partner_type=self.partner_type, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                with get_db() as conn:
                    conn.execute("""
                        INSERT INTO partner (name, kind, tax_id, address)
                        VALUES (?, ?, ?, ?)
                    """, (data['name'], data['kind'], data['tax_id'], data['address']))
                    conn.commit()
                self.refresh()
                type_text = "Vevő" if self.partner_type == "customer" else "Beszállító"
                QMessageBox.information(self, "Siker", f"{type_text} sikeresen hozzáadva!")
            except Exception as e:
                QMessageBox.warning(self, "Hiba", f"Partner hozzáadása sikertelen: {str(e)}")
    
    def edit_item(self):
        """Edit selected partner"""
        if self.table.currentRow() < 0:
            QMessageBox.information(self, "Figyelem", "Kérem válasszon ki egy partnert!")
            return
        
        # Get partner ID from the selected row
        id_item = self.table.item(self.table.currentRow(), 0)
        if not id_item:
            return
        
        partner_id = id_item.data(Qt.UserRole)
        
        try:
            with get_db() as conn:
                partner = conn.execute("""
                    SELECT id, name, kind, tax_id, address 
                    FROM partner WHERE id = ?
                """, (partner_id,)).fetchone()
                
                if partner:
                    partner_data = dict(partner)
                    dialog = PartnerFormDialog(partner_data, self.partner_type, parent=self)
                    if dialog.exec_() == QDialog.Accepted:
                        data = dialog.get_data()
                        conn.execute("""
                            UPDATE partner 
                            SET name=?, tax_id=?, address=?
                            WHERE id=?
                        """, (data['name'], data['tax_id'], data['address'], partner_id))
                        conn.commit()
                        self.refresh()
                        QMessageBox.information(self, "Siker", "Partner sikeresen módosítva!")
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Partner módosítása sikertelen: {str(e)}")
    
    def delete_item(self):
        """Delete selected partner"""
        if self.table.currentRow() < 0:
            QMessageBox.information(self, "Figyelem", "Kérem válasszon ki egy partnert!")
            return
        
        # Get partner name for confirmation
        name_item = self.table.item(self.table.currentRow(), 0)
        if not name_item:
            return
        
        partner_name = name_item.text()
        
        reply = QMessageBox.question(self, "Megerősítés", 
                                   f"Biztosan törölni szeretné ezt a partnert?\n\n'{partner_name}'",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Get partner ID
            partner_id = name_item.data(Qt.UserRole)
            
            try:
                with get_db() as conn:
                    conn.execute("DELETE FROM partner WHERE id = ?", (partner_id,))
                    conn.commit()
                self.refresh()
                QMessageBox.information(self, "Siker", "Partner sikeresen törölve!")
            except Exception as e:
                QMessageBox.warning(self, "Hiba", f"Partner törlése sikertelen: {str(e)}")


class MenuNavigationMixin:
    """Mixin for arrow key menu navigation"""
    
    def setup_menu_navigation(self):
        """Setup arrow key navigation for menus"""
        if hasattr(self, 'menuBar') and self.menuBar():
            self.menuBar().installEventFilter(self)
    
    def navigate_menu(self, direction):
        """Navigate menu with arrow keys"""
        if not hasattr(self, 'menuBar') or not self.menuBar():
            return False
        
        menubar = self.menuBar()
        actions = menubar.actions()
        
        if not actions:
            return False
        
        # Find current active menu
        current_menu = menubar.activeAction()
        if current_menu:
            current_index = actions.index(current_menu)
        else:
            current_index = 0
        
        # Navigate
        if direction == "left":
            new_index = (current_index - 1) % len(actions)
        elif direction == "right":
            new_index = (current_index + 1) % len(actions)
        else:
            return False
        
        # Activate new menu
        new_action = actions[new_index]
        menubar.setActiveAction(new_action)
        new_action.trigger()
        
        return True


class InvoiceListPage(QWidget):
    """Clean invoice list page with working keyboard navigation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header = QLabel("📄 Számlák Listája")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Instructions
        instructions = QLabel("F5 = Frissítés  •  Enter = Szerkesztés  •  Delete = Törlés")
        instructions.setStyleSheet("font-size: 12px; color: #7f8c8d; margin-bottom: 15px;")
        layout.addWidget(instructions)
        
        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["📅 Dátum", "📋 Számlaszám", "👤 Partner", "📊 Irány"])
        self.table.verticalHeader().setVisible(False)
        
        # Set table properties using proper methods
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        
        # Set header resize mode
        header = self.table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.Stretch)
        
        # Style the table
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                selection-background-color: #3498db;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e9ecef;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Setup keyboard navigation
        self.table.setFocus()
        self.table.installEventFilter(self)
        
        layout.addWidget(self.table)
    
    def eventFilter(self, obj, event):
        """Handle keyboard events"""
        if obj == self.table and event.type() == event.KeyPress:
            key = event.key()
            
            if key == Qt.Key_F5:
                self.refresh()
                return True
            elif key in (Qt.Key_Return, Qt.Key_Enter):
                self.edit_invoice()
                return True
            elif key == Qt.Key_Delete:
                self.delete_invoice()
                return True
            elif key == Qt.Key_Insert:
                self.add_invoice()
                return True
            elif key == Qt.Key_Escape:
                self.table.clearSelection()
                return True
        
        return super().eventFilter(obj, event)
    
    def refresh(self):
        """Refresh invoice list"""
        try:
            with get_db() as conn:
                rows = conn.execute("""
                    SELECT i.id, i.number, i.created_utc, i.direction, p.name as partner
                    FROM invoice i 
                    LEFT JOIN partner p ON i.partner_id = p.id 
                    ORDER BY i.created_utc DESC
                """).fetchall()
                
                self.table.setRowCount(0)
                for inv in rows:
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    vals = [
                        format_date(inv['created_utc']),
                        inv['number'],
                        inv['partner'] or 'Nincs partner',
                        'ELADÁS' if inv['direction'] == 'sale' else 'VÉTEL'
                    ]
                    for c, text in enumerate(vals):
                        item = QTableWidgetItem(text)
                        # Use proper Qt flags
                        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                        self.table.setItem(row, c, item)
                
                if rows:
                    self.table.selectRow(0)
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Lista frissítése sikertelen: {str(e)}")
    
    def add_invoice(self):
        """Add new invoice - placeholder"""
        QMessageBox.information(self, "Új számla", 
                               "Az új számla funkció jelenleg fejlesztés alatt áll.")
    
    def edit_invoice(self):
        """Edit selected invoice - placeholder"""
        if self.table.currentRow() < 0:
            QMessageBox.information(self, "Figyelem", "Kérem válasszon ki egy számlát!")
            return
        QMessageBox.information(self, "Szerkesztés", 
                               "A számla szerkesztés funkció jelenleg fejlesztés alatt áll.")
    
    def delete_invoice(self):
        """Delete selected invoice - placeholder"""
        if self.table.currentRow() < 0:
            QMessageBox.information(self, "Figyelem", "Kérem válasszon ki egy számlát!")
            return
        
        reply = QMessageBox.question(self, "Megerősítés", 
                                   "Biztosan törölni szeretné a kiválasztott számlát?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Törlés", 
                                   "A számla törlés funkció jelenleg fejlesztés alatt áll.")


class MainWindow(QMainWindow, MenuNavigationMixin):
    """Clean main window with working functionality and management pages"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.init_database()
        self.setup_menus()
        self.setup_keyboard_shortcuts()
        self.setup_menu_navigation()
        self.show_list()
    
    def setup_ui(self):
        """Setup main UI"""
        self.setWindowTitle("📄 Számlázó Rendszer v2.1 - Clean Edition")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
        
        # Stack for pages
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Pages
        self.list_page = InvoiceListPage(self)
        self.stack.addWidget(self.list_page)
        
        self.product_page = ProductListPage(self)
        self.stack.addWidget(self.product_page)
        
        self.customer_page = PartnerListPage("customer", self)
        self.stack.addWidget(self.customer_page)
        
        self.supplier_page = PartnerListPage("supplier", self)
        self.stack.addWidget(self.supplier_page)
        
        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("✅ Készen állunk")
    
    def init_database(self):
        """Initialize database"""
        try:
            init_database()
            self.status.showMessage("✅ Adatbázis inicializálva")
        except Exception as e:
            QMessageBox.critical(self, "Adatbázis hiba", f"Adatbázis inicializálás sikertelen: {str(e)}")
            sys.exit(1)
    
    def setup_menus(self):
        """Setup enhanced menu system with navigation"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("📁 &Fájl")
        
        refresh_action = QAction("🔄 &Frissítés", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_current)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        # New submenu
        new_menu = file_menu.addMenu("➕ &Új")
        
        new_invoice_action = QAction("📄 Új számla", self)
        new_invoice_action.setShortcut("Ctrl+N")
        new_invoice_action.triggered.connect(self.new_invoice)
        new_menu.addAction(new_invoice_action)
        
        new_product_action = QAction("🛍️ Új termék", self)
        new_product_action.setShortcut("Ctrl+Shift+P")
        new_product_action.triggered.connect(self.new_product)
        new_menu.addAction(new_product_action)
        
        new_customer_action = QAction("👥 Új vevő", self)
        new_customer_action.setShortcut("Ctrl+Shift+C")
        new_customer_action.triggered.connect(self.new_customer)
        new_menu.addAction(new_customer_action)
        
        new_supplier_action = QAction("🏭 Új beszállító", self)
        new_supplier_action.setShortcut("Ctrl+Shift+S")
        new_supplier_action.triggered.connect(self.new_supplier)
        new_menu.addAction(new_supplier_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 &Kilépés", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View Menu
        view_menu = menubar.addMenu("👁️ &Nézet")
        
        invoices_action = QAction("📄 &Számlák", self)
        invoices_action.setShortcut("F2")
        invoices_action.triggered.connect(self.show_list)
        view_menu.addAction(invoices_action)
        
        products_action = QAction("🛍️ &Termékek", self)
        products_action.setShortcut("F3")
        products_action.triggered.connect(self.show_products)
        view_menu.addAction(products_action)
        
        customers_action = QAction("👥 &Vevők", self)
        customers_action.setShortcut("F4")
        customers_action.triggered.connect(self.show_customers)
        view_menu.addAction(customers_action)
        
        suppliers_action = QAction("🏭 &Beszállítók", self)
        suppliers_action.setShortcut("F6")
        suppliers_action.triggered.connect(self.show_suppliers)
        view_menu.addAction(suppliers_action)
        
        # Management Menu
        manage_menu = menubar.addMenu("🔧 &Kezelés")
        
        manage_products_action = QAction("🛍️ Termékek kezelése", self)
        manage_products_action.triggered.connect(self.show_products)
        manage_menu.addAction(manage_products_action)
        
        manage_customers_action = QAction("👥 Vevők kezelése", self)
        manage_customers_action.triggered.connect(self.show_customers)
        manage_menu.addAction(manage_customers_action)
        
        manage_suppliers_action = QAction("🏭 Beszállítók kezelése", self)
        manage_suppliers_action.triggered.connect(self.show_suppliers)
        manage_menu.addAction(manage_suppliers_action)
        
        # Help Menu
        help_menu = menubar.addMenu("❓ &Súgó")
        
        shortcuts_action = QAction("🎹 &Billentyűparancsok", self)
        shortcuts_action.setShortcut("F1")
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        about_action = QAction("ℹ️ &Névjegy", self)
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)
    
    def setup_keyboard_shortcuts(self):
        """Setup global keyboard shortcuts"""
        # F-key shortcuts
        QShortcut(QKeySequence("F1"), self).activated.connect(self.show_shortcuts)
        QShortcut(QKeySequence("F2"), self).activated.connect(self.show_list)
        QShortcut(QKeySequence("F3"), self).activated.connect(self.show_products)
        QShortcut(QKeySequence("F4"), self).activated.connect(self.show_customers)
        QShortcut(QKeySequence("F5"), self).activated.connect(self.refresh_current)
        QShortcut(QKeySequence("F6"), self).activated.connect(self.show_suppliers)
        
        # Other shortcuts
        QShortcut(QKeySequence("Escape"), self).activated.connect(self.go_back)
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self.new_invoice)
        QShortcut(QKeySequence("Ctrl+Shift+P"), self).activated.connect(self.new_product)
        QShortcut(QKeySequence("Ctrl+Shift+C"), self).activated.connect(self.new_customer)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self).activated.connect(self.new_supplier)
    
    def keyPressEvent(self, event):
        """Handle global key events including menu navigation"""
        key = event.key()
        
        # Arrow key menu navigation
        if event.modifiers() == Qt.AltModifier:
            if key == Qt.Key_Left:
                if self.navigate_menu("left"):
                    return
            elif key == Qt.Key_Right:
                if self.navigate_menu("right"):
                    return
        
        super().keyPressEvent(event)
    
    # Page navigation methods
    def show_list(self):
        """Show invoice list"""
        self.list_page.refresh()
        self.stack.setCurrentWidget(self.list_page)
        self.status.showMessage("📋 Számlák listája")
    
    def show_products(self):
        """Show product management"""
        self.product_page.refresh()
        self.stack.setCurrentWidget(self.product_page)
        self.status.showMessage("🛍️ Termékek kezelése")
    
    def show_customers(self):
        """Show customer management"""
        self.customer_page.refresh()
        self.stack.setCurrentWidget(self.customer_page)
        self.status.showMessage("👥 Vevők kezelése")
    
    def show_suppliers(self):
        """Show supplier management"""
        self.supplier_page.refresh()
        self.stack.setCurrentWidget(self.supplier_page)
        self.status.showMessage("🏭 Beszállítók kezelése")
    
    def refresh_current(self):
        """Refresh current page"""
        current_widget = self.stack.currentWidget()
        if hasattr(current_widget, 'refresh'):
            current_widget.refresh()
            self.status.showMessage("🔄 Lista frissítve")
    
    def go_back(self):
        """Go back to invoice list or clear selection"""
        current_widget = self.stack.currentWidget()
        if current_widget == self.list_page:
            # Clear selection if on main page
            if hasattr(current_widget, 'table'):
                current_widget.table.clearSelection()
                self.status.showMessage("✨ Kijelölés törölve")
        else:
            # Go back to invoice list from other pages
            self.show_list()
    
    # New item methods
    def new_invoice(self):
        """Create new invoice - placeholder"""
        QMessageBox.information(self, "Új számla", 
                               "Az új számla funkció jelenleg fejlesztés alatt áll.")
    
    def new_product(self):
        """Create new product"""
        dialog = ProductFormDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                with get_db() as conn:
                    conn.execute("""
                        INSERT INTO product (sku, name, unit_price_cents, vat_rate)
                        VALUES (?, ?, ?, ?)
                    """, (data['sku'], data['name'], data['unit_price_cents'], data['vat_rate']))
                    conn.commit()
                
                # Refresh product page if visible
                if self.stack.currentWidget() == self.product_page:
                    self.product_page.refresh()
                
                self.status.showMessage("✅ Új termék hozzáadva")
                QMessageBox.information(self, "Siker", "Termék sikeresen hozzáadva!")
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Hiba", "Ez a SKU már létezik!")
            except Exception as e:
                QMessageBox.warning(self, "Hiba", f"Termék hozzáadása sikertelen: {str(e)}")
    
    def new_customer(self):
        """Create new customer"""
        dialog = PartnerFormDialog(partner_type="customer", parent=self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                with get_db() as conn:
                    conn.execute("""
                        INSERT INTO partner (name, kind, tax_id, address)
                        VALUES (?, ?, ?, ?)
                    """, (data['name'], data['kind'], data['tax_id'], data['address']))
                    conn.commit()
                
                # Refresh customer page if visible
                if self.stack.currentWidget() == self.customer_page:
                    self.customer_page.refresh()
                
                self.status.showMessage("✅ Új vevő hozzáadva")
                QMessageBox.information(self, "Siker", "Vevő sikeresen hozzáadva!")
            except Exception as e:
                QMessageBox.warning(self, "Hiba", f"Vevő hozzáadása sikertelen: {str(e)}")
    
    def new_supplier(self):
        """Create new supplier"""
        dialog = PartnerFormDialog(partner_type="supplier", parent=self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                with get_db() as conn:
                    conn.execute("""
                        INSERT INTO partner (name, kind, tax_id, address)
                        VALUES (?, ?, ?, ?)
                    """, (data['name'], data['kind'], data['tax_id'], data['address']))
                    conn.commit()
                
                # Refresh supplier page if visible
                if self.stack.currentWidget() == self.supplier_page:
                    self.supplier_page.refresh()
                
                self.status.showMessage("✅ Új beszállító hozzáadva")
                QMessageBox.information(self, "Siker", "Beszállító sikeresen hozzáadva!")
            except Exception as e:
                QMessageBox.warning(self, "Hiba", f"Beszállító hozzáadása sikertelen: {str(e)}")
    
    def show_shortcuts(self):
        """Show enhanced keyboard shortcuts help"""
        shortcuts_text = """
<h2>🎹 Billentyűparancsok</h2>

<h3>📋 Általános navigáció:</h3>
<table style='font-family: monospace; margin: 10px;'>
<tr><td><b>F1</b></td><td>Súgó megjelenítése</td></tr>
<tr><td><b>F2</b></td><td>Számlák listája</td></tr>
<tr><td><b>F3</b></td><td>Termékek kezelése</td></tr>
<tr><td><b>F4</b></td><td>Vevők kezelése</td></tr>
<tr><td><b>F5</b></td><td>Lista frissítése</td></tr>
<tr><td><b>F6</b></td><td>Beszállítók kezelése</td></tr>
<tr><td><b>Escape</b></td><td>Visszalépés / Kijelölés törlése</td></tr>
</table>

<h3>📝 Műveletek:</h3>
<table style='font-family: monospace; margin: 10px;'>
<tr><td><b>Enter</b></td><td>Kiválasztott elem szerkesztése</td></tr>
<tr><td><b>Delete</b></td><td>Kiválasztott elem törlése</td></tr>
<tr><td><b>Insert</b></td><td>Új elem hozzáadása</td></tr>
<tr><td><b>↑↓</b></td><td>Navigáció a listában</td></tr>
</table>

<h3>⚡ Gyorsbillentyűk:</h3>
<table style='font-family: monospace; margin: 10px;'>
<tr><td><b>Ctrl+N</b></td><td>Új számla</td></tr>
<tr><td><b>Ctrl+Shift+P</b></td><td>Új termék</td></tr>
<tr><td><b>Ctrl+Shift+C</b></td><td>Új vevő</td></tr>
<tr><td><b>Ctrl+Shift+S</b></td><td>Új beszállító</td></tr>
<tr><td><b>Ctrl+Q</b></td><td>Kilépés</td></tr>
</table>

<h3>🧭 Menü navigáció:</h3>
<table style='font-family: monospace; margin: 10px;'>
<tr><td><b>Alt + ←→</b></td><td>Menük közötti navigáció</td></tr>
<tr><td><b>Alt + betű</b></td><td>Menü aktiválása</td></tr>
</table>

<p><i>💡 Minden funkció elérhető billentyűzetről!</i></p>
        """
        
        QMessageBox.information(self, "🎹 Billentyűparancsok", shortcuts_text)
    
    def about(self):
        """Show about dialog"""
        QMessageBox.about(self, "📄 Számlázó Rendszer v2.1", 
                         "🎯 <b>Számlázó Rendszer v2.1</b><br><br>"
                         "🚀 <b>Clean Edition with Management</b><br><br>"
                         "✨ <b>Jellemzők:</b><br>"
                         "• 🎹 Teljes billentyűzet navigáció<br>"
                         "• 🛍️ Termékek kezelése<br>"
                         "• 👥 Vevők kezelése<br>"
                         "• 🏭 Beszállítók kezelése<br>"
                         "• 🧭 Menü navigáció nyilakkal<br>"
                         "• 🗄️ SQLite adatbázis<br>"
                         "• 📊 Számla kezelés<br>"
                         "• 🔧 Javított hibakezelés<br>"
                         "• 🎨 Professzionális megjelenés<br><br>"
                         "🔧 <b>Technológia:</b> PyQt5, SQLite<br>"
                         "📅 <b>Verzió:</b> 2.1.0<br>"
                         "© 2024 - Clean & Working Edition")


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Invoice Manager Clean")
    app.setApplicationVersion("2.1.0")
    app.setOrganizationName("Professional Software")
    
    # Apply basic styling
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f8f9fa;
        }
        QWidget {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 11pt;
        }
        QPushButton {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #0056b3;
        }
        QPushButton:pressed {
            background-color: #004085;
        }
        QMenuBar {
            background-color: #343a40;
            color: white;
            font-weight: bold;
        }
        QMenuBar::item {
            background-color: transparent;
            padding: 8px 12px;
        }
        QMenuBar::item:selected {
            background-color: #007bff;
        }
    """)
    
    try:
        window = MainWindow()
        window.show()
        
        print("✅ Invoice Manager v2.1 started successfully!")
        print("🎹 Use keyboard shortcuts for navigation")
        
        return app.exec_()
    except Exception as e:
        QMessageBox.critical(None, "Hiba", f"Alkalmazás indítási hiba:\n{str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
