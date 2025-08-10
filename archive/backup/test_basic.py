#!/usr/bin/env python3
"""
Simple test script to verify the application works
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_basic_imports():
    """Test basic imports"""
    print("🔍 Testing basic imports...")
    
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout
        from PyQt5.QtCore import Qt
        print("✅ PyQt5 imports successful")
        return True
    except Exception as e:
        print(f"❌ PyQt5 import failed: {e}")
        return False

def test_simple_ui():
    """Test creating a simple UI"""
    print("🔍 Testing simple UI creation...")
    
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Create simple window
        window = QMainWindow()
        window.setWindowTitle("Simple Test Window")
        window.resize(400, 300)
        
        # Create central widget
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Add a label
        label = QLabel("✅ Application is working!\n\n🎹 This confirms PyQt5 is properly installed and functioning.")
        label.setStyleSheet("font-size: 14px; padding: 20px; text-align: center;")
        layout.addWidget(label)
        
        window.setCentralWidget(central_widget)
        
        print("✅ Simple UI created successfully")
        
        # Show window (but don't start event loop for this test)
        window.show()
        
        # Clean up
        window.close()
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"❌ Simple UI test failed: {e}")
        return False

def main():
    print("🚀 Testing Basic Application Components")
    print("=" * 50)
    
    # Test imports
    if not test_basic_imports():
        return 1
    
    print()
    
    # Test simple UI
    if not test_simple_ui():
        return 1
    
    print()
    print("🎉 All basic tests passed!")
    print("💡 PyQt5 is working correctly")
    print("📝 The main application should work with some fixes")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
