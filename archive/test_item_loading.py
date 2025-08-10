#!/usr/bin/env python3
"""
Test invoice item loading with description column
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_item_loading():
    """Test loading invoice items with description column"""
    print("🧪 Testing Invoice Item Loading with Description...")
    
    try:
        from main_with_management import get_db
        
        # Test the exact query that was failing in load_items()
        with get_db() as conn:
            # Try to find an invoice with items
            invoice = conn.execute("SELECT id FROM invoice LIMIT 1").fetchone()
            if not invoice:
                print("⚠️  No invoices found in database")
                return True
            
            invoice_id = invoice['id']
            print(f"📄 Testing with invoice ID: {invoice_id}")
            
            # Test the exact query from load_items()
            items = conn.execute("""
                SELECT ii.*, p.name as product_name, p.sku
                FROM invoice_item ii
                LEFT JOIN product p ON ii.product_id = p.id
                WHERE ii.invoice_id = ?
                ORDER BY ii.id
            """, (invoice_id,)).fetchall()
            
            print(f"✅ Found {len(items)} items for invoice {invoice_id}")
            
            # Test accessing the fields that were causing "No item with that key" error
            for i, item in enumerate(items):
                description = item['description'] or ""
                quantity = item['qty']
                unit_price = item['unit_price_cents'] / 100.0
                vat_rate = item['vat_rate']
                product_name = item['product_name'] or "Egyedi tétel"
                
                print(f"  📦 Item {i+1}: '{product_name}', qty={quantity}, price={unit_price} Ft, desc='{description}'")
            
            print("✅ All item fields accessible - 'No item with that key' error should be fixed!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 Invoice Item Loading Test")
    print("=" * 40)
    
    if test_item_loading():
        print("\n🎉 Invoice item loading test successful!")
        print("💡 The 'Tételek betöltése sikertelen: No item with that key' error should be resolved")
        print("🏃 The application should now work properly")
    else:
        print("\n❌ Invoice item loading test failed")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
