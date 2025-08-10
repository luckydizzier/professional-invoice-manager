# Professional Invoice Manager v2.1.0

A comprehensive, professional-grade invoice management system built with PyQt5 and SQLite. Designed for small to medium businesses requiring robust invoice processing, customer management, and financial tracking.

## ✨ Key Features

### 🧾 Invoice Management
- **Professional Invoice Creation** - Generate detailed invoices with automatic numbering
- **VAT Calculations** - Comprehensive tax handling with multiple rates (0%, 18%, 27%)
- **Invoice Status Tracking** - Draft, pending, paid, cancelled states
- **PDF Generation Ready** - Export invoices to professional PDF format
- **Invoice Templates** - Customizable invoice layouts and branding

### 🏢 Business Management
- **Customer Database** - Complete customer information with billing/shipping addresses
- **Supplier Management** - Track suppliers with contact details and terms
- **Product Catalog** - Comprehensive product database with pricing and categories
- **Inventory Tracking** - Monitor stock levels and product availability

### 💻 User Experience
- **Professional UI** - Modern, intuitive interface with consistent styling
- **Keyboard Navigation** - Complete keyboard shortcuts for power users
- **Responsive Design** - Optimized layouts for different screen sizes
- **Multi-Language Ready** - Infrastructure prepared for internationalization

### 🔒 Data & Security
- **SQLite Database** - Reliable, file-based database with ACID compliance
- **Data Backup** - Built-in backup and restore functionality
- **Data Validation** - Comprehensive input validation and error handling
- **Referential Integrity** - Foreign key constraints ensure data consistency

## 🚀 Quick Start

### Option 1: Download Executable (Recommended)
1. Go to [Releases](https://github.com/luckydizzier/professional-invoice-manager/releases)
2. Download the appropriate package for your operating system:
   - **Windows**: `InvoiceManager-Windows-x64.zip`
   - **Linux**: `InvoiceManager-Linux-x64.tar.gz`
   - **macOS**: `InvoiceManager-macOS-x64.tar.gz`
3. Extract and run the executable

### Option 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/luckydizzier/professional-invoice-manager.git
cd professional-invoice-manager

# Install Python dependencies
pip install -r requirements.txt

# Launch the application
python launch_app.py
```

### Option 3: Easy Launch Scripts
- **Windows**: Double-click `start_invoice_manager.bat`
- **Linux/macOS**: Run `./start_invoice_manager.sh`

## 📋 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Operating System** | Windows 7+ / Ubuntu 16.04+ / macOS 10.12+ | Windows 10+ / Ubuntu 20.04+ / macOS 11+ |
| **Python** | 3.7+ | 3.9+ |
| **RAM** | 512MB | 2GB |
| **Storage** | 100MB | 500MB |
| **Display** | 1024x768 | 1920x1080 |

## 🎯 Target Users

- **Small Business Owners** - Complete invoice and customer management
- **Freelancers** - Professional invoicing with minimal setup
- **Accountants** - VAT calculations and financial tracking
- **Developers** - Clean codebase for customization and extension

## 🏗️ Architecture

```
Professional Invoice Manager
├── 📱 PyQt5 Frontend (GUI)
├── 🗄️ SQLite Database (Data)
├── 🔧 Business Logic (Core)
├── 🎨 Style Management (CSS)
└── 📋 Configuration (JSON)
```

### Core Components
- **`main_with_management.py`** - Main application with complete functionality
- **`launch_app.py`** - Application launcher with dependency checking
- **`config.py`** - Configuration management and database setup
- **`style_manager.py`** - CSS styling and theme management
- **`forms.py`** - Custom form widgets and validation

## 📊 Database Schema

The application uses a normalized SQLite database with four core tables:

```sql
Customers ← Invoices → Products
              ↓
         Invoice Items
```

### Table Structure
- **customers** - Customer information and addresses
- **products** - Product catalog with pricing
- **invoices** - Invoice headers with totals
- **invoice_items** - Line items with quantities and pricing

## 🎹 Keyboard Navigation

The application features complete keyboard navigation for power users:

| Key | Function | Context |
|-----|----------|---------|
| `F1` | Help | Global |
| `F2` | Invoices | Global |
| `F3` | Products | Global |
| `F4` | Customers | Global |
| `F5` | Refresh | Lists |
| `F6` | Suppliers | Global |
| `Enter` | Edit/Open | Lists |
| `Insert` | New Item | Lists |
| `Delete` | Delete Item | Lists |
| `Escape` | Back/Cancel | Forms |
| `Alt + ←→` | Menu Navigation | Global |

## 🔧 Development

### Project Structure
```
professional-invoice-manager/
├── 📁 docs/                    # Documentation
├── 📁 tests/                   # Unit tests
├── 📁 styles/                  # CSS stylesheets
├── 📁 .github/                 # GitHub workflows
├── 🐍 main_with_management.py  # Main application
├── 🚀 launch_app.py           # Application launcher
├── ⚙️ config.py               # Configuration
├── 🎨 style_manager.py        # Style management
├── 📋 forms.py                # Custom widgets
└── 📦 requirements.txt        # Dependencies
```

### Setting up Development Environment
```bash
# Clone and setup
git clone https://github.com/luckydizzier/professional-invoice-manager.git
cd professional-invoice-manager

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run with development options
python launch_app.py --debug
```

### Building Executables
```bash
# Build for current platform
python build_release.py

# Output will be in dist/ directory
```

## 📖 Documentation

- **[User Guide](docs/user-guide.md)** - Complete user manual
- **[Technical Specification](docs/technical-specification.md)** - Detailed technical docs
- **[Installation Guide](docs/installation-guide.md)** - Setup instructions
- **[Porting Guide](docs/porting-guide.md)** - Guide for other languages
- **[API Documentation](docs/api-documentation.md)** - Code reference
- **[VAT Implementation](docs/vat-summary-implementation.md)** - Tax calculations
- **[Development Guide](docs/development-guide.md)** - Contributing guidelines

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ways to Contribute
- 🐛 **Bug Reports** - Report issues and bugs
- 💡 **Feature Requests** - Suggest new features
- 🔧 **Code Contributions** - Submit pull requests
- 📖 **Documentation** - Improve docs and guides
- 🌍 **Translations** - Add language support
- 🧪 **Testing** - Add tests and improve coverage

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Repository**: https://github.com/luckydizzier/professional-invoice-manager
- **Issues**: https://github.com/luckydizzier/professional-invoice-manager/issues
- **Releases**: https://github.com/luckydizzier/professional-invoice-manager/releases
- **Documentation**: https://github.com/luckydizzier/professional-invoice-manager/tree/main/docs

## 🙏 Acknowledgments

- PyQt5 team for the excellent GUI framework
- SQLite team for the reliable database engine
- Contributors and users for feedback and improvements

## 📊 Project Stats

![GitHub release (latest by date)](https://img.shields.io/github/v/release/luckydizzier/professional-invoice-manager)
![GitHub](https://img.shields.io/github/license/luckydizzier/professional-invoice-manager)
![GitHub top language](https://img.shields.io/github/languages/top/luckydizzier/professional-invoice-manager)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/luckydizzier/professional-invoice-manager)
![GitHub issues](https://img.shields.io/github/issues/luckydizzier/professional-invoice-manager)
![GitHub pull requests](https://img.shields.io/github/issues-pr/luckydizzier/professional-invoice-manager)

---

<div align="center">

**Professional Invoice Manager v2.1.0**  
*Making business invoicing simple and professional*

[Download](https://github.com/luckydizzier/professional-invoice-manager/releases) • [Documentation](docs/) • [Issues](https://github.com/luckydizzier/professional-invoice-manager/issues) • [Contributing](CONTRIBUTING.md)

</div>
