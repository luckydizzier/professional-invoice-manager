#!/usr/bin/env python3
"""
Test invoice editing functionality
"""

import sys
import sqlite3
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_edit_invoice():
    """Test editing an existing invoice"""
    print("🧪 Testing Invoice Editing...")
    
    try:
        from PyQt5.QtWidgets import QApplication, QDialog
        from main_with_management import get_db, InvoiceFormDialog, init_database
        
        # Initialize database
        init_database()
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Get an existing invoice
        with get_db() as conn:
            invoice = conn.execute("""
                SELECT * FROM invoice LIMIT 1
            """).fetchone()
            
            if not invoice:
                print("❌ No invoices found to edit")
                return False
                
            invoice_data = dict(invoice)
            print(f"📄 Found invoice: {invoice_data['number']}")
        
        # Test creating the edit dialog
        dialog = InvoiceFormDialog(invoice_data)
        print("✅ InvoiceFormDialog created successfully for editing")
        
        # Test dialog constants
        print(f"📋 QDialog.Accepted = {QDialog.Accepted}")
        
        # Test getting data
        data = dialog.get_data()
        print(f"✅ Dialog data retrieved: {data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Invoice editing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 Invoice Editing Test")
    print("=" * 40)
    
    if test_edit_invoice():
        print("\n🎉 Invoice editing test passed!")
        print("💡 The invoice editing should work correctly")
    else:
        print("\n❌ Invoice editing test failed")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
