#!/usr/bin/env python3
"""
Build script for creating executable distributions
"""

import subprocess
import sys
from pathlib import Path
import shutil
import os

def build_executable():
    """Build standalone executable using PyInstaller"""
    
    print("🔨 Building Professional Invoice Manager executable...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("⚠️ Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Project directory
    project_dir = Path(__file__).parent
    
    # Clean previous builds
    dist_dir = project_dir / "dist"
    build_dir = project_dir / "build"
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    print("🧹 Cleaned previous builds")
    
    # Build command
    build_args = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window (GUI app)
        "--name=InvoiceManager",        # Executable name
        "--distpath=dist",              # Output directory
        "--workpath=build",             # Build directory
        "--clean",                      # Clean cache
        # Add data files
        "--add-data=styles;styles",     # Include CSS files
        "--add-data=config.json;.",     # Include config
        # Hide imports
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=sqlite3",
        # Main script
        "launch_app.py"
    ]
    
    # Adjust for different OS
    if os.name != 'nt':  # Not Windows
        build_args[build_args.index("--add-data=styles;styles")] = "--add-data=styles:styles"
        build_args[build_args.index("--add-data=config.json;.")] = "--add-data=config.json:."
    
    print(f"🔧 Running: {' '.join(build_args)}")
    
    try:
        # Run PyInstaller
        result = subprocess.run(build_args, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        
        # Show build results
        exe_path = dist_dir / ("InvoiceManager.exe" if os.name == 'nt' else "InvoiceManager")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📦 Executable created: {exe_path}")
            print(f"📊 Size: {size_mb:.1f} MB")
            return str(exe_path)
        else:
            print("❌ Executable not found in expected location")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def create_portable_package():
    """Create a portable package with all necessary files"""
    
    print("📦 Creating portable package...")
    
    project_dir = Path(__file__).parent
    package_dir = project_dir / "dist" / "portable"
    
    # Create package directory
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy essential files
    files_to_copy = [
        "main_with_management.py",
        "launch_app.py", 
        "config.py",
        "style_manager.py",
        "forms.py",
        "config.json",
        "README.md",
        "LICENSE",
        "requirements.txt"
    ]
    
    dirs_to_copy = [
        "styles"
    ]
    
    # Copy files
    for file in files_to_copy:
        src = project_dir / file
        if src.exists():
            shutil.copy2(src, package_dir / file)
            print(f"  ✅ Copied {file}")
    
    # Copy directories
    for dir_name in dirs_to_copy:
        src = project_dir / dir_name
        dst = package_dir / dir_name
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f"  ✅ Copied {dir_name}/")
    
    # Create run script
    if os.name == 'nt':  # Windows
        run_script = package_dir / "run.bat"
        with open(run_script, 'w') as f:
            f.write("""@echo off
echo Starting Professional Invoice Manager...
python launch_app.py
if errorlevel 1 (
    echo.
    echo Error: Python or required packages not found
    echo Please install Python and run: pip install -r requirements.txt
    pause
)
""")
    else:  # Unix/Linux/macOS
        run_script = package_dir / "run.sh"
        with open(run_script, 'w') as f:
            f.write("""#!/bin/bash
echo "Starting Professional Invoice Manager..."
python3 launch_app.py
if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Python or required packages not found"
    echo "Please install Python and run: pip install -r requirements.txt"
    read -p "Press Enter to continue..."
fi
""")
        # Make executable
        os.chmod(run_script, 0o755)
    
    print(f"  ✅ Created {run_script.name}")
    
    # Create installation instructions
    install_guide = package_dir / "INSTALL.txt"
    with open(install_guide, 'w') as f:
        f.write("""Professional Invoice Manager - Installation Guide

OPTION 1: Run from Source (Recommended)
1. Install Python 3.7+ from https://python.org
2. Install dependencies: pip install -r requirements.txt
3. Run the application: python launch_app.py

OPTION 2: Portable Installation
1. Extract all files to a folder
2. Install Python 3.7+ if not already installed
3. Open terminal/command prompt in this folder
4. Run: pip install PyQt5
5. Double-click run.bat (Windows) or run.sh (Linux/macOS)

OPTION 3: Use Pre-built Executable (if available)
1. Download the executable from GitHub Releases
2. Run InvoiceManager.exe (Windows) or InvoiceManager (Linux/macOS)

For help and documentation, see README.md or visit:
https://github.com/YOUR_USERNAME/professional-invoice-manager

System Requirements:
- Windows 7+, macOS 10.12+, or Linux (Ubuntu 16.04+)
- Python 3.7 or higher
- 512MB RAM (2GB recommended)
- 100MB disk space
""")
    
    print(f"  ✅ Created installation guide")
    print(f"📦 Portable package created in: {package_dir}")
    
    return str(package_dir)

def main():
    """Main build function"""
    print("🚀 Professional Invoice Manager Build Script")
    print("=" * 50)
    
    # Build executable
    exe_path = build_executable()
    
    # Create portable package
    portable_path = create_portable_package()
    
    print("\n🎉 Build Complete!")
    print("=" * 50)
    
    if exe_path:
        print(f"📱 Executable: {exe_path}")
    
    if portable_path:
        print(f"📦 Portable: {portable_path}")
    
    print("\n📋 Next Steps:")
    print("1. Test the executable on a clean system")
    print("2. Upload to GitHub Releases")
    print("3. Update download links in README")
    
    return exe_path is not None

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
