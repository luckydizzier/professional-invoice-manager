#!/usr/bin/env python3
"""
Quick test to verify database fix is working
"""

import sys
import sqlite3
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_database_fix():
    """Test that the database quantity column fix is working"""
    print("🧪 Testing Database Column Fix...")
    
    try:
        from main_with_management import get_db
        
        with get_db() as conn:
            # Test the fixed query
            rows = conn.execute("""
                SELECT i.id, i.number, i.created_utc, i.direction, p.name as partner,
                       COALESCE(SUM(ii.qty * ii.unit_price_cents * (1 + ii.vat_rate/100.0)), 0) as total_cents
                FROM invoice i 
                LEFT JOIN partner p ON i.partner_id = p.id 
                LEFT JOIN invoice_item ii ON i.id = ii.invoice_id
                GROUP BY i.id, i.number, i.created_utc, i.direction, p.name
                ORDER BY i.created_utc DESC
                LIMIT 5
            """).fetchall()
            
            print(f"✅ Database query fixed! Found {len(rows)} invoices")
            for row in rows:
                total = row[5] / 100.0 if row[5] else 0
                print(f"  📄 Invoice {row[1]}: {total:.2f} Ft total")
            
            # Test invoice item table structure
            cursor = conn.execute("PRAGMA table_info(invoice_item)")
            columns = [row[1] for row in cursor.fetchall()]
            print(f"\n📋 Invoice Item table columns: {columns}")
            
            if 'qty' in columns:
                print("✅ 'qty' column exists")
            else:
                print("❌ 'qty' column missing")
                
            return True
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    print("🚀 Database Fix Verification Test")
    print("=" * 40)
    
    if test_database_fix():
        print("\n🎉 Database fix verified successfully!")
        print("💡 The application should now work without the 'no such column: ii.quantity' error")
        print("🏃 You can now run: python main_with_management.py")
    else:
        print("\n❌ Database fix verification failed")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
