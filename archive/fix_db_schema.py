#!/usr/bin/env python3
"""
Test adding description column to existing database
"""
import sqlite3

def add_description_column():
    """Add description column to invoice_item table if it doesn't exist"""
    conn = sqlite3.connect('invoice_qt5.db')
    
    try:
        # Check if description column exists
        cursor = conn.execute('PRAGMA table_info(invoice_item)')
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'description' not in columns:
            print("📋 Adding description column to invoice_item table...")
            conn.execute('ALTER TABLE invoice_item ADD COLUMN description TEXT')
            conn.commit()
            print("✅ Description column added successfully")
        else:
            print("✅ Description column already exists")
        
        # Verify the schema
        cursor = conn.execute('PRAGMA table_info(invoice_item)')
        print("\n📋 Updated invoice_item table columns:")
        for row in cursor.fetchall():
            print(f"  {row[1]} ({row[2]})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_description_column()
