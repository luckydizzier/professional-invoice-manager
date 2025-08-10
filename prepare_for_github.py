#!/usr/bin/env python3
"""
Project Cleanup Script for GitHub Publication
Organizes the invoice manager project for public release
"""

import shutil
from pathlib import Path
import json

def cleanup_for_github():
    """Clean up and organize the project for GitHub publication"""
    project_root = Path(__file__).parent
    
    print("🧹 Starting GitHub preparation cleanup...")
    print(f"📁 Project root: {project_root}")
    
    # Create directories for organization
    docs_dir = project_root / "docs"
    tests_dir = project_root / "tests"
    archive_dir = project_root / "archive"
    
    docs_dir.mkdir(exist_ok=True)
    tests_dir.mkdir(exist_ok=True)
    archive_dir.mkdir(exist_ok=True)
    
    # Documentation files to move to docs/
    docs_files = {
        "TECHNICAL_SPECIFICATION.md": "technical-specification.md",
        "PORTING_GUIDE.md": "porting-guide.md",
        "VAT_SUMMARY_IMPLEMENTATION.md": "vat-summary-implementation.md",
        "IMPLEMENTATION_SUMMARY.md": "implementation-summary.md",
        "DATABASE_DESCRIPTION_FIX.md": "database-fixes.md",
        "DATABASE_FIX_SUMMARY.md": "database-fixes-summary.md",
        "INVOICE_EDIT_FIX.md": "invoice-edit-fixes.md",
    }
    
    # Test files to move to tests/
    test_files = {
        "test_management.py": "test_management.py",
        "test_complete_implementation.py": "test_implementation.py",
        "test_vat_summary.py": "test_vat_features.py",
        "test_app_vat.py": "test_vat_integration.py",
    }
    
    # Files to archive (development artifacts)
    archive_files = {
        "main.py", "main_clean.py", "main_fixed.py", "main_professional.py",
        "main_refactored.py", "main_simple.py", "main_working.py",
        "run_app.py", "qt_constants.py",
        "test_app.py", "test_basic.py", "test_date.py", "test_db_fix.py",
        "test_fixes.py", "test_invoice_edit.py", "test_invoice_edit_complete.py",
        "test_item_loading.py", "test_schema.py", "test_status_fix.py",
        "test_styling.py", "final_test.py", "fix_complete.py",
        "fix_db_schema.py", "vat_summary_complete.py", "cleanup_project.py"
    }
    
    # Move documentation files
    print("\n📚 Moving documentation files...")
    for old_name, new_name in docs_files.items():
        old_path = project_root / old_name
        new_path = docs_dir / new_name
        if old_path.exists():
            shutil.move(str(old_path), str(new_path))
            print(f"  ✅ {old_name} → docs/{new_name}")
    
    # Move test files
    print("\n🧪 Moving test files...")
    for old_name, new_name in test_files.items():
        old_path = project_root / old_name
        new_path = tests_dir / new_name
        if old_path.exists():
            shutil.move(str(old_path), str(new_path))
            print(f"  ✅ {old_name} → tests/{new_name}")
    
    # Archive development files
    print("\n📦 Archiving development files...")
    for filename in archive_files:
        old_path = project_root / filename
        new_path = archive_dir / filename
        if old_path.exists():
            shutil.move(str(old_path), str(new_path))
            print(f"  📦 {filename} → archive/{filename}")
    
    # Move backup directory to archive
    backup_dir = project_root / "backup"
    if backup_dir.exists():
        archive_backup = archive_dir / "backup"
        shutil.move(str(backup_dir), str(archive_backup))
        print(f"  📦 backup/ → archive/backup/")
    
    # Clean up Python cache
    pycache_dir = project_root / "__pycache__"
    if pycache_dir.exists():
        shutil.rmtree(pycache_dir)
        print(f"  🗑️ Removed __pycache__/")
    
    # Create requirements.txt if it doesn't exist
    requirements_file = project_root / "requirements.txt"
    if not requirements_file.exists():
        create_requirements_file(requirements_file)
    
    # Create .gitignore if it doesn't exist
    gitignore_file = project_root / ".gitignore"
    if not gitignore_file.exists():
        create_gitignore_file(gitignore_file)
    
    # Create LICENSE file if it doesn't exist
    license_file = project_root / "LICENSE"
    if not license_file.exists():
        create_license_file(license_file)
    
    # Update README.md for GitHub
    update_readme_for_github(project_root / "README.md")
    
    # Clean up config.json for public release
    clean_config_for_release(project_root / "config.json")
    
    print("\n🎉 GitHub preparation complete!")
    print("\n📁 Final project structure:")
    print("├── main_with_management.py    # Main application")
    print("├── launch_app.py              # Application launcher")
    print("├── config.py                  # Configuration management")
    print("├── style_manager.py           # CSS styling")
    print("├── forms.py                   # Form dialogs")
    print("├── styles/                    # CSS stylesheets")
    print("├── docs/                      # Documentation")
    print("├── tests/                     # Test files")
    print("├── archive/                   # Development artifacts")
    print("├── README.md                  # Project documentation")
    print("├── requirements.txt           # Python dependencies")
    print("├── .gitignore                 # Git ignore rules")
    print("└── LICENSE                    # License file")
    
    return True

def create_requirements_file(filepath):
    """Create requirements.txt file"""
    requirements = """# Professional Invoice Manager Requirements
PyQt5>=5.15.0
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(requirements)
    print(f"  ✅ Created {filepath.name}")

def create_gitignore_file(filepath):
    """Create .gitignore file"""
    gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
*.db-journal
*.db-wal
*.db-shm
config_local.json
exports/
backups/
logs/

# Temporary files
*.tmp
*.temp
*.log
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    print(f"  ✅ Created {filepath.name}")

def create_license_file(filepath):
    """Create MIT License file"""
    license_content = """MIT License

Copyright (c) 2025 Professional Invoice Manager

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(license_content)
    print(f"  ✅ Created {filepath.name}")

def update_readme_for_github(filepath):
    """Update README.md for GitHub publication"""
    if filepath.exists():
        # Read current README
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add GitHub-specific sections if not present
        github_additions = """

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
"""
        
        # Only add if not already present
        if "## 🤝 Contributing" not in content:
            content += github_additions
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Updated README.md for GitHub")

def clean_config_for_release(filepath):
    """Clean config.json for public release"""
    if filepath.exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Clean sensitive data
            if 'business' in config_data:
                config_data['business']['company_name'] = ""
                config_data['business']['company_address'] = ""
                config_data['business']['company_tax_id'] = ""
            
            # Set default values
            if 'database' in config_data:
                config_data['database']['path'] = "invoice_qt5.db"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            print(f"  ✅ Cleaned config.json for public release")
            
        except Exception as e:
            print(f"  ⚠️ Could not clean config.json: {e}")

if __name__ == "__main__":
    cleanup_for_github()
