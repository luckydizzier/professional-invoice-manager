#!/usr/bin/env python3
"""
Test script for the Professional Invoice Manager with Keyboard Navigation
Run this to test the enhanced application with professional styling and keyboard navigation
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from main_fixed import *
    
    if __name__ == "__main__":
        print("🚀 Starting Professional Invoice Manager with Keyboard Navigation...")
        print("📋 Features:")
        print("   • Professional styling with CSS")
        print("   • Comprehensive keyboard navigation")
        print("   • Enhanced focus indicators")
        print("   • Fixed database schema")
        print("")
        print("🎹 Keyboard Shortcuts:")
        print("   F5          - Refresh list")
        print("   Ctrl+N      - New invoice")
        print("   Enter       - Edit selected invoice")
        print("   Delete      - Delete selected invoice")
        print("   Insert      - New invoice (alternative)")
        print("   Escape      - Cancel/Back")
        print("   F1          - Show help")
        print("   Arrow keys  - Navigate in tables")
        print("")
        
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("Professional Invoice Manager")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("Invoice Solutions")
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        print("✅ Application started successfully!")
        print("💡 Use keyboard shortcuts for navigation")
        
        # Run the application
        sys.exit(app.exec_())
        
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure all required modules are available")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting application: {e}")
    sys.exit(1)
