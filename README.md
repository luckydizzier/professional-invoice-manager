# Professional Invoice Manager

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-green)](https://pypi.org/project/PyQt5/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive desktop invoice management system with full keyboard navigation, professional UI, and advanced VAT calculations. Built with Python and PyQt5 for small to medium business operations.

![Application Screenshot](https://via.placeholder.com/800x600/3b82f6/ffffff?text=Professional+Invoice+Manager)

## ✨ Key Features

### 📋 Business Management
- **📄 Invoice Management**: Complete CRUD operations with VAT calculations
- **🛍️ Product Catalog**: SKU-based inventory with pricing management  
- **👥 Customer Management**: Contact information and relationship tracking
- **🏭 Supplier Management**: Vendor database with purchase integration

### 🎹 Professional Interface
- **Complete keyboard navigation** - No mouse required!
- **F-key shortcuts** for instant page switching
- **Professional styling** with modern CSS design
- **Real-time validation** and error feedback

### 💰 Advanced Calculations
- **Multi-rate VAT support** (5%, 18%, 27%)
- **Detailed VAT breakdown** by rate
- **Currency precision** with cent-based calculations
- **Professional invoicing** with automated totals
- **Context-sensitive operations** (Enter/Delete/Insert)

## 🎹 Keyboard Shortcuts

### Navigation
- **F1** - Show help and shortcuts
- **F2** - Invoices list
- **F3** - Products management 
- **F4** - Customers management
- **F5** - Refresh current list
- **F6** - Suppliers management
- **Escape** - Go back or clear selection

### Operations
- **Enter** - Edit selected item
- **Delete** - Delete selected item  
- **Insert** - Add new item
- **↑↓** - Navigate in lists

### Quick Actions
- **Ctrl+N** - New invoice
- **Ctrl+Shift+P** - New product
- **Ctrl+Shift+C** - New customer
- **Ctrl+Shift+S** - New supplier
- **Ctrl+Q** - Exit application

### Menu Navigation
- **Alt + ←→** - Navigate between menus
- **Alt + letter** - Activate menu by underlined letter

## 📁 Project Structure

- `main_with_management.py` - Full application with management features
- `launch_app.py` - Application launcher with error handling
- `test_management.py` - Comprehensive feature testing
- `config.py` - Configuration management
- `style_manager.py` - CSS style management
- `forms.py` - Dialog forms
- `styles/` - CSS stylesheets
- `backup/` - Old/deprecated files
- `invoice_qt5.db` - SQLite database

## 📦 Management Features

### Invoice Management (F2)
- Create new invoices with form-based dialog
- Edit existing invoice details
- Delete invoices with confirmation
- Partner selection (customers/suppliers)
- Invoice direction (incoming/outgoing)
- Automatic timestamp tracking
- Real-time status updates

### Product Management (F3)
- Add products with SKU, name, price (HUF), VAT rate
- Edit existing product information
- Delete products with confirmation
- Price conversion (HUF ↔ cents)
- VAT rate configuration (0-50%)

### Customer Management (F4)
- Customer contact information
- Tax ID and address management
- Full CRUD operations
- Search and filtering

### Supplier Management (F6)
- Supplier database management
- Contact information storage
- Integration with purchase workflows
- Relationship tracking

## 🗄️ Database Schema

```sql
-- Products
CREATE TABLE product (
    id INTEGER PRIMARY KEY,
    sku TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    unit_price_cents INTEGER NOT NULL,
    vat_rate INTEGER NOT NULL DEFAULT 27
);

-- Partners (customers and suppliers)
CREATE TABLE partner (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT CHECK(kind IN ('customer','supplier')),
    tax_id TEXT,
    address TEXT
);

-- Invoices
CREATE TABLE invoice (
    id INTEGER PRIMARY KEY,
    number TEXT NOT NULL UNIQUE,
    partner_id INTEGER REFERENCES partner(id),
    direction TEXT CHECK(direction IN ('sale','purchase')),
    created_utc INTEGER NOT NULL,
    notes TEXT
);
```

## 🧭 Menu System

```
📁 Fájl (File)
├── 🔄 Frissítés (Refresh)
├── ➕ Új (New)
│   ├── 📄 Új számla (New Invoice)
│   ├── 🛍️ Új termék (New Product)
│   ├── 👥 Új vevő (New Customer)
│   └── 🏭 Új beszállító (New Supplier)
└── 🚪 Kilépés (Exit)

👁️ Nézet (View)
├── 📄 Számlák (Invoices)
├── 🛍️ Termékek (Products)
├── 👥 Vevők (Customers)
└── 🏭 Beszállítók (Suppliers)

🔧 Kezelés (Management)
├── 🛍️ Termékek kezelése
├── 👥 Vevők kezelése
└── 🏭 Beszállítók kezelése

❓ Súgó (Help)
├── 🎹 Billentyűparancsok
└── ℹ️ Névjegy
```

## 📋 Requirements

- Python 3.7+
- PyQt5
- SQLite (included with Python)

## 🔧 Technical Features

- **Professional UI** with modern styling
- **SQLite database** with foreign key constraints
- **WAL mode** for better performance
- **Form validation** with user-friendly errors
- **Event-driven architecture** with proper signal handling
- **Modular design** with separation of concerns

## 🐛 Troubleshooting

**Application won't start:**
```bash
pip install PyQt5
python test_management.py
```

**Need help with shortcuts:**
- Press `F1` in the application for complete help
- All features are accessible via keyboard

## 📝 Version History

### v2.1.0 - Management Edition
- ✅ Complete product management system
- ✅ Customer and supplier management
- ✅ Enhanced keyboard navigation with F-keys
- ✅ Menu navigation with arrow keys
- ✅ Professional form dialogs with validation
- ✅ Comprehensive help system

### v2.0.0 - Professional Edition  
- ✅ Complete keyboard navigation
- ✅ Professional CSS styling
- ✅ Fixed database schema
- ✅ Enhanced error handling

---

**💡 Pro Tip**: Use `F1` at any time to see all available keyboard shortcuts!


## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚀 Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/professional-invoice-manager.git
   cd professional-invoice-manager
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python launch_app.py
   ```

## 📁 Project Structure

```
├── main_with_management.py    # Main application
├── launch_app.py              # Application launcher  
├── config.py                  # Configuration management
├── style_manager.py           # CSS styling system
├── forms.py                   # Form dialogs
├── styles/                    # CSS stylesheets
├── docs/                      # Documentation
├── tests/                     # Test files
├── archive/                   # Development history
└── README.md                  # This file
```

## 🔧 Development

See the [Technical Specification](docs/technical-specification.md) for detailed architecture information and the [Porting Guide](docs/porting-guide.md) for implementation in other languages.
