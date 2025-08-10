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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QDialog, QHeaderView,
    QMessageBox, QComboBox, QLineEdit, QSpinBox, QMenuBar, QAction, QStatusBar,
    QAbstractItemView, QShortcut, QDialogButtonBox
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


class MainWindow(QMainWindow):
    """Clean main window with working functionality"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.init_database()
        self.setup_menus()
        self.setup_keyboard_shortcuts()
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
        """Setup simple menu system"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("📁 &Fájl")
        
        refresh_action = QAction("🔄 &Frissítés", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_list)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 &Kilépés", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
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
        # F5 - Refresh
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self.refresh_list)
        
        # F1 - Help
        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.activated.connect(self.show_shortcuts)
        
        # Escape - Clear selection
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(self.clear_selection)
    
    def show_list(self):
        """Show invoice list"""
        self.list_page.refresh()
        self.stack.setCurrentWidget(self.list_page)
        self.status.showMessage("📋 Számlák listája")
    
    def refresh_list(self):
        """Refresh current list"""
        self.list_page.refresh()
        self.status.showMessage("🔄 Lista frissítve")
    
    def clear_selection(self):
        """Clear table selection"""
        if hasattr(self.list_page, 'table'):
            self.list_page.table.clearSelection()
            self.status.showMessage("✨ Kijelölés törölve")
    
    def show_shortcuts(self):
        """Show keyboard shortcuts help"""
        shortcuts_text = """
<h2>🎹 Billentyűparancsok</h2>
<table style='font-family: monospace; margin: 10px;'>
<tr><td><b>F5</b></td><td>Lista frissítése</td></tr>
<tr><td><b>Enter</b></td><td>Kiválasztott számla szerkesztése</td></tr>
<tr><td><b>Delete</b></td><td>Számla törlése</td></tr>
<tr><td><b>Insert</b></td><td>Új számla</td></tr>
<tr><td><b>Escape</b></td><td>Kijelölés törlése</td></tr>
<tr><td><b>↑↓</b></td><td>Navigáció a listában</td></tr>
<tr><td><b>F1</b></td><td>Ez a súgó</td></tr>
<tr><td><b>Ctrl+Q</b></td><td>Kilépés</td></tr>
</table>
<p><i>💡 Minden funkció elérhető billentyűzetről!</i></p>
        """
        
        QMessageBox.information(self, "🎹 Billentyűparancsok", shortcuts_text)
    
    def about(self):
        """Show about dialog"""
        QMessageBox.about(self, "📄 Számlázó Rendszer v2.1", 
                         "🎯 <b>Számlázó Rendszer v2.1</b><br><br>"
                         "🚀 <b>Clean Edition</b><br><br>"
                         "✨ <b>Jellemzők:</b><br>"
                         "• 🎹 Teljes billentyűzet navigáció<br>"
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
