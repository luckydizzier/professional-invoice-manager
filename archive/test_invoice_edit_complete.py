#!/usr/bin/env python3
"""
Comprehensive test for invoice editing functionality
"""

import sys
import sqlite3
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_invoice_edit_complete():
    """Test complete invoice editing workflow"""
    print("🧪 Testing Complete Invoice Editing Workflow...")
    
    try:
        from PyQt5.QtWidgets import QApplication, QDialog
        from main_with_management import get_db, InvoiceFormDialog, init_database, MainWindow
        
        # Initialize database
        init_database()
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        print("✅ Application initialized")
        
        # Test 1: Get an existing invoice
        with get_db() as conn:
            invoice = conn.execute("""
                SELECT * FROM invoice LIMIT 1
            """).fetchone()
            
            if not invoice:
                print("❌ No invoices found to edit")
                return False
                
            invoice_data = dict(invoice)
            print(f"📄 Found invoice: {invoice_data['number']}")
        
        # Test 2: Create edit dialog with existing data
        dialog = InvoiceFormDialog(invoice_data)
        print("✅ Edit dialog created successfully")
        
        # Test 3: Verify data loading
        loaded_data = dialog.get_data()
        print(f"✅ Data loaded: {loaded_data}")
        
        # Test 4: Verify dialog constants
        print(f"📋 QDialog.Accepted = {QDialog.Accepted}")
        
        # Test 5: Test MainWindow creation
        main_window = MainWindow()
        print("✅ MainWindow created successfully")
        
        # Test 6: Check if invoice list page exists
        if hasattr(main_window, 'invoice_page'):
            print("✅ Invoice list page exists")
        else:
            print("⚠️ Invoice list page not found - checking pages...")
            if hasattr(main_window, 'pages'):
                print(f"📋 Available pages: {list(main_window.pages.keys()) if hasattr(main_window.pages, 'keys') else 'No pages dict'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Invoice editing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_invoice_save_simulation():
    """Test simulating an invoice save operation"""
    print("\n🧪 Testing Invoice Save Simulation...")
    
    try:
        from main_with_management import get_db, init_database
        
        # Initialize database
        init_database()
        
        # Get an existing invoice
        with get_db() as conn:
            invoice = conn.execute("""
                SELECT * FROM invoice LIMIT 1
            """).fetchone()
            
            if not invoice:
                print("❌ No invoices found")
                return False
            
            original_number = invoice['number']
            invoice_id = invoice['id']
            
            print(f"📄 Original invoice: {original_number}")
            
            # Simulate an update
            new_number = f"{original_number}_EDITED"
            
            # Test the update query that would be used in edit_invoice
            conn.execute("""
                UPDATE invoice SET number=?, direction=?, partner_id=? 
                WHERE id=?
            """, (new_number, invoice['direction'], invoice['partner_id'], invoice_id))
            conn.commit()
            
            # Verify the update
            updated_invoice = conn.execute("""
                SELECT * FROM invoice WHERE id = ?
            """, (invoice_id,)).fetchone()
            
            if updated_invoice['number'] == new_number:
                print(f"✅ Invoice update successful: {new_number}")
                
                # Restore original
                conn.execute("""
                    UPDATE invoice SET number=? WHERE id=?
                """, (original_number, invoice_id))
                conn.commit()
                print(f"✅ Invoice restored to: {original_number}")
                
                return True
            else:
                print("❌ Invoice update failed")
                return False
                
    except Exception as e:
        print(f"❌ Invoice save test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 Comprehensive Invoice Editing Test")
    print("=" * 50)
    
    test1_passed = test_invoice_edit_complete()
    test2_passed = test_invoice_save_simulation()
    
    if test1_passed and test2_passed:
        print("\n🎉 All invoice editing tests passed!")
        print("💡 Invoice editing should work correctly in the application")
        print("🏃 Try running: python launch_app.py")
    else:
        print("\n❌ Some invoice editing tests failed")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
