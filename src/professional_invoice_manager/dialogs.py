"""Dialog classes for user interactions."""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QDialogButtonBox,
    QMessageBox,
)


class PartnerFormDialog(QDialog):
    """Partner (customer/supplier) management dialog."""

    def __init__(
        self, partner_data=None, partner_type="customer", parent=None
    ):
        super().__init__(parent)
        self.partner_data = partner_data
        self.partner_type = partner_type

        type_text = "Vevő" if partner_type == "customer" else "Beszállító"
        self.setWindowTitle(
            "👤 "
            + type_text
            + (" szerkesztése" if partner_data else " hozzáadása")
        )
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
