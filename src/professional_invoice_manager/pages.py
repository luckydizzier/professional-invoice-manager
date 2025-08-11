"""Page widgets for management features."""

from PyQt5.QtWidgets import (
    QLabel,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)


class InvoiceDetailWidget(QWidget):
    """Widget for displaying invoice details and items"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.vat_table = QTableWidget(0, 1)
        self.vat_table.setHorizontalHeaderLabels(["VAT"])
        layout.addWidget(self.vat_table)

    def update_vat_summary(self):
        """Placeholder for VAT summary update."""

    def load_invoice(self, invoice_id):
        """Placeholder for loading invoice details."""

    def clear_details(self):
        """Placeholder for clearing details."""


class ProductListPage(QWidget):
    """Product management page"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("📦 Termékek"))
        self.table = QTableWidget(0, 1)
        self.table.setHorizontalHeaderLabels(["🏷️ Név"])
        layout.addWidget(self.table)

    def refresh(self):
        """Placeholder refresh."""

    def add_item(self):
        """Placeholder add."""

    def edit_item(self):
        """Placeholder edit."""

    def delete_item(self):
        """Placeholder delete."""


class PartnerListPage(QWidget):
    """Partner management page"""

    def __init__(self, partner_type="customer", parent=None):
        super().__init__(parent)
        self.partner_type = partner_type
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("👥 Partnerek"))
        self.table = QTableWidget(0, 1)
        self.table.setHorizontalHeaderLabels(["🏢 Név"])
        layout.addWidget(self.table)

    def refresh(self):
        """Placeholder refresh."""

    def add_item(self):
        """Placeholder add."""

    def edit_item(self):
        """Placeholder edit."""

    def delete_item(self):
        """Placeholder delete."""


class InvoiceListPage(QWidget):
    """Invoice management page with two-column layout"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("📄 Számlák"))
        self.table = QTableWidget(0, 1)
        self.table.setHorizontalHeaderLabels(["📋 Szám"])
        layout.addWidget(self.table)
        self.detail_widget = InvoiceDetailWidget(self)
        layout.addWidget(self.detail_widget)

    def refresh(self):
        """Placeholder refresh."""

    def refresh_invoice_list(self):
        """Compatibility alias for refresh."""
        self.refresh()

    def add_invoice(self):
        """Placeholder add."""

    def edit_invoice(self):
        """Placeholder edit."""

    def delete_invoice(self):
        """Placeholder delete."""
