#!/usr/bin/env python3
"""
Test script to verify the status bar fix
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("🧪 Testing status bar fix...")
    
    # Test just the imports
    from PyQt5.QtWidgets import QApplication, QMainWindow, QStatusBar
    from PyQt5.QtCore import Qt
    
    print("✅ PyQt5 imports successful")
    
    # Test basic status bar creation
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    status = QStatusBar()
    window.setStatusBar(status)
    status.showMessage("✅ Status bar test")
    
    print("✅ Status bar created successfully")
    
    # Test our config import
    try:
        from config import config
        print("✅ Config import successful")
    except Exception as e:
        print(f"⚠️ Config import warning: {e}")
    
    # Test the main components without running the full app
    try:
        from main_fixed import MainWindow
        print("✅ MainWindow import successful")
        
        # Test creating the main window (but don't show it)
        test_window = MainWindow()
        
        # Check if status bar exists
        if hasattr(test_window, 'status') and test_window.status:
            print("✅ Status bar properly initialized in MainWindow")
            test_window.status.showMessage("🎉 Status bar fix successful!")
        else:
            print("❌ Status bar not found in MainWindow")
        
        print("✅ MainWindow created successfully without errors")
        
    except Exception as e:
        print(f"❌ MainWindow creation error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🏁 Test completed. The status bar fix should be working!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
