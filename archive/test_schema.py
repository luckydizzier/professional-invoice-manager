#!/usr/bin/env python3
"""
Test database schema
"""
import sqlite3

def check_schema():
    conn = sqlite3.connect('invoice_qt5.db')
    conn.row_factory = sqlite3.Row
    
    # Check invoice_item table schema
    cursor = conn.execute('PRAGMA table_info(invoice_item)')
    print('📋 invoice_item table columns:')
    for row in cursor.fetchall():
        print(f'  {row[1]} ({row[2]})')
    
    print()
    
    # Check product table schema
    cursor = conn.execute('PRAGMA table_info(product)')
    print('📦 product table columns:')
    for row in cursor.fetchall():
        print(f'  {row[1]} ({row[2]})')
    
    conn.close()

if __name__ == "__main__":
    check_schema()
