#!/usr/bin/env python3
"""
Project Cleanup Script
Organizes and cleans up the invoice manager project
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Clean up and organize the project"""
    project_root = Path(__file__).parent
    
    print("🧹 Starting project cleanup...")
    print(f"📁 Project root: {project_root}")
    
    # Create backup directory for old files
    backup_dir = project_root / "backup"
    backup_dir.mkdir(exist_ok=True)
    
    # Files to keep in main directory
    keep_files = {
        "main_clean.py",  # Main working application
        "launch_app.py",  # Application launcher
        "config.py",      # Configuration management
        "style_manager.py", # Style management
        "forms.py",       # Form dialogs
        "config.json",    # Configuration file
        "invoice_qt5.db", # Main database
    }
    
    # Files to move to backup
    backup_files = {
        "main.py",
        "main_fixed.py", 
        "main_professional.py",
        "main_refactored.py",
        "main_simple.py",
        "main_working.py",
        "run_app.py",
        "qt_constants.py",
        "test_app.py",
        "test_basic.py", 
        "test_date.py",
        "test_fixes.py",
        "test_status_fix.py",
        "test_styling.py",
        "invoice.db",
        "invoiceref.db", 
        "invoices.db",
    }
    
    # Move files to backup
    for file_name in backup_files:
        file_path = project_root / file_name
        if file_path.exists():
            backup_path = backup_dir / file_name
            try:
                shutil.move(str(file_path), str(backup_path))
                print(f"📦 Moved {file_name} to backup/")
            except Exception as e:
                print(f"⚠️ Could not move {file_name}: {e}")
    
    # Clean up __pycache__ directories
    pycache_dirs = list(project_root.rglob("__pycache__"))
    for pycache_dir in pycache_dirs:
        try:
            shutil.rmtree(pycache_dir)
            print(f"🗑️ Removed {pycache_dir}")
        except Exception as e:
            print(f"⚠️ Could not remove {pycache_dir}: {e}")
    
    # Create a simple README
    readme_content = """# Professional Invoice Manager v2.1

## 🚀 Quick Start

```bash
python launch_app.py
```

## 🎹 Keyboard Shortcuts

- **F5** - Refresh list
- **Enter** - Edit selected invoice
- **Delete** - Delete selected invoice
- **Insert** - New invoice
- **Escape** - Clear selection
- **F1** - Show help
- **Ctrl+Q** - Exit

## 📁 Project Structure

- `main_clean.py` - Main application (clean, working version)
- `launch_app.py` - Application launcher with error handling
- `config.py` - Configuration management
- `style_manager.py` - CSS style management
- `forms.py` - Dialog forms
- `styles/` - CSS stylesheets
- `backup/` - Old/deprecated files

## 🔧 Features

- Professional UI with keyboard navigation
- SQLite database for data storage
- Configurable settings
- CSS-based styling
- Error handling and logging

## 📋 Requirements

- Python 3.7+
- PyQt5
- SQLite (included with Python)

## 🐛 Known Issues

Fixed in v2.1:
- Qt constants import issues
- Status bar initialization
- Event filter handling
- Table widget flag setting

## 📝 Version History

- v2.1 - Clean working version with fixed Qt constants
- v2.0 - Enhanced version with keyboard navigation
- v1.0 - Initial version
"""
    
    readme_path = project_root / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("📝 Created README.md")
    
    # Update the main application to be the entry point
    main_link = project_root / "main.py"
    if not main_link.exists():
        try:
            # Create a symlink or copy for easy access
            shutil.copy(project_root / "main_clean.py", main_link)
            print("🔗 Created main.py -> main_clean.py")
        except Exception as e:
            print(f"⚠️ Could not create main.py link: {e}")
    
    print("\n✅ Project cleanup completed!")
    print("\n📁 Current project structure:")
    
    # Show final structure
    for item in sorted(project_root.iterdir()):
        if item.name.startswith('.'):
            continue
        if item.is_dir():
            print(f"  📁 {item.name}/")
        else:
            print(f"  📄 {item.name}")
    
    print(f"\n📦 Backed up {len(backup_files)} files to backup/")
    print("🚀 Ready to run: python launch_app.py")

if __name__ == "__main__":
    cleanup_project()
