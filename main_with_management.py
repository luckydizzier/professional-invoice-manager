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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QShortcut,
    QSpinBox,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
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
from professional_invoice_manager.dialogs import (
    InvoiceFormDialog,
    PartnerFormDialog,
    ProductFormDialog,
)
from professional_invoice_manager.pages import (
    InvoiceListPage,
    PartnerListPage,
    ProductListPage,
)


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
