"""Dialog classes for user interactions."""

import logging
import sqlite3

from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
)

from professional_invoice_manager.db import get_db


class PartnerFormDialog(QDialog):
    """Partner (customer/supplier) management dialog."""

    def __init__(
        self, partner_data=None, partner_type="customer", parent=None
    ):
        super().__init__(parent)
        self.partner_data = partner_data
        self.partner_type = partner_type

        type_text = "Vevő" if partner_type == "customer" else "Beszállító"
        title_suffix = " szerkesztése" if partner_data else " hozzáadása"
        self.setWindowTitle(f"👤 {type_text}{title_suffix}")
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
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Set focus
        self.name_edit.setFocus()

    def load_data(self):
        """Load existing partner data."""
        if self.partner_data:
            self.name_edit.setText(self.partner_data.get('name', ''))
            self.tax_edit.setText(self.partner_data.get('tax_id', '') or '')
            self.address_edit.setText(
                self.partner_data.get('address', '') or ''
            )

    def get_data(self):
        """Get form data."""
        return {
            'name': self.name_edit.text().strip(),
            'kind': self.partner_type,
            'tax_id': self.tax_edit.text().strip() or None,
            'address': self.address_edit.text().strip() or None,
        }

    def accept(self):
        """Validate and accept."""
        data = self.get_data()

        if not data['name']:
            QMessageBox.warning(self, "Hiba", "A név mező kitöltése kötelező!")
            self.name_edit.setFocus()
            return

        super().accept()


class InvoiceFormDialog(QDialog):
    """Invoice creation/editing dialog"""

    def __init__(self, invoice_data=None, parent=None):
        super().__init__(parent)
        self.invoice_data = invoice_data
        title = "🧾 Számla" + (
            " szerkesztése" if invoice_data else " létrehozása"
        )
        self.setWindowTitle(title)
        self.setup_ui()
        if invoice_data:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.number_edit = QLineEdit()
        form.addRow("📋 Számlaszám:", self.number_edit)

        self.partner_combo = QComboBox()
        self.load_partners()
        form.addRow("👤 Partner:", self.partner_combo)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def load_partners(self):
        try:
            with get_db() as conn:
                rows = conn.execute(
                    "SELECT id, name FROM partner ORDER BY name"
                ).fetchall()
                for row in rows:
                    self.partner_combo.addItem(row["name"], row["id"])
        except sqlite3.Error:
            logging.exception("Failed to load partners")
            QMessageBox.warning(
                self,
                "Hiba",
                "Nem sikerült betölteni a partnereket.",
            )
            self.partner_combo.clear()

    def load_data(self):
        self.number_edit.setText(self.invoice_data.get("number", ""))
        partner_id = self.invoice_data.get("partner_id")
        if partner_id is not None:
            index = self.partner_combo.findData(partner_id)
            if index >= 0:
                self.partner_combo.setCurrentIndex(index)

    def get_data(self):
        return {
            "number": self.number_edit.text().strip(),
            "direction": "sale",
            "partner_id": self.partner_combo.currentData(),
        }

    def accept(self):
        data = self.get_data()
        if not data["number"]:
            QMessageBox.warning(self, "Hiba", "Kérem adja meg a számlaszámot!")
            return
        if not data["partner_id"]:
            QMessageBox.warning(self, "Hiba", "Kérem válasszon partnert!")
            return
        super().accept()


class ProductFormDialog(QDialog):
    """Product management dialog"""

    def __init__(self, product_data=None, parent=None):
        super().__init__(parent)
        self.product_data = product_data
        title = "🛍️ Termék" + (
            " szerkesztése" if product_data else " hozzáadása"
        )
        self.setWindowTitle(title)
        self.setup_ui()
        if product_data:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.sku_edit = QLineEdit()
        form.addRow("📋 SKU:", self.sku_edit)

        self.name_edit = QLineEdit()
        form.addRow("🏷️ Név:", self.name_edit)

        self.price_edit = QLineEdit()
        form.addRow("💰 Ár (HUF):", self.price_edit)

        self.vat_spin = QSpinBox()
        self.vat_spin.setRange(0, 50)
        form.addRow("📊 ÁFA (%):", self.vat_spin)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def load_data(self):
        self.sku_edit.setText(self.product_data.get("sku", ""))
        self.name_edit.setText(self.product_data.get("name", ""))
        price_cents = self.product_data.get("unit_price_cents", 0)
        self.price_edit.setText(str(price_cents // 100))
        self.vat_spin.setValue(self.product_data.get("vat_rate", 27))

    def get_data(self):
        try:
            price_cents = int(float(self.price_edit.text()) * 100)
        except ValueError:
            price_cents = 0
        return {
            "sku": self.sku_edit.text().strip(),
            "name": self.name_edit.text().strip(),
            "unit_price_cents": price_cents,
            "vat_rate": self.vat_spin.value(),
        }

    def accept(self):
        data = self.get_data()
        if not data["sku"]:
            QMessageBox.warning(self, "Hiba", "A SKU mező kitöltése kötelező!")
            return
        if not data["name"]:
            QMessageBox.warning(self, "Hiba", "A név mező kitöltése kötelező!")
            return
        if data["unit_price_cents"] <= 0:
            QMessageBox.warning(
                self, "Hiba", "Az ár nagyobb kell legyen nullánál!"
            )
            return
        super().accept()
