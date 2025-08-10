"""
Professional Invoice Manager v2.0
Enhanced version with external CSS, configuration, and comprehensive menu system
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
    QAbstractItemView
)

# Load configuration and styling
from config import config


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


class ConfirmDialog(QDialog):
    """Professional confirmation dialog"""
    
    def __init__(self, message, title="Megerősítés", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 160)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Message
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 14px; color: #2c3e50;")
        layout.addWidget(msg_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        layout.addLayout(btn_layout)
        
        btn_layout.addStretch()
        
        no_btn = QPushButton("❌ Nem")
        no_btn.setFixedSize(80, 32)
        no_btn.clicked.connect(self.reject)
        btn_layout.addWidget(no_btn)
        
        yes_btn = QPushButton("✅ Igen")
        yes_btn.setFixedSize(80, 32)
        yes_btn.setDefault(True)
        yes_btn.clicked.connect(self.accept)
        btn_layout.addWidget(yes_btn)


class ListSelectDialog(QDialog):
    """Professional list selection dialog"""
    
    def __init__(self, title, items, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(600, 400)
        self.selected = None
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Instructions
        instructions = QLabel("Válassz egy elemet a listából:")
        instructions.setStyleSheet("font-size: 14px; color: #7f8c8d; margin-bottom: 10px;")
        layout.addWidget(instructions)
        
        # Table
        self.table = QTableWidget(0, 1)
        self.table.setHorizontalHeaderLabels([title])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)
        
        # Populate table
        for value, text in items:
            row = self.table.rowCount()
            self.table.insertRow(row)
            item = QTableWidgetItem(text)
            item.setData(Qt.UserRole, value)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table.setItem(row, 0, item)
        
        if items:
            self.table.selectRow(0)
        
        # Buttons
        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)
        
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("❌ Mégse")
        cancel_btn.setFixedSize(100, 32)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("✅ Kiválaszt")
        ok_btn.setFixedSize(100, 32)
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept_selection)
        btn_layout.addWidget(ok_btn)
        
        # Double-click handler
        self.table.doubleClicked.connect(self.accept_selection)
    
    def accept_selection(self):
        current = self.table.currentRow()
        if current >= 0:
            item = self.table.item(current, 0)
            self.selected = item.data(Qt.UserRole)
            self.accept()
    
    def selected_value(self):
        return self.selected


class SimpleFormDialog(QDialog):
    """Simple form dialog for basic data entry"""
    
    def __init__(self, title, fields, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(400, 300)
        self.fields = {}
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Create form fields
        for field_name, field_type, default_value in fields:
            label = QLabel(field_name + ":")
            layout.addWidget(label)
            
            if field_type == "text":
                widget = QLineEdit(default_value)
            elif field_type == "number":
                widget = QSpinBox()
                widget.setRange(0, 999999)
                widget.setValue(int(default_value) if default_value else 0)
            else:
                widget = QLineEdit(default_value)
            
            self.fields[field_name] = widget
            layout.addWidget(widget)
        
        # Buttons
        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)
        
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("❌ Mégse")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Mentés")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
    
    def get_values(self):
        """Get form values"""
        values = {}
        for name, widget in self.fields.items():
            if isinstance(widget, QLineEdit):
                values[name] = widget.text()
            elif isinstance(widget, QSpinBox):
                values[name] = widget.value()
        return values


class InvoiceListPage(QWidget):
    """Invoice list page with date column"""
    
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
        header.setObjectName("header")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Instructions
        instructions = QLabel("F10 = Új számla  •  Delete = Törlés  •  Enter = Megnyitás  •  F5 = Frissítés")
        instructions.setStyleSheet("font-size: 12px; color: #7f8c8d; margin-bottom: 15px;")
        layout.addWidget(instructions)
        
        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["📅 Dátum", "📋 Számlaszám", "👤 Partner", "📊 Irány"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                gridline-color: #e9ecef;
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
        layout.addWidget(self.table)
    
    def refresh(self):
        """Refresh invoice list with date sorting"""
        try:
            with get_db() as conn:
                # Order by created_utc DESC (newest first) - using correct column name
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
                        format_date(inv['created_utc']),  # Use created_utc and handle timestamp
                        inv['number'],
                        inv['partner'] or 'Nincs partner',
                        'ELADÁS' if inv['direction'] == 'sale' else 'VÉTEL'
                    ]
                    for c, text in enumerate(vals):
                        it = QTableWidgetItem(text)
                        it.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                        self.table.setItem(row, c, it)
                
                if rows:
                    self.table.selectRow(0)
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Lista frissítése sikertelen: {str(e)}")
    
    def selected_invoice_id(self):
        """Get selected invoice ID"""
        idxs = self.table.selectionModel().selectedRows()
        if not idxs:
            return None
        row = idxs[0].row()
        
        with get_db() as conn:
            invs = list(conn.execute("""
                SELECT i.id FROM invoice i 
                LEFT JOIN partner p ON i.partner_id = p.id 
                ORDER BY i.created_utc DESC
            """).fetchall())
            
            if 0 <= row < len(invs):
                return invs[row]['id']
        return None


class MainWindow(QMainWindow):
    """Enhanced main window with comprehensive features"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_menus()
        self.load_styles()
        self.show_list()
    
    def setup_ui(self):
        """Setup main UI"""
        self.setWindowTitle("📄 Számlázó Rendszer v2.0 - Professional Edition")
        
        # Use config for window size
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
    
    def setup_menus(self):
        """Setup comprehensive menu system"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #34495e;
                color: white;
                font-weight: bold;
                padding: 4px;
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
            QMenu {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        # File Menu
        file_menu = menubar.addMenu("📁 &Fájl")
        
        refresh_action = QAction("🔄 &Frissítés", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_list)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        backup_action = QAction("💾 &Biztonsági mentés", self)
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 &Kilépés", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Data Menu
        data_menu = menubar.addMenu("📦 &Adatok")
        
        products_action = QAction("📦 &Termékek kezelése", self)
        products_action.triggered.connect(self.manage_products)
        data_menu.addAction(products_action)
        
        partners_action = QAction("👥 &Partnerek kezelése", self)
        partners_action.triggered.connect(self.manage_partners)
        data_menu.addAction(partners_action)
        
        # Reports Menu
        reports_menu = menubar.addMenu("📊 &Jelentések")
        
        planned_action = QAction("📅 &Tervezett jelentések", self)
        planned_action.triggered.connect(self.planned_reports)
        reports_menu.addAction(planned_action)
        
        # Settings Menu
        settings_menu = menubar.addMenu("⚙️ &Beállítások")
        
        config_action = QAction("🔧 &Konfiguráció", self)
        config_action.triggered.connect(self.open_settings)
        settings_menu.addAction(config_action)
        
        db_action = QAction("🗃️ &Adatbázis útvonal", self)
        db_action.triggered.connect(self.change_database_path)
        settings_menu.addAction(db_action)
        
        # Help Menu
        help_menu = menubar.addMenu("❓ &Súgó")
        
        about_action = QAction("ℹ️ &Névjegy", self)
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)
    
    def load_styles(self):
        """Load external CSS styles"""
        try:
            from style_manager import style_manager
            style_manager.apply_styles(self)
            self.status.showMessage("🎨 Stílusok betöltve")
        except Exception as e:
            self.status.showMessage(f"⚠️ Stílus betöltési hiba: {str(e)}")
    
    def show_list(self):
        """Show invoice list"""
        self.list_page.refresh()
        self.stack.setCurrentWidget(self.list_page)
        self.status.showMessage("📋 Számlák listája")
    
    def refresh_list(self):
        """Refresh current list"""
        self.list_page.refresh()
        self.status.showMessage("🔄 Lista frissítve")
    
    def manage_products(self):
        """Manage products"""
        try:
            with get_db() as conn:
                products = list(conn.execute("SELECT * FROM product ORDER BY name").fetchall())
                
                if not products:
                    QMessageBox.information(self, "Termékek", "Még nincsenek termékek a rendszerben.")
                    if self.add_product():
                        self.manage_products()  # Refresh the list
                    return
                
                # Show products list
                items = [(p['id'], f"{p['sku']} - {p['name']} - {p['unit_price_cents']/100:.2f} Ft") for p in products]
                dialog = ListSelectDialog("Termékek Kezelése", items, self)
                dialog.exec_()
                
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Termékek kezelése sikertelen: {str(e)}")
    
    def add_product(self):
        """Add new product"""
        try:
            dialog = SimpleFormDialog("Új Termék", [
                ("SKU", "text", ""),
                ("Megnevezés", "text", ""),
                ("Egységár (Ft)", "number", "0"),
                ("ÁFA (%)", "number", "27")
            ], self)
            
            if dialog.exec_() == QDialog.Accepted:
                values = dialog.get_values()
                with get_db() as conn:
                    conn.execute("""
                        INSERT INTO product (sku, name, unit_price_cents, vat_rate) 
                        VALUES (?, ?, ?, ?)
                    """, (
                        values["SKU"],
                        values["Megnevezés"],
                        values["Egységár (Ft)"] * 100,  # Convert to cents
                        values["ÁFA (%)"]
                    ))
                    conn.commit()
                
                self.status.showMessage("✅ Termék hozzáadva")
                return True
            return False
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Termék hozzáadása sikertelen: {str(e)}")
            return False
    
    def manage_partners(self):
        """Manage partners"""
        try:
            with get_db() as conn:
                partners = list(conn.execute("SELECT * FROM partner ORDER BY name").fetchall())
                
                if not partners:
                    QMessageBox.information(self, "Partnerek", "Még nincsenek partnerek a rendszerben.")
                    if self.add_partner():
                        self.manage_partners()  # Refresh the list
                    return
                
                # Show partners list
                items = [(p['id'], f"{p['name']} - {p['address'] or 'Nincs cím'}") for p in partners]
                dialog = ListSelectDialog("Partnerek Kezelése", items, self)
                dialog.exec_()
                
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Partnerek kezelése sikertelen: {str(e)}")
    
    def add_partner(self):
        """Add new partner"""
        try:
            dialog = SimpleFormDialog("Új Partner", [
                ("Név", "text", ""),
                ("Cím", "text", ""),
                ("Adószám", "text", "")
            ], self)
            
            if dialog.exec_() == QDialog.Accepted:
                values = dialog.get_values()
                with get_db() as conn:
                    conn.execute("""
                        INSERT INTO partner (name, address, tax_id) 
                        VALUES (?, ?, ?)
                    """, (
                        values["Név"],
                        values["Cím"],
                        values["Adószám"]
                    ))
                    conn.commit()
                
                self.status.showMessage("✅ Partner hozzáadva")
                return True
            return False
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Partner hozzáadása sikertelen: {str(e)}")
            return False
    
    def planned_reports(self):
        """Show planned reports"""
        QMessageBox.information(self, "Jelentések", 
                               "📊 Tervezett jelentések:\\n\\n"
                               "• Havi összesítők\\n"
                               "• ÁFA jelentések\\n"
                               "• Partner statisztikák\\n"
                               "• Termék forgalom\\n\\n"
                               "🚧 Fejlesztés alatt...")
    
    def open_settings(self):
        """Open settings dialog"""
        try:
            # Simple settings for now
            current_db = config.get("database.path", "invoice_qt5.db")
            dialog = SimpleFormDialog("Beállítások", [
                ("Adatbázis útvonal", "text", current_db),
                ("Ablak szélesség", "number", str(config.get("ui.window_width", 960))),
                ("Ablak magasság", "number", str(config.get("ui.window_height", 640)))
            ], self)
            
            if dialog.exec_() == QDialog.Accepted:
                values = dialog.get_values()
                config.set("database.path", values["Adatbázis útvonal"])
                config.set("ui.window_width", values["Ablak szélesség"])
                config.set("ui.window_height", values["Ablak magasság"])
                config.save()
                
                self.status.showMessage("💾 Beállítások mentve")
                QMessageBox.information(self, "Beállítások", 
                                       "A beállítások mentve lettek.\\n"
                                       "Egyes változtatások az újraindítás után lépnek érvénybe.")
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"Beállítások megnyitása sikertelen: {str(e)}")
    
    def change_database_path(self):
        """Change database path"""
        from PyQt5.QtWidgets import QFileDialog
        current_path = config.get("database.path", "invoice_qt5.db")
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Adatbázis fájl kiválasztása", current_path,
            "SQLite Database Files (*.db);;All Files (*)"
        )
        
        if path:
            config.set("database.path", path)
            config.save()
            QMessageBox.information(self, "Adatbázis útvonal", 
                                   f"Az új adatbázis útvonal:\\n{path}\\n\\n"
                                   "Az alkalmazás újraindítása után lép érvénybe.")
    
    def backup_database(self):
        """Backup current database"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            import shutil
            
            current_db = config.get("database.path", "invoice_qt5.db")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_backup = f"backup_{timestamp}.db"
            
            path, _ = QFileDialog.getSaveFileName(
                self, "Biztonsági mentés helye", default_backup,
                "SQLite Database Files (*.db);;All Files (*)"
            )
            
            if path:
                shutil.copy2(current_db, path)
                QMessageBox.information(self, "Biztonsági mentés", 
                                       f"✅ Mentés sikeres!\\n\\nMentve: {path}")
                self.status.showMessage(f"💾 Biztonsági mentés készült: {Path(path).name}")
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"❌ Mentés sikertelen:\\n{str(e)}")
    
    def about(self):
        """Show about dialog"""
        QMessageBox.about(self, "📄 Számlázó Rendszer v2.0", 
                         "🎯 <b>Számlázó Rendszer v2.0</b><br><br>"
                         "🚀 <b>Professzionális Edition</b><br><br>"
                         "✨ <b>Újdonságok:</b><br>"
                         "• 🎨 Külső CSS stíluslapok<br>"
                         "• ⚙️ Konfigurációs rendszer<br>"
                         "• 📊 Dátum szerinti rendezés<br>"
                         "• 🏢 Adatkezelési menük<br>"
                         "• 💾 Biztonsági mentés<br><br>"
                         "🔧 <b>Technológia:</b> PyQt5, SQLite<br>"
                         "📅 <b>Verzió:</b> 2.0.0<br>"
                         "© 2024 - AI Enhanced")
    
    def keyPressEvent(self, e):
        """Global key handling"""
        if e.key() == Qt.Key_F5:
            self.refresh_list()
        elif e.key() == Qt.Key_F1:
            self.about()
        elif e.key() == Qt.Key_F10:
            self.status.showMessage("🚧 Új számla funkció fejlesztés alatt...")
        else:
            super().keyPressEvent(e)


def main():
    """Enhanced main function"""
    app = QApplication(sys.argv)
    app.setApplicationName("Invoice Manager Professional")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Professional Software")
    
    # Set application icon (if available)
    try:
        app.setWindowIcon(app.style().standardIcon(app.style().SP_FileDialogDetailedView))
    except:
        pass
    
    # Apply global style
    app.setStyleSheet("""
        QApplication {
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-size: 10pt;
        }
        QMainWindow {
            background-color: #ecf0f1;
        }
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #21618c;
        }
    """)
    
    try:
        window = MainWindow()
        window.show()
        
        # Show startup message
        window.status.showMessage("🎉 Számlázó Rendszer v2.0 - Professional Edition elindítva")
        
        return app.exec_()
    except Exception as e:
        QMessageBox.critical(None, "Hiba", f"Alkalmazás indítási hiba:\\n{str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
