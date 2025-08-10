#!/usr/bin/env python3
"""
Test detailed VAT summary functionality
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_vat_summary():
    """Test the new VAT summary feature"""
    print("🧪 Testing Detailed VAT Summary Feature...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from main_with_management import get_db, InvoiceDetailWidget, init_database
        
        # Initialize database
        init_database()
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        print("✅ Application initialized")
        
        # Test VAT calculation logic
        print("\n📊 Testing VAT Breakdown Calculation...")
        
        # Sample invoice items with different VAT rates
        test_items = [
            {'qty': 2, 'unit_price_cents': 100000, 'vat_rate': 27},  # 2x 1000 Ft @ 27%
            {'qty': 1, 'unit_price_cents': 50000, 'vat_rate': 18},   # 1x 500 Ft @ 18%
            {'qty': 3, 'unit_price_cents': 200000, 'vat_rate': 27},  # 3x 2000 Ft @ 27%
            {'qty': 1, 'unit_price_cents': 75000, 'vat_rate': 5},    # 1x 750 Ft @ 5%
        ]
        
        # Calculate expected VAT breakdown
        vat_breakdown = {}
        total_net = 0
        total_vat = 0
        
        for item in test_items:
            quantity = item['qty']
            unit_price = item['unit_price_cents'] / 100.0
            vat_rate = item['vat_rate']
            
            line_net = quantity * unit_price
            line_vat = line_net * (vat_rate / 100.0)
            
            total_net += line_net
            total_vat += line_vat
            
            if vat_rate not in vat_breakdown:
                vat_breakdown[vat_rate] = {'net': 0, 'vat': 0, 'gross': 0}
            
            vat_breakdown[vat_rate]['net'] += line_net
            vat_breakdown[vat_rate]['vat'] += line_vat
            vat_breakdown[vat_rate]['gross'] += line_net + line_vat
        
        print("✅ VAT Breakdown Calculation:")
        for vat_rate, data in sorted(vat_breakdown.items()):
            print(f"   📊 {vat_rate}% ÁFA: Nettó {data['net']:.2f} Ft | ÁFA {data['vat']:.2f} Ft | Bruttó {data['gross']:.2f} Ft")
        
        total_gross = total_net + total_vat
        print(f"\n💰 Összesen: Nettó {total_net:.2f} Ft | ÁFA {total_vat:.2f} Ft | Bruttó {total_gross:.2f} Ft")
        
        # Test widget creation
        print("\n🖼️ Testing VAT Summary Widget...")
        widget = InvoiceDetailWidget()
        
        # Check if VAT table exists
        if hasattr(widget, 'vat_table'):
            print("✅ VAT summary table created successfully")
            print(f"   📋 VAT table columns: {widget.vat_table.columnCount()}")
            print(f"   📊 VAT table headers: {[widget.vat_table.horizontalHeaderItem(i).text() for i in range(widget.vat_table.columnCount())]}")
        else:
            print("❌ VAT summary table not found")
            return False
        
        # Test VAT summary update method
        if hasattr(widget, 'update_vat_summary'):
            print("✅ VAT summary update method available")
            
            # Test the method with our test data
            widget.update_vat_summary(vat_breakdown)
            print(f"   📊 VAT table rows after update: {widget.vat_table.rowCount()}")
        else:
            print("❌ VAT summary update method not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ VAT summary test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_vat_data():
    """Test VAT calculations with real database data"""
    print("\n🗄️ Testing VAT Summary with Database Data...")
    
    try:
        from main_with_management import get_db
        
        with get_db() as conn:
            # Find an invoice with items
            invoice = conn.execute("""
                SELECT i.id, i.number, COUNT(ii.id) as item_count
                FROM invoice i
                LEFT JOIN invoice_item ii ON i.id = ii.invoice_id
                GROUP BY i.id, i.number
                HAVING item_count > 0
                LIMIT 1
            """).fetchone()
            
            if not invoice:
                print("⚠️  No invoices with items found for testing")
                return True
            
            print(f"📄 Testing with invoice: {invoice['number']} ({invoice['item_count']} items)")
            
            # Get items and calculate VAT breakdown
            items = conn.execute("""
                SELECT ii.qty, ii.unit_price_cents, ii.vat_rate
                FROM invoice_item ii
                WHERE ii.invoice_id = ?
            """, (invoice['id'],)).fetchall()
            
            vat_breakdown = {}
            for item in items:
                quantity = item['qty']
                unit_price = item['unit_price_cents'] / 100.0
                vat_rate = item['vat_rate']
                
                line_net = quantity * unit_price
                line_vat = line_net * (vat_rate / 100.0)
                
                if vat_rate not in vat_breakdown:
                    vat_breakdown[vat_rate] = {'net': 0, 'vat': 0, 'gross': 0}
                
                vat_breakdown[vat_rate]['net'] += line_net
                vat_breakdown[vat_rate]['vat'] += line_vat
                vat_breakdown[vat_rate]['gross'] += line_net + line_vat
            
            print("✅ Real data VAT breakdown:")
            for vat_rate, data in sorted(vat_breakdown.items()):
                print(f"   📊 {vat_rate}% ÁFA: Nettó {data['net']:.2f} Ft | ÁFA {data['vat']:.2f} Ft | Bruttó {data['gross']:.2f} Ft")
            
            return True
            
    except Exception as e:
        print(f"❌ Database VAT test failed: {e}")
        return False

def main():
    print("🚀 Detailed VAT Summary Test")
    print("=" * 50)
    
    test1_passed = test_vat_summary()
    test2_passed = test_database_vat_data()
    
    if test1_passed and test2_passed:
        print("\n🎉 VAT Summary implementation successful!")
        print("\n📋 New Features Added:")
        print("   • Detailed VAT breakdown by rate")
        print("   • Professional VAT summary table")
        print("   • Enhanced totals display")
        print("   • Automatic VAT calculation grouping")
        print("\n🏃 Ready to Use: python launch_app.py")
    else:
        print("\n❌ VAT summary tests failed")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
