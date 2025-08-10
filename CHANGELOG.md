# Changelog

All notable changes to the Professional Invoice Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-08-11

### Added
- **Complete Product Management System**: Full CRUD operations for products with SKU, pricing, and VAT rate management
- **Customer and Supplier Management**: Comprehensive partner management with contact information and tax ID tracking
- **Enhanced Keyboard Navigation**: F-key shortcuts for instant page switching and complete keyboard control
- **Professional Form Dialogs**: Modal dialogs with validation, error handling, and user feedback
- **Advanced VAT Summary System**: Detailed VAT breakdown by rate with professional table layout
- **Menu Navigation System**: Traditional menu bar with keyboard shortcuts and Alt+key access
- **Real-time Status Updates**: Status bar feedback for all operations
- **Comprehensive Help System**: F1 help with complete keyboard shortcut reference

### Enhanced
- **Database Schema**: Added description column to invoice items and improved foreign key constraints
- **Error Handling**: Multi-layer validation with user-friendly error messages and recovery suggestions
- **Professional Styling**: Modern CSS design with focus indicators and hover effects
- **Configuration Management**: External JSON configuration with business settings
- **Code Architecture**: Improved separation of concerns with repository pattern and service layer

### Fixed
- **Database Column Issues**: Resolved "No item with that key" errors in invoice item loading
- **Qt Constants**: Fixed all Qt constants import issues for better compatibility
- **Invoice Editing**: Complete invoice editing workflow with form pre-population
- **VAT Calculations**: Precise cent-based calculations with proper rounding
- **Keyboard Navigation**: Fixed all keyboard shortcuts and navigation flows

### Technical Improvements
- **Code Quality**: Comprehensive error handling and input validation
- **Testing**: Added comprehensive test suite for all major features
- **Documentation**: Complete technical specification and porting guide
- **Project Structure**: Organized codebase with clear separation of concerns

## [2.0.0] - 2024-12-01

### Added
- **Complete Invoice Management**: CRUD operations for invoices with partner selection
- **SQLite Database**: Relational database with foreign key constraints and WAL mode
- **Professional UI**: Modern desktop interface with CSS styling
- **Keyboard Navigation**: Basic keyboard shortcuts and navigation support

### Changed
- **Architecture**: Moved from simple script to professional application architecture
- **Database**: Migrated to SQLite with proper schema design
- **UI Framework**: Upgraded to PyQt5 with professional styling

## [1.0.0] - 2024-11-01

### Added
- **Initial Release**: Basic invoice management functionality
- **Simple UI**: Basic desktop interface
- **Database**: Simple file-based data storage

---

## Development Timeline

### Phase 1: Foundation (v1.0.0)
- Basic invoice management
- Simple UI interface
- File-based storage

### Phase 2: Professional Upgrade (v2.0.0)
- Professional architecture
- SQLite database
- Enhanced UI with CSS styling
- Keyboard navigation

### Phase 3: Business Features (v2.1.0)
- Complete business management
- Advanced calculations
- Professional form handling
- Comprehensive keyboard navigation

### Future Roadmap

#### v2.2.0 - Export & Reporting
- PDF invoice generation
- CSV/Excel export
- Advanced reporting features
- Backup and restore functionality

#### v2.3.0 - Integration & Automation
- Email integration
- Cloud synchronization
- Automated backups
- Advanced search and filtering

#### v3.0.0 - Enterprise Features
- Multi-user support
- Advanced permissions
- API integration
- Plugin architecture

---

## Migration Notes

### Upgrading from v2.0.x to v2.1.0
- **Database**: Automatic migration adds description column to invoice_item table
- **Configuration**: New business settings in config.json
- **UI**: Enhanced keyboard navigation may require learning new shortcuts

### Upgrading from v1.x to v2.0.0
- **Breaking Change**: Complete rewrite with new database format
- **Data Migration**: Manual data export/import required
- **Configuration**: New configuration system

---

## Support

For questions about specific versions or upgrade paths, please:
- Check the [Technical Documentation](docs/technical-specification.md)
- Review [Migration Guides](docs/database-fixes.md)
- Open an issue on GitHub with your specific version information
