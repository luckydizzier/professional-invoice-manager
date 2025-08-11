#!/usr/bin/env python3
"""
Professional Invoice Manager v2.1 - With Product & Supplier Management
Enhanced version with full management capabilities and keyboard navigation
"""
import sys
import sqlite3
import time
from datetime import datetime
from pathlib import Path

# Ensure src package is importable
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QDialog, QHeaderView,
    QMessageBox, QComboBox, QLineEdit, QSpinBox, QMenuBar, QAction, QStatusBar,
    QAbstractItemView, QShortcut, QDialogButtonBox, QFormLayout, QGroupBox,
    QTextEdit, QDoubleSpinBox, QToolBar, QCheckBox
)
from PyQt5.QtGui import QKeySequence

# Load configuration with fallback
try:
    from professional_invoice_manager.config import config
except ImportError:
    class SimpleConfig:
        def get(self, key, default=None):
            if key == "database.path":
                return "invoice_qt5.db"
            if key == "ui.window_width":
                return 1200
            if key == "ui.window_height":
                return 800
            return default

        @property
        def window_size(self):
            return (1200, 800)

    config = SimpleConfig()

from professional_invoice_manager.db import get_db, init_database


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
 

class InvoiceFormDialog(QDialog):
    """Invoice creation/editing dialog"""
    
    def __init__(self, invoice_data=None, parent=None):
        super().__init__(parent)
        self.invoice_data = invoice_data
        self.setWindowTitle("🧾 Számla" + (" szerkesztése" if invoice_data else " létrehozása"))
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.setup_ui()
        if invoice_data:
            self.load_data()
    
    def setup_ui(self):
        """Setup the form UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🧾 " + ("Számla szerkesztése" if self.invoice_data else "Új számla"))
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Invoice number
        self.number_edit = QLineEdit()
        self.number_edit.setPlaceholderText("pl. INV-001")
        form_layout.addRow("📋 Számlaszám:", self.number_edit)
        
        # Direction
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["sale", "purchase"])
        self.direction_combo.setItemText(0, "📤 Kimenő számla (eladás)")
        self.direction_combo.setItemText(1, "📥 Bejövő számla (beszerzés)")
        form_layout.addRow("🔄 Típus:", self.direction_combo)
        
        # Partner selection
        self.partner_combo = QComboBox()
        self.load_partners()
        form_layout.addRow("👤 Partner:", self.partner_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Mentés")
        self.save_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("❌ Mégse")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def load_partners(self):
        """Load available partners"""
        try:
            with get_db() as conn:
                partners = conn.execute("""
                    SELECT id, name, kind FROM partner ORDER BY name
                """).fetchall()
                
                for partner in partners:
                    icon = "👥" if partner['kind'] == 'customer' else "🏭"
                    text = f"{icon} {partner['name']}"
                    self.partner_combo.addItem(text, partner['id'])
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Partnerek betöltése sikertelen: {str(e)}")
    
    def load_data(self):
        """Load existing invoice data"""
        if not self.invoice_data:
            return
        
        self.number_edit.setText(self.invoice_data.get('number', ''))
        
        direction = self.invoice_data.get('direction', 'sale')
        index = 0 if direction == 'sale' else 1
        self.direction_combo.setCurrentIndex(index)
        
        # Set partner
        partner_id = self.invoice_data.get('partner_id')
        if partner_id:
            for i in range(self.partner_combo.count()):
                if self.partner_combo.itemData(i) == partner_id:
                    self.partner_combo.setCurrentIndex(i)
                    break
    
    def get_data(self):
        """Get form data"""
        try:
            return {
                'number': self.number_edit.text().strip(),
                'direction': 'sale' if self.direction_combo.currentIndex() == 0 else 'purchase',
                'partner_id': self.partner_combo.currentData()
            }
        except Exception:
            return {}
    
    def accept(self):
        """Validate and accept"""
        data = self.get_data()
        
        if not data['number']:
            QMessageBox.warning(self, "Hiba", "Kérem adja meg a számlaszámot!")
            self.number_edit.setFocus()
            return
        
        if not data['partner_id']:
            QMessageBox.warning(self, "Hiba", "Kérem válasszon partnert!")
            self.partner_combo.setFocus()
            return
        
        super().accept()


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
        if obj == self.table and event.type() == QEvent.KeyPress:
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
        QMessageBox.information(self, "Hozzáadás", 
                               "Ez a funkció nincs implementálva ebben az osztályban.")
    
    def edit_item(self):
        """Override in subclasses"""
        QMessageBox.information(self, "Szerkesztés", 
                               "Ez a funkció nincs implementálva ebben az osztályban.")
    
    def delete_item(self):
        """Override in subclasses"""
        QMessageBox.information(self, "Törlés", 
                               "Ez a funkció nincs implementálva ebben az osztályban.")
    
    def refresh(self):
        """Override in subclasses"""
        QMessageBox.information(self, "Frissítés", 
                               "Ez a funkció nincs implementálva ebben az osztályban.")


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


class InvoiceDetailWidget(QWidget):
    """Widget for displaying invoice details and items"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_invoice_id = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        self.header_label = QLabel("📋 Számla Részletei")
        self.header_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(self.header_label)
        
        # Invoice info section
        info_group = QGroupBox("📄 Számla Információk")
        info_layout = QFormLayout(info_group)
        
        self.number_label = QLabel()
        self.date_label = QLabel()
        self.direction_label = QLabel()
        self.partner_label = QLabel()
        
        info_layout.addRow("📋 Számlaszám:", self.number_label)
        info_layout.addRow("📅 Dátum:", self.date_label)
        info_layout.addRow("📊 Irány:", self.direction_label)
        info_layout.addRow("👤 Partner:", self.partner_label)
        
        layout.addWidget(info_group)
        
        # Items section
        items_group = QGroupBox("📦 Számla Tételek")
        items_layout = QVBoxLayout(items_group)
        
        # Items toolbar
        items_toolbar = QHBoxLayout()
        
        self.add_item_btn = QPushButton("➕ Tétel Hozzáadása")
        self.add_item_btn.clicked.connect(self.add_item)
        
        self.edit_item_btn = QPushButton("✏️ Tétel Szerkesztése")
        self.edit_item_btn.clicked.connect(self.edit_item)
        
        self.delete_item_btn = QPushButton("🗑️ Tétel Törlése")
        self.delete_item_btn.clicked.connect(self.delete_item)
        
        items_toolbar.addWidget(self.add_item_btn)
        items_toolbar.addWidget(self.edit_item_btn)
        items_toolbar.addWidget(self.delete_item_btn)
        items_toolbar.addStretch()
        
        items_layout.addLayout(items_toolbar)
        
        # Items table
        self.items_table = QTableWidget(0, 6)
        self.items_table.setHorizontalHeaderLabels([
            "📦 Termék", "📝 Leírás", "🔢 Mennyiség", 
            "💰 Egységár", "📊 ÁFA", "💵 Összesen"
        ])
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.items_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.items_table.setAlternatingRowColors(True)
        
        # Set header resize mode
        header = self.items_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Product
            header.setSectionResizeMode(1, QHeaderView.Stretch)  # Description
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Quantity
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Price
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # VAT
            header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Total
        
        self.items_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                selection-background-color: #3498db;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #e9ecef;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        
        items_layout.addWidget(self.items_table)
        
        # VAT Summary section
        vat_summary_group = QGroupBox("📊 ÁFA Összesítő")
        vat_summary_layout = QVBoxLayout(vat_summary_group)
        
        # VAT breakdown table
        self.vat_table = QTableWidget(0, 4)
        self.vat_table.setHorizontalHeaderLabels([
            "📊 ÁFA kulcs", "💰 Nettó alap", "📈 ÁFA összeg", "💵 Bruttó összeg"
        ])
        self.vat_table.verticalHeader().setVisible(False)
        self.vat_table.setMaximumHeight(150)
        self.vat_table.setAlternatingRowColors(True)
        
        # Set VAT table column widths
        vat_header = self.vat_table.horizontalHeader()
        if vat_header:
            vat_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # VAT rate
            vat_header.setSectionResizeMode(1, QHeaderView.Stretch)  # Net base
            vat_header.setSectionResizeMode(2, QHeaderView.Stretch)  # VAT amount
            vat_header.setSectionResizeMode(3, QHeaderView.Stretch)  # Gross amount
        
        self.vat_table.setStyleSheet("""
            QTableWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                selection-background-color: #e9ecef;
            }
            QTableWidget::item {
                padding: 4px 8px;
                border-bottom: 1px solid #e9ecef;
            }
            QHeaderView::section {
                background-color: #6c757d;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        
        vat_summary_layout.addWidget(self.vat_table)
        
        # Totals section
        totals_layout = QHBoxLayout()
        totals_layout.addStretch()
        
        self.totals_label = QLabel()
        self.totals_label.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            color: #2c3e50; 
            padding: 12px; 
            background-color: #ecf0f1; 
            border: 2px solid #bdc3c7; 
            border-radius: 6px;
        """)
        totals_layout.addWidget(self.totals_label)
        
        vat_summary_layout.addLayout(totals_layout)
        items_layout.addWidget(vat_summary_group)
        layout.addWidget(items_group)
        
        # Initially disable buttons
        self.update_buttons_state()
    
    def load_invoice(self, invoice_id):
        """Load invoice details and items"""
        self.current_invoice_id = invoice_id
        
        if not invoice_id:
            self.clear_details()
            return
        
        try:
            with get_db() as conn:
                # Load invoice info
                invoice = conn.execute("""
                    SELECT i.*, p.name as partner_name, p.tax_id, p.address
                    FROM invoice i
                    LEFT JOIN partner p ON i.partner_id = p.id
                    WHERE i.id = ?
                """, (invoice_id,)).fetchone()
                
                if invoice:
                    self.number_label.setText(invoice['number'])
                    self.date_label.setText(format_date(invoice['created_utc']))
                    
                    direction_text = "📤 Kimenő (eladás)" if invoice['direction'] == 'sale' else "📥 Bejövő (beszerzés)"
                    self.direction_label.setText(direction_text)
                    
                    partner_info = invoice['partner_name'] or "Nincs megadva"
                    if invoice['tax_id']:
                        partner_info += f" (Adószám: {invoice['tax_id']})"
                    self.partner_label.setText(partner_info)
                    
                    # Load invoice items
                    self.load_items()
                
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Számla betöltése sikertelen: {str(e)}")
        
        self.update_buttons_state()
    
    def load_items(self):
        """Load invoice items with detailed VAT breakdown"""
        if not self.current_invoice_id:
            return
        
        try:
            with get_db() as conn:
                items = conn.execute("""
                    SELECT ii.*, p.name as product_name, p.sku
                    FROM invoice_item ii
                    LEFT JOIN product p ON ii.product_id = p.id
                    WHERE ii.invoice_id = ?
                    ORDER BY ii.id
                """, (self.current_invoice_id,)).fetchall()
                
                self.items_table.setRowCount(len(items))
                
                # VAT breakdown calculation
                vat_breakdown = {}  # {vat_rate: {'net': amount, 'vat': amount, 'gross': amount}}
                total_net = 0
                total_vat = 0
                
                for row, item in enumerate(items):
                    product_text = item['product_name'] or "Egyedi tétel"
                    if item['sku']:
                        product_text = f"{item['sku']} - {product_text}"
                    
                    description = item['description'] or ""
                    quantity = item['qty']
                    unit_price = item['unit_price_cents'] / 100.0
                    vat_rate = item['vat_rate']
                    
                    line_net = quantity * unit_price
                    line_vat = line_net * (vat_rate / 100.0)
                    line_total = line_net + line_vat
                    
                    total_net += line_net
                    total_vat += line_vat
                    
                    # Update VAT breakdown
                    if vat_rate not in vat_breakdown:
                        vat_breakdown[vat_rate] = {'net': 0, 'vat': 0, 'gross': 0}
                    
                    vat_breakdown[vat_rate]['net'] += line_net
                    vat_breakdown[vat_rate]['vat'] += line_vat
                    vat_breakdown[vat_rate]['gross'] += line_total
                    
                    # Populate items table
                    self.items_table.setItem(row, 0, QTableWidgetItem(product_text))
                    self.items_table.setItem(row, 1, QTableWidgetItem(description))
                    self.items_table.setItem(row, 2, QTableWidgetItem(f"{quantity:.2f}"))
                    self.items_table.setItem(row, 3, QTableWidgetItem(f"{unit_price:.2f} Ft"))
                    self.items_table.setItem(row, 4, QTableWidgetItem(f"{vat_rate:.0f}%"))
                    self.items_table.setItem(row, 5, QTableWidgetItem(f"{line_total:.2f} Ft"))
                    
                    # Store item ID for editing
                    self.items_table.item(row, 0).setData(Qt.UserRole, item['id'])
                
                # Update VAT breakdown table
                self.update_vat_summary(vat_breakdown)
                
                # Update totals
                total_gross = total_net + total_vat
                totals_text = f"🏦 VÉGÖSSZEG: Nettó: {total_net:.2f} Ft  |  ÁFA: {total_vat:.2f} Ft  |  Bruttó: {total_gross:.2f} Ft"
                self.totals_label.setText(totals_text)
                
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Tételek betöltése sikertelen: {str(e)}")
    
    def update_vat_summary(self, vat_breakdown):
        """Update the VAT summary table"""
        # Sort VAT rates for consistent display
        sorted_rates = sorted(vat_breakdown.keys())
        self.vat_table.setRowCount(len(sorted_rates))
        
        for row, vat_rate in enumerate(sorted_rates):
            data = vat_breakdown[vat_rate]
            
            # VAT rate
            rate_item = QTableWidgetItem(f"{vat_rate:.0f}%")
            rate_item.setTextAlignment(Qt.AlignCenter)
            self.vat_table.setItem(row, 0, rate_item)
            
            # Net base
            net_item = QTableWidgetItem(f"{data['net']:.2f} Ft")
            net_item.setTextAlignment(Qt.AlignRight)
            self.vat_table.setItem(row, 1, net_item)
            
            # VAT amount
            vat_item = QTableWidgetItem(f"{data['vat']:.2f} Ft")
            vat_item.setTextAlignment(Qt.AlignRight)
            self.vat_table.setItem(row, 2, vat_item)
            
            # Gross amount
            gross_item = QTableWidgetItem(f"{data['gross']:.2f} Ft")
            gross_item.setTextAlignment(Qt.AlignRight)
            gross_item.setBackground(Qt.lightGray)  # Highlight the gross amounts
            self.vat_table.setItem(row, 3, gross_item)
    
    def clear_details(self):
        """Clear invoice details"""
        self.number_label.setText("")
        self.date_label.setText("")
        self.direction_label.setText("")
        self.partner_label.setText("")
        self.items_table.setRowCount(0)
        self.vat_table.setRowCount(0)
        self.totals_label.setText("")
        self.current_invoice_id = None
        self.update_buttons_state()
    
    def update_buttons_state(self):
        """Update button states based on selection"""
        has_invoice = self.current_invoice_id is not None
        has_item_selection = has_invoice and self.items_table.currentRow() >= 0
        
        self.add_item_btn.setEnabled(has_invoice)
        self.edit_item_btn.setEnabled(has_item_selection)
        self.delete_item_btn.setEnabled(has_item_selection)
    
    def add_item(self):
        """Add new invoice item"""
        if not self.current_invoice_id:
            return
        
        dialog = InvoiceItemDialog(self.current_invoice_id, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_items()
            # Notify parent to refresh totals
            if hasattr(self.parent(), 'refresh_invoice_list'):
                self.parent().refresh_invoice_list()
    
    def edit_item(self):
        """Edit selected invoice item"""
        current_row = self.items_table.currentRow()
        if current_row < 0:
            return
        
        item_id = self.items_table.item(current_row, 0).data(Qt.UserRole)
        dialog = InvoiceItemDialog(self.current_invoice_id, item_id, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_items()
            # Notify parent to refresh totals
            if hasattr(self.parent(), 'refresh_invoice_list'):
                self.parent().refresh_invoice_list()
    
    def delete_item(self):
        """Delete selected invoice item"""
        current_row = self.items_table.currentRow()
        if current_row < 0:
            return
        
        item_id = self.items_table.item(current_row, 0).data(Qt.UserRole)
        product_text = self.items_table.item(current_row, 0).text()
        
        reply = QMessageBox.question(self, "Megerősítés",
                                   f"Biztosan törölni szeretné a '{product_text}' tételt?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                with get_db() as conn:
                    conn.execute("DELETE FROM invoice_item WHERE id = ?", (item_id,))
                    conn.commit()
                
                self.load_items()
                # Notify parent to refresh totals
                if hasattr(self.parent(), 'refresh_invoice_list'):
                    self.parent().refresh_invoice_list()
                
            except Exception as e:
                QMessageBox.critical(self, "Hiba", f"Tétel törlése sikertelen: {str(e)}")


class InvoiceItemDialog(QDialog):
    """Dialog for adding/editing invoice items"""
    
    def __init__(self, invoice_id, item_id=None, parent=None):
        super().__init__(parent)
        self.invoice_id = invoice_id
        self.item_id = item_id
        self.setWindowTitle("📦 Számla Tétel" + (" szerkesztése" if item_id else " hozzáadása"))
        self.setModal(True)
        self.setFixedSize(600, 450)
        self.setup_ui()
        if item_id:
            self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("📦 " + ("Tétel szerkesztése" if self.item_id else "Új tétel hozzáadása"))
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Product selection
        self.product_combo = QComboBox()
        self.load_products()
        form_layout.addRow("📦 Termék:", self.product_combo)
        
        # Description
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Opcionális leírás...")
        form_layout.addRow("📝 Leírás:", self.description_edit)
        
        # Quantity
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0.01, 9999.99)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setValue(1.0)
        self.quantity_spin.setSuffix(" db")
        form_layout.addRow("🔢 Mennyiség:", self.quantity_spin)
        
        # Unit price
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0.01, 999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setSuffix(" Ft")
        form_layout.addRow("💰 Egységár:", self.price_spin)
        
        # VAT rate
        self.vat_spin = QSpinBox()
        self.vat_spin.setRange(0, 50)
        self.vat_spin.setValue(27)
        self.vat_spin.setSuffix("%")
        form_layout.addRow("📊 ÁFA:", self.vat_spin)
        
        layout.addLayout(form_layout)
        
        # Auto-fill checkbox
        self.auto_fill_check = QCheckBox("Termék adatainak automatikus kitöltése")
        self.auto_fill_check.setChecked(True)
        self.auto_fill_check.toggled.connect(self.on_auto_fill_changed)
        layout.addWidget(self.auto_fill_check)
        
        # Connect product change to auto-fill
        self.product_combo.currentTextChanged.connect(self.on_product_changed)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Mentés")
        self.save_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("❌ Mégse")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def load_products(self):
        """Load available products"""
        try:
            self.product_combo.addItem("-- Egyedi tétel --", None)
            
            with get_db() as conn:
                products = conn.execute("""
                    SELECT id, sku, name, unit_price_cents, vat_rate
                    FROM product ORDER BY name
                """).fetchall()
                
                for product in products:
                    text = f"{product['sku']} - {product['name']}"
                    self.product_combo.addItem(text, product)
                    
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Termékek betöltése sikertelen: {str(e)}")
    
    def on_product_changed(self):
        """Handle product selection change"""
        if not self.auto_fill_check.isChecked():
            return
        
        product = self.product_combo.currentData()
        if product:
            self.price_spin.setValue(product['unit_price_cents'] / 100.0)
            self.vat_spin.setValue(product['vat_rate'])
    
    def on_auto_fill_changed(self, checked):
        """Handle auto-fill checkbox change"""
        if checked:
            self.on_product_changed()
    
    def load_data(self):
        """Load existing item data"""
        if not self.item_id:
            return
        
        try:
            with get_db() as conn:
                item = conn.execute("""
                    SELECT * FROM invoice_item WHERE id = ?
                """, (self.item_id,)).fetchone()
                
                if item:
                    # Find and select product
                    if item['product_id']:
                        for i in range(self.product_combo.count()):
                            product = self.product_combo.itemData(i)
                            if product and product['id'] == item['product_id']:
                                self.product_combo.setCurrentIndex(i)
                                break
                    
                    self.description_edit.setText(item['description'] or "")
                    self.quantity_spin.setValue(item['qty'])
                    self.price_spin.setValue(item['unit_price_cents'] / 100.0)
                    self.vat_spin.setValue(item['vat_rate'])
                    
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Tétel betöltése sikertelen: {str(e)}")
    
    def get_data(self):
        """Get form data"""
        product = self.product_combo.currentData()
        return {
            'product_id': product['id'] if product else None,
            'description': self.description_edit.text().strip(),
            'quantity': self.quantity_spin.value(),
            'unit_price_cents': int(self.price_spin.value() * 100),
            'vat_rate': self.vat_spin.value()
        }
    
    def accept(self):
        """Validate and save"""
        data = self.get_data()
        
        if data['quantity'] <= 0:
            QMessageBox.warning(self, "Hiba", "A mennyiség nem lehet nulla vagy negatív!")
            self.quantity_spin.setFocus()
            return
        
        if data['unit_price_cents'] <= 0:
            QMessageBox.warning(self, "Hiba", "Az egységár nem lehet nulla vagy negatív!")
            self.price_spin.setFocus()
            return
        
        try:
            with get_db() as conn:
                if self.item_id:
                    # Update existing item
                    conn.execute("""
                        UPDATE invoice_item 
                        SET product_id=?, description=?, qty=?, unit_price_cents=?, vat_rate=?
                        WHERE id=?
                    """, (data['product_id'], data['description'], data['quantity'],
                          data['unit_price_cents'], data['vat_rate'], self.item_id))
                else:
                    # Create new item
                    conn.execute("""
                        INSERT INTO invoice_item 
                        (invoice_id, product_id, description, qty, unit_price_cents, vat_rate)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (self.invoice_id, data['product_id'], data['description'],
                          data['quantity'], data['unit_price_cents'], data['vat_rate']))
                
                conn.commit()
            
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Tétel mentése sikertelen: {str(e)}")


class InvoiceListPage(QWidget):
    """Invoice management page with two-column layout"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.refresh_invoice_list()
    
    def setup_ui(self):
        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Left column - Invoice list
        left_widget = QWidget()
        left_widget.setFixedWidth(400)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(12)
        left_layout.setContentsMargins(8, 8, 8, 8)
        
        # Left header
        left_header = QLabel("📄 Számlák Listája")
        left_header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 8px;")
        left_layout.addWidget(left_header)
        
        # Left toolbar
        left_toolbar = QHBoxLayout()
        
        self.add_invoice_btn = QPushButton("➕ Új")
        self.add_invoice_btn.clicked.connect(self.add_invoice)
        self.add_invoice_btn.setToolTip("Új számla létrehozása (Insert)")
        
        self.edit_invoice_btn = QPushButton("✏️ Szerk.")
        self.edit_invoice_btn.clicked.connect(self.edit_invoice)
        self.edit_invoice_btn.setToolTip("Számla szerkesztése (Enter)")
        
        self.delete_invoice_btn = QPushButton("🗑️ Törlés")
        self.delete_invoice_btn.clicked.connect(self.delete_invoice)
        self.delete_invoice_btn.setToolTip("Számla törlése (Delete)")
        
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.clicked.connect(self.refresh_invoice_list)
        self.refresh_btn.setToolTip("Lista frissítése (F5)")
        
        left_toolbar.addWidget(self.add_invoice_btn)
        left_toolbar.addWidget(self.edit_invoice_btn)
        left_toolbar.addWidget(self.delete_invoice_btn)
        left_toolbar.addStretch()
        left_toolbar.addWidget(self.refresh_btn)
        
        left_layout.addLayout(left_toolbar)
        
        # Invoice list table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["📋 Szám", "👤 Partner", "� Összeg"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        
        # Set header resize mode for compact view
        header = self.table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Number
            header.setSectionResizeMode(1, QHeaderView.Stretch)  # Partner
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Amount
        
        # Style the table for compact view
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                selection-background-color: #3498db;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #e9ecef;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        
        # Connect selection change
        self.table.itemSelectionChanged.connect(self.on_invoice_selected)
        
        # Setup keyboard navigation
        self.table.setFocus()
        self.table.installEventFilter(self)
        
        left_layout.addWidget(self.table)
        
        # Instructions
        instructions = QLabel("💡 F5=Frissít | Enter=Szerk | Del=Töröl | Ins=Új")
        instructions.setStyleSheet("font-size: 10px; color: #7f8c8d; margin-top: 5px;")
        left_layout.addWidget(instructions)
        
        main_layout.addWidget(left_widget)
        
        # Right column - Invoice details
        self.detail_widget = InvoiceDetailWidget(self)
        main_layout.addWidget(self.detail_widget, 2)  # Give more space to details
        
        # Initially disable edit/delete buttons
        self.update_buttons_state()
    
    def eventFilter(self, obj, event):
        """Handle keyboard events"""
        if obj == self.table and event.type() == QEvent.KeyPress:
            key = event.key()
            
            if key == Qt.Key_F5:
                self.refresh_invoice_list()
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
    
    def refresh_invoice_list(self):
        """Refresh invoice list"""
        try:
            with get_db() as conn:
                rows = conn.execute("""
                    SELECT i.id, i.number, i.created_utc, i.direction, p.name as partner,
                           COALESCE(SUM(ii.qty * ii.unit_price_cents * (1 + ii.vat_rate/100.0)), 0) as total_cents
                    FROM invoice i 
                    LEFT JOIN partner p ON i.partner_id = p.id 
                    LEFT JOIN invoice_item ii ON i.id = ii.invoice_id
                    GROUP BY i.id, i.number, i.created_utc, i.direction, p.name
                    ORDER BY i.created_utc DESC
                """).fetchall()
                
                self.table.setRowCount(len(rows))
                
                for row, data in enumerate(rows):
                    number_item = QTableWidgetItem(data['number'])
                    number_item.setData(Qt.UserRole, data['id'])
                    
                    partner_text = data['partner'] or "Nincs partner"
                    partner_item = QTableWidgetItem(partner_text)
                    
                    total_amount = data['total_cents'] / 100.0 if data['total_cents'] else 0
                    amount_text = f"{total_amount:.2f} Ft" if total_amount > 0 else "0.00 Ft"
                    amount_item = QTableWidgetItem(amount_text)
                    
                    self.table.setItem(row, 0, number_item)
                    self.table.setItem(row, 1, partner_item)
                    self.table.setItem(row, 2, amount_item)
                
                if rows:
                    self.table.selectRow(0)
                else:
                    self.detail_widget.clear_details()
                    
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Lista frissítése sikertelen: {str(e)}")
        
        self.update_buttons_state()
    
    # Alias for compatibility
    def refresh(self):
        """Compatibility alias for refresh_invoice_list"""
        self.refresh_invoice_list()
    
    def on_invoice_selected(self):
        """Handle invoice selection change"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            invoice_id = self.table.item(current_row, 0).data(Qt.UserRole)
            self.detail_widget.load_invoice(invoice_id)
        else:
            self.detail_widget.clear_details()
        
        self.update_buttons_state()
    
    def update_buttons_state(self):
        """Update button states based on selection"""
        has_selection = self.table.currentRow() >= 0
        self.edit_invoice_btn.setEnabled(has_selection)
        self.delete_invoice_btn.setEnabled(has_selection)
    
    def add_invoice(self):
        """Add new invoice"""
        dialog = InvoiceFormDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                with get_db() as conn:
                    conn.execute("""
                        INSERT INTO invoice (number, direction, partner_id, created_utc)
                        VALUES (?, ?, ?, ?)
                    """, (data['number'], data['direction'], data['partner_id'], int(time.time())))
                    conn.commit()
                    
                self.refresh_invoice_list()
                if hasattr(self.parent(), 'status'):
                    self.parent().status.showMessage(f"✅ Számla '{data['number']}' létrehozva!", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Hiba", f"Számla létrehozása sikertelen: {str(e)}")
    
    def edit_invoice(self):
        """Edit selected invoice"""
        if self.table.currentRow() < 0:
            QMessageBox.information(self, "Figyelem", "Kérem válasszon ki egy számlát!")
            return
        
        # Get invoice data
        try:
            invoice_id = self.table.item(self.table.currentRow(), 0).data(Qt.UserRole)
            
            with get_db() as conn:
                invoice = conn.execute("""
                    SELECT * FROM invoice WHERE id = ?
                """, (invoice_id,)).fetchone()
                
                if not invoice:
                    QMessageBox.warning(self, "Hiba", "Számla nem található!")
                    return
                
                invoice_data = dict(invoice)
                
            dialog = InvoiceFormDialog(invoice_data, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                with get_db() as conn:
                    conn.execute("""
                        UPDATE invoice SET number=?, direction=?, partner_id=? 
                        WHERE id=?
                    """, (data['number'], data['direction'], data['partner_id'], invoice_data['id']))
                    conn.commit()
                    
                self.refresh_invoice_list()
                if hasattr(self.parent(), 'status'):
                    self.parent().status.showMessage(f"✅ Számla '{data['number']}' frissítve!", 3000)
                    
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Számla szerkesztése sikertelen: {str(e)}")
    
    def delete_invoice(self):
        """Delete selected invoice"""
        if self.table.currentRow() < 0:
            QMessageBox.information(self, "Figyelem", "Kérem válasszon ki egy számlát!")
            return
        
        invoice_number = self.table.item(self.table.currentRow(), 0).text()
        invoice_id = self.table.item(self.table.currentRow(), 0).data(Qt.UserRole)
        
        reply = QMessageBox.question(self, "Megerősítés", 
                                   f"Biztosan törölni szeretné a '{invoice_number}' számlát?\n\nEz a művelet törli az összes kapcsolódó tételt is!",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                with get_db() as conn:
                    # Delete invoice items first (foreign key constraint)
                    conn.execute("DELETE FROM invoice_item WHERE invoice_id = ?", (invoice_id,))
                    # Then delete the invoice
                    conn.execute("DELETE FROM invoice WHERE id = ?", (invoice_id,))
                    conn.commit()
                    
                self.refresh_invoice_list()
                if hasattr(self.parent(), 'status'):
                    self.parent().status.showMessage(f"🗑️ Számla '{invoice_number}' törölve!", 3000)
                    
            except Exception as e:
                QMessageBox.critical(self, "Hiba", f"Számla törlése sikertelen: {str(e)}")


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


class MainWindow(QMainWindow, MenuNavigationMixin):
    """Main window with product & supplier management"""
    
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
        self.setWindowTitle("📄 Számlázó Rendszer v2.1 - Management Edition")
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
        self.status.showMessage("✅ Készen állunk - Management Edition")
    
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
        """Create new invoice"""
        dialog = InvoiceFormDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                with get_db() as conn:
                    conn.execute("""
                        INSERT INTO invoice (number, direction, partner_id, created_utc)
                        VALUES (?, ?, ?, ?)
                    """, (data['number'], data['direction'], data['partner_id'], int(time.time())))
                    conn.commit()
                
                # Switch to invoice list and refresh
                self.show_list()
                self.list_page.refresh()
                self.status.showMessage(f"✅ Számla '{data['number']}' létrehozva!", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Hiba", f"Számla létrehozása sikertelen: {str(e)}")
    
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
                         "🚀 <b>Management Edition</b><br><br>"
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
                         "© 2024 - Management Edition")


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Invoice Manager Management")
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
        
        print("✅ Invoice Manager v2.1 with Management started successfully!")
        print("🎹 Use F3=Products, F4=Customers, F6=Suppliers")
        print("🧭 Use Alt+Left/Right for menu navigation")
        
        return app.exec_()
    except Exception as e:
        QMessageBox.critical(None, "Hiba", f"Alkalmazás indítási hiba:\n{str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
