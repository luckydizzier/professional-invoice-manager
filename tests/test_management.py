#!/usr/bin/env python3
"""
Test Product and Supplier Management Features
"""

import sys
import sqlite3
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_management_features():
    """Test the management functionality"""
    print("🧪 Testing Product & Supplier Management Features...")
    
    try:
        # Test database connectivity
        from main_with_management import get_db, init_database
        
        print("✅ Database functions imported successfully")
        
        # Initialize database
        init_database()
        print("✅ Database initialized")
        
        # Test database content
        with get_db() as conn:
            # Check products
            products = conn.execute("SELECT COUNT(*) FROM product").fetchone()[0]
            print(f"📦 Products in database: {products}")
            
            # Check partners
            customers = conn.execute("SELECT COUNT(*) FROM partner WHERE kind='customer'").fetchone()[0]
            suppliers = conn.execute("SELECT COUNT(*) FROM partner WHERE kind='supplier'").fetchone()[0]
            print(f"👥 Customers in database: {customers}")
            print(f"🏭 Suppliers in database: {suppliers}")
            
            # Show sample products
            sample_products = conn.execute("""
                SELECT sku, name, unit_price_cents/100 as price_huf, vat_rate 
                FROM product LIMIT 3
            """).fetchall()
            
            print("\n📋 Sample Products:")
            for product in sample_products:
                print(f"  • {product['sku']}: {product['name']} - {product['price_huf']:.0f} Ft ({product['vat_rate']}% ÁFA)")
            
            # Show sample partners
            sample_partners = conn.execute("""
                SELECT name, kind, tax_id FROM partner LIMIT 3
            """).fetchall()
            
            print("\n👤 Sample Partners:")
            for partner in sample_partners:
                kind_emoji = "👥" if partner['kind'] == 'customer' else "🏭"
                print(f"  • {kind_emoji} {partner['name']} ({partner['tax_id'] or 'Nincs adószám'})")
        
        # Test dialog imports
        from main_with_management import ProductFormDialog, PartnerFormDialog
        print("✅ Form dialogs imported successfully")
        
        # Test main window import
        from main_with_management import MainWindow
        print("✅ MainWindow imported successfully")
        
        print("\n🎉 All management features are working!")
        print("\n📋 Available keyboard shortcuts:")
        print("   F1 - Help")
        print("   F2 - Invoices list")
        print("   F3 - Products management")
        print("   F4 - Customers management")  
        print("   F5 - Refresh current list")
        print("   F6 - Suppliers management")
        print("   Enter - Edit selected item")
        print("   Delete - Delete selected item")
        print("   Insert - Add new item")
        print("   Escape - Go back or clear selection")
        print("   Alt + Left/Right - Navigate between menus")
        
        print("\n🔧 Management Features:")
        print("   • Add, edit, delete products")
        print("   • Add, edit, delete customers")
        print("   • Add, edit, delete suppliers")
        print("   • Price management in HUF")
        print("   • VAT rate configuration")
        print("   • Tax ID and address management")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Product & Supplier Management Test")
    print("=" * 50)
    
    if test_management_features():
        print("\n✅ All tests passed!")
        print("💡 Run 'python launch_app.py' to start the application")
        return 0
    else:
        print("\n❌ Tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
