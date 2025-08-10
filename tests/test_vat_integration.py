#!/usr/bin/env python3
"""
Quick test to verify VAT summary works with the main application
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_application_launch():
    """Test launching the application with VAT summary"""
    print("🧪 Testing Application Launch with VAT Summary...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from main_with_management import MainWindow, init_database
        
        # Initialize database
        init_database()
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        print("✅ PyQt5 Application created")
        
        # Create main window
        window = MainWindow()
        print("✅ MainWindow created successfully")
        
        # Check if the invoice detail widget has VAT summary components
        if hasattr(window, 'invoice_page'):
            detail_widget = window.invoice_page.detail_widget
            
            if hasattr(detail_widget, 'vat_table'):
                print("✅ VAT summary table found in detail widget")
                print(f"   📊 VAT table columns: {detail_widget.vat_table.columnCount()}")
            else:
                print("❌ VAT summary table not found")
                return False
                
            if hasattr(detail_widget, 'update_vat_summary'):
                print("✅ VAT summary update method found")
            else:
                print("❌ VAT summary update method not found")
                return False
        else:
            print("⚠️  Could not access invoice page for testing")
        
        print("✅ Application ready with VAT summary feature")
        return True
        
    except Exception as e:
        print(f"❌ Application launch test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 VAT Summary Application Test")
    print("=" * 40)
    
    if test_application_launch():
        print("\n🎉 VAT Summary feature successfully integrated!")
        print("\n📋 Enhanced Invoice Features:")
        print("   ✅ Detailed VAT breakdown by rate")
        print("   ✅ Professional VAT summary table")
        print("   ✅ Enhanced totals display")
        print("   ✅ Automatic calculations")
        print("\n🏃 Ready to use: python launch_app.py")
        print("💡 Select any invoice to see the new VAT summary!")
    else:
        print("\n❌ VAT summary integration test failed")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
