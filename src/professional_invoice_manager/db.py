"""Database utilities for Professional Invoice Manager."""

import sqlite3

from professional_invoice_manager.config import config


def get_db():
    """Get database connection."""
    db_path = config.get("database.path", "invoice_qt5.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database with correct schema."""
    with get_db() as conn:
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS partner (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                kind TEXT NOT NULL CHECK(kind IN ('customer','supplier')),
                tax_id TEXT,
                address TEXT
            );
            CREATE TABLE IF NOT EXISTS product (
                id INTEGER PRIMARY KEY,
                sku TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                unit_price_cents INTEGER NOT NULL,
                vat_rate INTEGER NOT NULL DEFAULT 27
            );
            CREATE TABLE IF NOT EXISTS invoice (
                id INTEGER PRIMARY KEY,
                number TEXT NOT NULL UNIQUE,
                partner_id INTEGER NOT NULL REFERENCES partner(id),
                direction TEXT NOT NULL
                    CHECK(direction IN ('sale','purchase')),
                created_utc INTEGER NOT NULL,
                notes TEXT
            );
            CREATE TABLE IF NOT EXISTS invoice_item (
                id INTEGER PRIMARY KEY,
                invoice_id INTEGER NOT NULL REFERENCES invoice(id)
                    ON DELETE CASCADE,
                product_id INTEGER NOT NULL REFERENCES product(id),
                description TEXT,
                qty INTEGER NOT NULL,
                unit_price_cents INTEGER NOT NULL,
                vat_rate INTEGER NOT NULL
            );
            """
        )

        if conn.execute("SELECT COUNT(*) FROM product").fetchone()[0] == 0:
            products = [
                ("SKU001", "Kenyér 1kg", 69900, 5),
                ("SKU002", "Tej 1l", 39900, 18),
                ("SKU003", "Kolbász 1kg", 299900, 27),
                ("SKU004", "Kakaóscsiga", 34900, 27),
                ("SKU005", "Rostos üdítő 1l", 59900, 27),
            ]
            conn.executemany(
                "INSERT INTO product(sku,name,unit_price_cents,vat_rate) "
                "VALUES(?,?,?,?)",
                products,
            )

        if conn.execute("SELECT COUNT(*) FROM partner").fetchone()[0] == 0:
            partners = [
                ("Lakossági Vevő", "customer", None, None),
                (
                    "Teszt Kft.",
                    "customer",
                    "12345678-1-42",
                    "1111 Bp, Fő u. 1.",
                ),
                (
                    "Minta Beszállító Zrt.",
                    "supplier",
                    "87654321-2-13",
                    "7626 Pécs, Utca 2.",
                ),
            ]
            conn.executemany(
                "INSERT INTO partner(name,kind,tax_id,address) "
                "VALUES(?,?,?,?)",
                partners,
            )

        conn.commit()
