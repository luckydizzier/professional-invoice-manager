#!/usr/bin/env python3
"""
Fixed Professional Invoice Manager v2.0
Working version with proper Qt constants handling and keyboard navigation
"""

import sys
import sqlite3
import time
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QDialog, QHeaderView,
    QMessageBox, QComboBox, QLineEdit, QSpinBox, QMenuBar, QAction, QStatusBar,
    QAbstractItemView, QShortcut, QDialogButtonBox
)
from PyQt5.QtGui import QKeySequence

# Load configuration and styling
try:
    from config import config
except ImportError:
    # Fallback configuration
    class Config:
        def get(self, key, default=None):
            defaults = {
                "database.path": "invoice_qt5.db",
                "ui.window_width": 1200,
                "ui.window_height": 800
            }
            return defaults.get(key, default)
        
        @property
        def window_size(self):
            return (1200, 800)
    
    config = Config()

def format_date(timestamp_or_str):
    """Format datetime string or timestamp"""
    try:
        # If it's an integer timestamp
        if isinstance(timestamp_or_str, int):
            return datetime.fromtimestamp(timestamp_or_str).strftime('%Y-%m-%d %H:%M')
        # If it's a string with ISO format
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
        conn.execute("PRAGMA foreign_keys=ON")
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
        
        # Add sample data if empty
        if conn.execute("SELECT COUNT(*) FROM partner").fetchone()[0] == 0:
            conn.executescript("""
                INSERT INTO partner (name, kind, tax_id, address) VALUES 
                ('Teszt Ügyfél Kft.', 'customer', '12345678-1-23', '1234 Budapest, Teszt utca 1.'),
                ('Teszt Beszállító Zrt.', 'supplier', '87654321-2-34', '5678 Debrecen, Minta tér 2.');
                
                INSERT INTO product (sku, name, unit_price_cents, vat_rate) VALUES 
                ('PROD001', 'Teszt Termék 1', 10000, 27),
                ('PROD002', 'Teszt Termék 2', 25000, 27),
                ('SERV001', 'Teszt Szolgáltatás', 50000, 27);
                
                INSERT INTO invoice (number, partner_id, direction, created_utc, notes) VALUES 
                ('INV-001', 1, 'sale', ?, 'Teszt eladási számla'),
                ('INV-002', 2, 'purchase', ?, 'Teszt beszerzési számla');
            """, (int(time.time()), int(time.time()) - 86400))
        
        conn.commit()


class ConfirmDialog(QDialog):
    """Professional confirmation dialog"""
    
    def __init__(self, message, title="Megerősítés", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # Message
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 14px; padding: 20px;")
        layout.addWidget(msg_label)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class SimpleFormDialog(QDialog):
    """Simple form dialog for basic data entry"""
    
    def __init__(self, title, fields, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(400, 300)
        
        self.fields = {}
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)
        
        # Fields
        for field_name, field_type, default_value in fields:
            field_layout = QHBoxLayout()
            
            label = QLabel(f"{field_name}:")
            label.setMinimumWidth(120)
            field_layout.addWidget(label)
            
            if field_type == "text":
                widget = QLineEdit(str(default_value))
            elif field_type == "number":
                widget = QSpinBox()
                widget.setRange(0, 1000000)
                widget.setValue(int(default_value))
            else:
                widget = QLineEdit(str(default_value))
            
            self.fields[field_name] = widget
            field_layout.addWidget(widget)
            layout.addLayout(field_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_values(self):
        """Get form values"""
        values = {}
        for name, widget in self.fields.items():
            if isinstance(widget, QSpinBox):
                values[name] = widget.value()
            else:
                values[name] = widget.text()
        return values


class InvoiceListPage(QWidget):
    """Invoice list page with keyboard navigation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
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
        instructions = QLabel("🎹 F5=Frissítés • Enter=Szerkesztés • Delete=Törlés • Insert=Új • Escape=Mégse")
        instructions.setStyleSheet("font-size: 12px; color: #7f8c8d; margin-bottom: 15px;")
        layout.addWidget(instructions)
        
        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["📅 Dátum", "📋 Számlaszám", "👤 Partner", "📊 Irány"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Set column widths
        header = self.table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
        
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                gridline-color: #e9ecef;
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
        
        # Enhanced keyboard navigation
        self.table.setFocus()
        self.setup_table_keyboard_navigation()
        
        layout.addWidget(self.table)
        
        # Button panel
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Frissítés (F5)")
        refresh_btn.clicked.connect(self.refresh)
        button_layout.addWidget(refresh_btn)
        
        new_btn = QPushButton("➕ Új számla (Insert)")
        new_btn.clicked.connect(self.add_invoice)
        button_layout.addWidget(new_btn)
        
        edit_btn = QPushButton("✏️ Szerkesztés (Enter)")
        edit_btn.clicked.connect(self.edit_invoice)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Törlés (Delete)")
        delete_btn.clicked.connect(self.delete_invoice)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def setup_table_keyboard_navigation(self):
        """Setup keyboard navigation for the table"""
        self.table.installEventFilter(self)
        self.table.setFocusPolicy(Qt.StrongFocus)
        self.table.doubleClicked.connect(self.edit_invoice)
    
    def eventFilter(self, obj, event):
        """Handle keyboard events"""
        try:
            if obj == self.table and hasattr(event, 'type') and event.type() == event.KeyPress:
                key = event.key()
                
                # F5 - Refresh
                if key == 16777268:  # Qt.Key_F5
                    self.refresh()
                    return True
                
                # Enter/Return - Edit
                elif key in (16777220, 16777221):  # Qt.Key_Return, Qt.Key_Enter
                    if self.table.currentRow() >= 0:
                        self.edit_invoice()
                    return True
                
                # Delete - Delete
                elif key == 16777223:  # Qt.Key_Delete
                    if self.table.currentRow() >= 0:
                        self.delete_invoice()
                    return True
                
                # Insert - New
                elif key == 16777222:  # Qt.Key_Insert
                    self.add_invoice()
                    return True
                
                # Escape - Clear selection
                elif key == 16777216:  # Qt.Key_Escape
                    self.table.clearSelection()
                    return True
        
        except Exception as e:
            print(f"Event filter error: {e}")
            return False
        
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
                        '🔥 ELADÁS' if inv['direction'] == 'sale' else '📦 VÉTEL'
                    ]
                    for c, text in enumerate(vals):
                        item = QTableWidgetItem(text)
                        self.table.setItem(row, c, item)
                
                if rows:
                    self.table.selectRow(0)
                
            if self.main_window:
                self.main_window.status.showMessage(f"✅ {len(rows)} számla betöltve", 3000)
                
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Lista frissítése sikertelen: {str(e)}")
    
    def add_invoice(self):
        """Add new invoice - placeholder"""
        QMessageBox.information(self, "Fejlesztés alatt", 
                               "🔧 Az új számla funkció jelenleg fejlesztés alatt áll.\n"
                               "Hamarosan elérhető lesz!")
        if self.main_window:
            self.main_window.status.showMessage("🔧 Új számla funkció fejlesztés alatt...", 3000)
    
    def edit_invoice(self):
        """Edit selected invoice - placeholder"""
        if self.table.currentRow() < 0:
            QMessageBox.information(self, "Figyelem", "Kérem válasszon ki egy számlát!")
            return
        
        QMessageBox.information(self, "Fejlesztés alatt", 
                               "🔧 A számla szerkesztés funkció jelenleg fejlesztés alatt áll.\n"
                               "Hamarosan elérhető lesz!")
        if self.main_window:
            self.main_window.status.showMessage("🔧 Számla szerkesztés funkció fejlesztés alatt...", 3000)
    
    def delete_invoice(self):
        """Delete selected invoice - placeholder"""
        if self.table.currentRow() < 0:
            QMessageBox.information(self, "Figyelem", "Kérem válasszon ki egy számlát!")
            return
        
        dialog = ConfirmDialog("Biztosan törölni szeretné a kiválasztott számlát?", "Megerősítés", self)
        if dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "Fejlesztés alatt", 
                                   "🔧 A számla törlés funkció jelenleg fejlesztés alatt áll.\n"
                                   "Hamarosan elérhető lesz!")
            if self.main_window:
                self.main_window.status.showMessage("🔧 Számla törlés funkció fejlesztés alatt...", 3000)


class MainWindow(QMainWindow):
    """Enhanced main window with keyboard navigation"""
    
    def __init__(self):
        super().__init__()
        self.init_database()
        self.setup_ui()
        self.setup_menus()
        self.setup_keyboard_navigation()
        self.load_styles()
        self.show_list()
    
    def init_database(self):
        """Initialize database"""
        try:
            init_database()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to initialize database: {str(e)}")
            sys.exit(1)
    
    def setup_ui(self):
        """Setup main UI"""
        self.setWindowTitle("📄 Számlázó Rendszer v2.0 - Professional Edition")
        
        # Window size
        width, height = config.window_size
        self.resize(width, height)
        self.setMinimumSize(1000, 700)
        
        # Stack for pages
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Pages
        self.list_page = InvoiceListPage(self)
        self.stack.addWidget(self.list_page)
        
        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("✅ Készen állunk")
    
    def setup_keyboard_navigation(self):
        """Setup global keyboard shortcuts"""
        # F5 - Refresh
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self.refresh_current_view)
        
        # F1 - Help
        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.activated.connect(self.show_help)
        
        # Ctrl+N - New
        new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_shortcut.activated.connect(self.new_invoice)
        
        # Update status with hints
        self.update_keyboard_hints()
    
    def update_keyboard_hints(self):
        """Update status bar with keyboard hints"""
        hints = "🎹 F5:Frissítés | Ctrl+N:Új | Enter:Szerkesztés | Del:Törlés | F1:Súgó"
        self.status.showMessage(hints)
    
    def refresh_current_view(self):
        """Refresh current view"""
        if hasattr(self.list_page, 'refresh'):
            self.list_page.refresh()
        self.status.showMessage("✅ Lista frissítve", 2000)
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
<h2>🎹 Billentyűzet Navigáció</h2>
<table style='font-family: monospace; margin: 10px;'>
<tr><td><b>F5</b></td><td>Lista frissítése</td></tr>
<tr><td><b>Ctrl+N</b></td><td>Új számla létrehozása</td></tr>
<tr><td><b>Insert</b></td><td>Új számla (alternatív)</td></tr>
<tr><td><b>Enter</b></td><td>Kiválasztott számla szerkesztése</td></tr>
<tr><td><b>Delete</b></td><td>Számla törlése</td></tr>
<tr><td><b>Escape</b></td><td>Mégse / Vissza</td></tr>
<tr><td><b>↑↓</b></td><td>Navigáció a listában</td></tr>
<tr><td><b>Tab</b></td><td>Mezők közötti váltás</td></tr>
<tr><td><b>F1</b></td><td>Ez a súgó</td></tr>
</table>
<p><i>💡 Tipp: Minden funkció elérhető billentyűzetről!</i></p>
        """
        QMessageBox.information(self, "🎹 Billentyűzet Navigáció", help_text)
    
    def new_invoice(self):
        """New invoice shortcut"""
        if hasattr(self.list_page, 'add_invoice'):
            self.list_page.add_invoice()
    
    def setup_menus(self):
        """Setup menu system"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("📁 &Fájl")
        
        refresh_action = QAction("🔄 &Frissítés", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_current_view)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 &Kilépés", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Data menu
        data_menu = menubar.addMenu("📦 &Adatok")
        
        products_action = QAction("📦 &Termékek", self)
        products_action.triggered.connect(self.manage_products)
        data_menu.addAction(products_action)
        
        partners_action = QAction("👥 &Partnerek", self)
        partners_action.triggered.connect(self.manage_partners)
        data_menu.addAction(partners_action)
        
        # Help menu
        help_menu = menubar.addMenu("❓ &Súgó")
        
        help_action = QAction("🎹 &Billentyűzet", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        about_action = QAction("ℹ️ &Névjegy", self)
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)
    
    def load_styles(self):
        """Load external CSS styles"""
        try:
            # Try to load external styles
            styles_dir = Path("styles")
            if styles_dir.exists():
                main_css = styles_dir / "main.css"
                if main_css.exists():
                    with open(main_css, 'r', encoding='utf-8') as f:
                        stylesheet = f.read()
                        self.setStyleSheet(stylesheet)
                        self.status.showMessage("✅ Stílusok betöltve", 2000)
                        return
        except Exception as e:
            print(f"CSS loading error: {e}")
        
        # Fallback inline styles
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QMenuBar {
                background-color: #2c3e50;
                color: white;
                padding: 5px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
                margin: 2px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #3498db;
            }
            QStatusBar {
                background-color: #ecf0f1;
                border-top: 1px solid #bdc3c7;
                padding: 5px;
            }
        """)
    
    def show_list(self):
        """Show invoice list"""
        self.stack.setCurrentWidget(self.list_page)
        self.status.showMessage("📋 Számlák listája")
    
    def manage_products(self):
        """Manage products"""
        QMessageBox.information(self, "Fejlesztés alatt", 
                               "🔧 A termékkezelés funkció jelenleg fejlesztés alatt áll.\n"
                               "Hamarosan elérhető lesz!")
    
    def manage_partners(self):
        """Manage partners"""
        QMessageBox.information(self, "Fejlesztés alatt", 
                               "🔧 A partnerkezelés funkció jelenleg fejlesztés alatt áll.\n"
                               "Hamarosan elérhető lesz!")
    
    def about(self):
        """Show about dialog"""
        about_text = """
<h2>📄 Számlázó Rendszer v2.0</h2>
<p><b>Professional Edition</b></p>
<p>Modern számlakezelo alkalmazás PyQt5 alapokon</p>
<br>
<p><b>🎹 Jellemzők:</b></p>
<ul>
<li>Teljes billentyűzet navigáció</li>
<li>Professzionális megjelenés</li>
<li>SQLite adatbázis</li>
<li>Rugalmas konfiguráció</li>
</ul>
<br>
<p><i>Készítette: AI Assistant</i></p>
        """
        QMessageBox.about(self, "Névjegy", about_text)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Professional Invoice Manager")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Invoice Solutions")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
