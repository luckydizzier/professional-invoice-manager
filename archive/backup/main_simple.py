"""
Simplified working version with correct Qt constants
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
    QAbstractItemView, QHBoxLayout, QPushButton
)

# Import our modules
from config import config
from style_manager import style_manager
from forms import ProductFormDialog, PartnerFormDialog, SettingsDialog


def format_date(dt_str: str) -> str:
    """Format datetime string for display"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return dt_str


class Repository:
    """Data access layer"""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
    
    def list_invoices(self) -> List[Dict]:
        """Get all invoices ordered by date (newest first)"""
        return list(self.conn.execute("""
            SELECT i.id, i.number, i.created, i.direction, p.name as partner
            FROM invoice i 
            LEFT JOIN partner p ON i.partner_id = p.id 
            ORDER BY i.created DESC
        """).fetchall())
    
    def list_products(self) -> List[Dict]:
        return list(self.conn.execute("SELECT * FROM product ORDER BY name").fetchall())
    
    def list_partners(self) -> List[Dict]:
        return list(self.conn.execute("SELECT * FROM partner ORDER BY name").fetchall())
    
    def create_invoice(self, number: str, direction: str, partner_id: int) -> int:
        cursor = self.conn.execute(
            "INSERT INTO invoice (number, direction, partner_id, created) VALUES (?, ?, ?, ?)",
            (number, direction, partner_id, datetime.now().isoformat())
        )
        return cursor.lastrowid


class MainWindow(QMainWindow):
    """Simplified main window"""
    
    def __init__(self):
        super().__init__()
        self.conn = None
        self.repo = None
        self.setup_database()
        self.setup_ui()
        self.setup_menus()
        self.load_styles()
    
    def setup_database(self):
        """Initialize database"""
        try:
            db_path = config.get("database.path", "invoice_qt5.db")
            self.conn = sqlite3.connect(db_path)
            self.conn.row_factory = sqlite3.Row
            self.repo = Repository(self.conn)
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to open database: {str(e)}")
            sys.exit(1)
    
    def setup_ui(self):
        """Setup UI"""
        self.setWindowTitle("📄 Számlázó Rendszer v2.0")
        self.setMinimumSize(1000, 700)
        
        # Main widget
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("📄 Számlák Listája")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(header)
        
        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["📅 Dátum", "📋 Számlaszám", "👤 Partner", "📊 Irány"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.table)
        
        # Status
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Készen")
        
        self.refresh_list()
    
    def setup_menus(self):
        """Setup menus"""
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
        
        # Settings Menu
        settings_menu = menubar.addMenu("⚙️ &Beállítások")
        
        config_action = QAction("🔧 &Konfiguráció", self)
        config_action.triggered.connect(self.open_settings)
        settings_menu.addAction(config_action)
        
        # Help Menu
        help_menu = menubar.addMenu("❓ &Súgó")
        
        about_action = QAction("ℹ️ &Névjegy", self)
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)
    
    def load_styles(self):
        """Load CSS styles"""
        try:
            style_manager.apply_styles(self)
            self.status.showMessage("Stílusok betöltve")
        except Exception as e:
            self.status.showMessage(f"Stílus hiba: {str(e)}")
    
    def refresh_list(self):
        """Refresh invoice list"""
        try:
            invoices = self.repo.list_invoices()
            self.table.setRowCount(0)
            
            for inv in invoices:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                items = [
                    format_date(inv['created']),
                    inv['number'],
                    inv['partner'] or 'Nincs partner',
                    'ELADÁS' if inv['direction'] == 'sale' else 'VÉTEL'
                ]
                
                for col, text in enumerate(items):
                    item = QTableWidgetItem(text)
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.table.setItem(row, col, item)
            
            self.status.showMessage(f"{len(invoices)} számla betöltve")
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Lista frissítése sikertelen: {str(e)}")
    
    def add_product(self):
        """Add new product"""
        try:
            dialog = ProductFormDialog(self.repo, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                self.status.showMessage("Termék hozzáadva")
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Termék hozzáadása sikertelen: {str(e)}")
    
    def list_products(self):
        """Show products"""
        try:
            products = self.repo.list_products()
            msg = "Termékek:\\n\\n"
            for p in products:
                msg += f"• {p['sku']} - {p['name']} - {p['unit']/100:.2f} Ft\\n"
            QMessageBox.information(self, "Termékek", msg if products else "Nincsenek termékek")
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Termékek listázása sikertelen: {str(e)}")
    
    def add_partner(self):
        """Add new partner"""
        try:
            dialog = PartnerFormDialog(self.repo, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                self.status.showMessage("Partner hozzáadva")
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Partner hozzáadása sikertelen: {str(e)}")
    
    def list_partners(self):
        """Show partners"""
        try:
            partners = self.repo.list_partners()
            msg = "Partnerek:\\n\\n"
            for p in partners:
                msg += f"• {p['name']} - {p['address'] or 'Nincs cím'}\\n"
            QMessageBox.information(self, "Partnerek", msg if partners else "Nincsenek partnerek")
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Partnerek listázása sikertelen: {str(e)}")
    
    def open_settings(self):
        """Open settings"""
        try:
            dialog = SettingsDialog(parent=self)
            if dialog.exec_() == QDialog.Accepted:
                self.status.showMessage("Beállítások mentve")
                self.load_styles()
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Beállítások megnyitása sikertelen: {str(e)}")
    
    def about(self):
        """Show about"""
        QMessageBox.about(self, "Névjegy", 
                         "📄 Számlázó Rendszer v2.0\\n\\n"
                         "Professzionális számlázó alkalmazás\\n"
                         "PyQt5 alapú grafikus felülettel\\n\\n"
                         "© 2024")
    
    def keyPressEvent(self, e):
        """Handle key events"""
        if e.key() == Qt.Key_F5:
            self.refresh_list()
        elif e.key() == Qt.Key_F1:
            self.about()
        else:
            super().keyPressEvent(e)
    
    def closeEvent(self, e):
        """Clean up on close"""
        if self.conn:
            self.conn.close()
        e.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Invoice Manager v2.0")
    app.setApplicationVersion("2.0")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
