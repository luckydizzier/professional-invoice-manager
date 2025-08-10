"""
Form dialogs for data management
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, 
    QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPushButton, 
    QDialogButtonBox, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt
from typing import Dict, Optional, Any, List


class BaseFormDialog(QDialog):
    """Base class for form dialogs"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setObjectName("formDialog")
        self.setMinimumWidth(400)
        
        self.fields = {}
        self.errors = {}
        
        self.setup_ui()
        self.setup_layout()
    
    def setup_ui(self):
        """Setup the UI elements"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(16)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        self.header_label = QLabel(self.windowTitle())
        self.header_label.setObjectName("formHeader")
        self.main_layout.addWidget(self.header_label)
        
        # Form layout
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(12)
        self.main_layout.addLayout(self.form_layout)
        
        # Button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept_form)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)
    
    def setup_layout(self):
        """Override in subclasses to add form fields"""
        pass
    
    def add_field(self, name: str, label: str, widget, required: bool = False, 
                  validator=None, error_label: str = None):
        """Add a field to the form"""
        field_label = QLabel(label + ("*" if required else ""))
        field_label.setObjectName("fieldLabel")
        
        if error_label:
            error_widget = QLabel(error_label)
            error_widget.setObjectName("errorLabel")
            error_widget.hide()
            self.errors[name] = error_widget
        
        self.fields[name] = {
            'widget': widget,
            'required': required,
            'validator': validator,
            'error': self.errors.get(name)
        }
        
        self.form_layout.addRow(field_label, widget)
        if error_label:
            self.form_layout.addRow("", self.errors[name])
    
    def get_field_value(self, name: str) -> Any:
        """Get the value of a field"""
        if name not in self.fields:
            return None
        
        widget = self.fields[name]['widget']
        
        if isinstance(widget, QLineEdit):
            return widget.text().strip()
        elif isinstance(widget, QTextEdit):
            return widget.toPlainText().strip()
        elif isinstance(widget, QComboBox):
            return widget.currentData() or widget.currentText()
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            return widget.value()
        elif isinstance(widget, QCheckBox):
            return widget.isChecked()
        
        return None
    
    def set_field_value(self, name: str, value: Any) -> None:
        """Set the value of a field"""
        if name not in self.fields:
            return
        
        widget = self.fields[name]['widget']
        
        if isinstance(widget, QLineEdit):
            widget.setText(str(value) if value is not None else "")
        elif isinstance(widget, QTextEdit):
            widget.setPlainText(str(value) if value is not None else "")
        elif isinstance(widget, QComboBox):
            index = widget.findData(value)
            if index >= 0:
                widget.setCurrentIndex(index)
            else:
                widget.setCurrentText(str(value) if value is not None else "")
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            widget.setValue(value if value is not None else 0)
        elif isinstance(widget, QCheckBox):
            widget.setChecked(bool(value))
    
    def validate_form(self) -> bool:
        """Validate all form fields"""
        valid = True
        
        for name, field in self.fields.items():
            error_widget = field.get('error')
            if error_widget:
                error_widget.hide()
            
            value = self.get_field_value(name)
            
            # Check required fields
            if field['required'] and not value:
                if error_widget:
                    error_widget.setText(f"Ez a mező kötelező")
                    error_widget.show()
                valid = False
                continue
            
            # Run custom validator
            if field['validator'] and value:
                error_msg = field['validator'](value)
                if error_msg and error_widget:
                    error_widget.setText(error_msg)
                    error_widget.show()
                    valid = False
        
        return valid
    
    def accept_form(self):
        """Validate and accept the form"""
        if self.validate_form():
            self.accept()
    
    def get_form_data(self) -> Dict[str, Any]:
        """Get all form data as a dictionary"""
        return {name: self.get_field_value(name) for name in self.fields.keys()}
    
    def set_form_data(self, data: Dict[str, Any]) -> None:
        """Set form data from a dictionary"""
        for name, value in data.items():
            self.set_field_value(name, value)


class ProductFormDialog(BaseFormDialog):
    """Dialog for adding/editing products"""
    
    def __init__(self, product_data: Optional[Dict] = None, parent=None):
        self.product_data = product_data
        title = "Termék Szerkesztése" if product_data else "Új Termék"
        super().__init__(title, parent)
        
        if product_data:
            self.set_form_data(product_data)
    
    def setup_layout(self):
        """Setup product form fields"""
        # SKU
        sku_edit = QLineEdit()
        sku_edit.setPlaceholderText("pl. SKU001")
        self.add_field("sku", "Termék kód (SKU)", sku_edit, 
                      required=True, validator=self.validate_sku,
                      error_label="")
        
        # Name
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("pl. Kenyér 1kg")
        self.add_field("name", "Megnevezés", name_edit, 
                      required=True, error_label="")
        
        # Unit price
        price_spin = QDoubleSpinBox()
        price_spin.setRange(0.01, 999999.99)
        price_spin.setDecimals(2)
        price_spin.setSuffix(" Ft")
        price_spin.setValue(100.00)
        self.add_field("unit_price", "Egységár", price_spin, 
                      required=True, error_label="")
        
        # VAT rate
        vat_combo = QComboBox()
        vat_combo.addItems(["5%", "18%", "27%"])
        vat_combo.setCurrentText("27%")
        self.add_field("vat_rate", "ÁFA kulcs", vat_combo, 
                      required=True, error_label="")
    
    def validate_sku(self, sku: str) -> Optional[str]:
        """Validate SKU format"""
        if len(sku) < 3:
            return "A termék kód legalább 3 karakter hosszú legyen"
        if not sku.replace("-", "").replace("_", "").isalnum():
            return "A termék kód csak betűket, számokat, kötőjelet és aláhúzást tartalmazhat"
        return None
    
    def get_form_data(self) -> Dict[str, Any]:
        """Get product data with proper formatting"""
        data = super().get_form_data()
        
        # Convert price to cents
        if 'unit_price' in data:
            data['unit_price_cents'] = int(data['unit_price'] * 100)
            del data['unit_price']
        
        # Extract VAT rate number
        if 'vat_rate' in data:
            vat_text = data['vat_rate']
            data['vat_rate'] = int(vat_text.replace('%', ''))
        
        return data


class PartnerFormDialog(BaseFormDialog):
    """Dialog for adding/editing partners (customers/suppliers)"""
    
    def __init__(self, partner_data: Optional[Dict] = None, partner_kind: str = "customer", parent=None):
        self.partner_data = partner_data
        self.partner_kind = partner_kind
        
        kind_text = "Vevő" if partner_kind == "customer" else "Szállító"
        title = f"{kind_text} Szerkesztése" if partner_data else f"Új {kind_text}"
        super().__init__(title, parent)
        
        if partner_data:
            self.set_form_data(partner_data)
    
    def setup_layout(self):
        """Setup partner form fields"""
        # Name
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Cég vagy személy neve")
        self.add_field("name", "Név", name_edit, 
                      required=True, error_label="")
        
        # Tax ID
        tax_id_edit = QLineEdit()
        tax_id_edit.setPlaceholderText("12345678-1-42")
        self.add_field("tax_id", "Adószám", tax_id_edit, 
                      validator=self.validate_tax_id, error_label="")
        
        # Address
        address_edit = QTextEdit()
        address_edit.setPlaceholderText("Teljes cím")
        address_edit.setMaximumHeight(80)
        self.add_field("address", "Cím", address_edit, error_label="")
        
        # Kind (hidden, set automatically)
        self.fields["kind"] = {
            'widget': None,
            'required': False,
            'validator': None,
            'error': None
        }
    
    def validate_tax_id(self, tax_id: str) -> Optional[str]:
        """Validate Hungarian tax ID format"""
        if not tax_id:
            return None  # Optional field
        
        # Remove spaces and hyphens
        clean_tax_id = tax_id.replace(" ", "").replace("-", "")
        
        if len(clean_tax_id) != 10:
            return "Az adószám 10 számjegyből áll"
        
        if not clean_tax_id.isdigit():
            return "Az adószám csak számokat tartalmazhat"
        
        return None
    
    def get_form_data(self) -> Dict[str, Any]:
        """Get partner data with kind included"""
        data = super().get_form_data()
        data['kind'] = self.partner_kind
        return data


class SettingsDialog(BaseFormDialog):
    """Dialog for application settings"""
    
    def __init__(self, config_data: Dict, parent=None):
        self.config_data = config_data
        super().__init__("Beállítások", parent)
        self.setMinimumSize(500, 400)
        self.set_form_data(config_data)
    
    def setup_layout(self):
        """Setup settings form fields"""
        # Company info
        company_name_edit = QLineEdit()
        self.add_field("company_name", "Cég neve", company_name_edit)
        
        company_address_edit = QTextEdit()
        company_address_edit.setMaximumHeight(60)
        self.add_field("company_address", "Cég címe", company_address_edit)
        
        company_tax_id_edit = QLineEdit()
        self.add_field("company_tax_id", "Cég adószáma", company_tax_id_edit)
        
        # Database settings
        db_path_edit = QLineEdit()
        self.add_field("db_path", "Adatbázis útvonal", db_path_edit, required=True)
        
        # UI settings
        confirm_deletions_check = QCheckBox()
        self.add_field("confirm_deletions", "Törlés megerősítése", confirm_deletions_check)
        
        show_tooltips_check = QCheckBox()
        self.add_field("show_tooltips", "Súgó buborékok", show_tooltips_check)
