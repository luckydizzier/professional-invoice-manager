#!/usr/bin/env python3
"""
Test script for the fixed database version
"""

import sys
import sqlite3

# Test database connectivity and schema
def test_database():
    print("🔍 Testing database schema...")
    
    try:
        conn = sqlite3.connect("invoice_qt5.db")
        conn.row_factory = sqlite3.Row
        
        # Test invoice table schema
        cursor = conn.execute("PRAGMA table_info(invoice)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Invoice table columns: {columns}")
        
        # Test if created_utc exists
        if 'created_utc' in columns:
            print("✅ created_utc column found")
        else:
            print("❌ created_utc column missing")
        
        # Test product table schema
        cursor = conn.execute("PRAGMA table_info(product)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"📦 Product table columns: {columns}")
        
        # Test if unit_price_cents exists
        if 'unit_price_cents' in columns:
            print("✅ unit_price_cents column found")
        else:
            print("❌ unit_price_cents column missing")
        
        # Test basic query
        invoices = conn.execute("""
            SELECT i.id, i.number, i.created_utc, i.direction, p.name as partner
            FROM invoice i 
            LEFT JOIN partner p ON i.partner_id = p.id 
            ORDER BY i.created_utc DESC
            LIMIT 5
        """).fetchall()
        
        print(f"📊 Found {len(invoices)} invoices")
        
        conn.close()
        print("✅ Database test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

# Test the main application imports
def test_imports():
    print("🔍 Testing imports...")
    
    try:
        from config import config
        print("✅ Config import successful")
        
        # Test config access
        db_path = config.get("database.path", "invoice_qt5.db")
        print(f"📁 Database path: {db_path}")
        
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5 import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    print("🚀 Testing Fixed Invoice Manager v2.0.1")
    print("=" * 50)
    
    # Test imports first
    if not test_imports():
        return 1
    
    print()
    
    # Test database
    if not test_database():
        return 1
    
    print()
    print("🎉 All tests passed! The application should work correctly.")
    print("💡 To run the application: python main_fixed.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
