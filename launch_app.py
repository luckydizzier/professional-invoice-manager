#!/usr/bin/env python3
"""
Professional Invoice Manager v2.0 - Working Version
Launch script with proper error handling and keyboard navigation
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main application launcher with comprehensive error handling"""
    print("🚀 Starting Professional Invoice Manager v2.1 with Management...")
    print("📋 Features: Product & Supplier Management | Keyboard Navigation | Professional Styling")
    print("🔧 Database: Fixed column name compatibility (qty vs quantity)")
    print("")
    
    try:
        # Import PyQt5 components
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        
        # Import our main application
        from main_with_management import main as app_main
        
        print("✅ All imports successful")
        print("🎹 Keyboard shortcuts:")
        print("   F1     - Help")
        print("   F2     - Invoices")
        print("   F3     - Products")
        print("   F4     - Customers")
        print("   F5     - Refresh")
        print("   F6     - Suppliers")
        print("   Enter  - Edit item")
        print("   Delete - Delete item")
        print("   Insert - New item")
        print("   Escape - Back/Clear")
        print("   Alt+←→ - Menu navigation")
        print("")
        
        # Run the application
        return app_main()
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure all required modules are installed")
        return 1
    except Exception as e:
        print(f"❌ Application Error: {e}")
        print("\n📋 Full traceback:")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
