# database.py
import sqlite3
import os
import json
from datetime import datetime

DB_FILE = "store.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # ========================
    #    USERS TABLE
    # ========================
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'cashier', 'manager')),
            full_name TEXT
        )
    """)

    # ========================
    #    CATEGORIES TABLE
    # ========================
    c.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parent_id INTEGER,
            location_tag TEXT,
            FOREIGN KEY (parent_id) REFERENCES categories(id)
        )
    """)

    # ========================
    #    SUPPLIERS TABLE
    # ========================
    c.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ntn TEXT,
            gst TEXT,
            address TEXT,
            payment_terms TEXT,
            order_days TEXT,
            lead_time_days INTEGER DEFAULT 3
        )
    """)

    # ========================
    #    TAXES TABLE
    # ========================
    c.execute("""
        CREATE TABLE IF NOT EXISTS taxes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rate REAL NOT NULL,
            is_default BOOLEAN DEFAULT 0
        )
    """)

    # ========================
    #    UOM TABLE
    # ========================
    c.execute("""
        CREATE TABLE IF NOT EXISTS uoms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            symbol TEXT NOT NULL UNIQUE
        )
    """)

    # ========================
    #    PRODUCTS TABLE
    # ========================
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            barcode TEXT,
            company TEXT,
            category_id INTEGER,
            supplier_id INTEGER,
            tax_id INTEGER,
            base_uom_id INTEGER,
            purchase_uom_id INTEGER,
            cost_price REAL,
            selling_price REAL,
            stock REAL DEFAULT 0,
            tax_type TEXT DEFAULT 'exclusive',
            gst_rate REAL DEFAULT 17.0,
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY (tax_id) REFERENCES taxes(id),
            FOREIGN KEY (base_uom_id) REFERENCES uoms(id),
            FOREIGN KEY (purchase_uom_id) REFERENCES uoms(id)
        )
    """)

    # ========================
    #    PRODUCT VARIANTS TABLE
    # ========================
    c.execute("""
        CREATE TABLE IF NOT EXISTS product_variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            variant_name TEXT,
            variant_value TEXT,
            barcode TEXT,
            price REAL,
            stock REAL DEFAULT 0,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # ========================
    #    UOM CONVERSIONS TABLE
    # ========================
    c.execute("""
        CREATE TABLE IF NOT EXISTS uom_conversions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            from_uom_id INTEGER,
            to_uom_id INTEGER,
            factor REAL,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (from_uom_id) REFERENCES uoms(id),
            FOREIGN KEY (to_uom_id) REFERENCES uoms(id)
        )
    """)

    # ========================
    #    SALES TABLE
    # ========================
    c.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no TEXT UNIQUE,
            customer_name TEXT,
            total REAL,
            discount REAL DEFAULT 0,
            payment_method TEXT CHECK(payment_method IN ('cash', 'credit_card', 'return')),
            is_held BOOLEAN DEFAULT 0,
            is_return BOOLEAN DEFAULT 0,
            original_invoice TEXT,
            cashier_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cashier_id) REFERENCES users(id)
        )
    """)

    # ========================
    #    SALE ITEMS TABLE
    # ========================
    c.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER,
            product_id INTEGER,
            variant_id INTEGER,
            quantity REAL,
            unit_price REAL,
            total_price REAL,
            FOREIGN KEY (sale_id) REFERENCES sales(id),
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (variant_id) REFERENCES product_variants(id)
        )
    """)

    # ========================
    #    PURCHASE ORDERS TABLE
    # ========================
    c.execute("""
        CREATE TABLE IF NOT EXISTS purchase_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_number TEXT UNIQUE,
            supplier_id INTEGER,
            status TEXT CHECK(status IN ('draft', 'sent', 'received', 'partial', 'cancelled')) DEFAULT 'draft',
            total_amount REAL,
            created_by INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            sent_at TEXT,
            received_at TEXT,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)

    # ========================
    #    PO ITEMS TABLE
    # ========================
    c.execute("""
        CREATE TABLE IF NOT EXISTS po_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_id INTEGER,
            product_id INTEGER,
            quantity_ordered REAL,
            quantity_received REAL DEFAULT 0,
            cost_price REAL,
            FOREIGN KEY (po_id) REFERENCES purchase_orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # ========================
    #    GOODS RECEIPT TABLE
    # ========================
    c.execute("""
        CREATE TABLE IF NOT EXISTS goods_receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_number TEXT UNIQUE,
            po_id INTEGER,
            supplier_id INTEGER,
            total_amount REAL,
            net_payable REAL,
            withholding_tax_rate REAL DEFAULT 0,
            withholding_tax_amount REAL DEFAULT 0,
            received_by INTEGER,
            received_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_direct_receipt BOOLEAN DEFAULT 0,
            FOREIGN KEY (po_id) REFERENCES purchase_orders(id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY (received_by) REFERENCES users(id)
        )
    """)

    # ========================
    #    GOODS RECEIPT ITEMS TABLE
    # ========================
    c.execute("""
        CREATE TABLE IF NOT EXISTS goods_receipt_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id INTEGER,
            product_id INTEGER,
            quantity_received REAL,
            foc_quantity REAL DEFAULT 0,
            quantity_in_base_uom REAL,
            trade_price REAL,
            retail_price REAL,
            cost_price REAL,
            FOREIGN KEY (receipt_id) REFERENCES goods_receipts(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # ========================
    #    WITHHOLDING TAX RECORDS
    # ========================
    c.execute("""
        CREATE TABLE IF NOT EXISTS withholding_tax_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id INTEGER,
            tax_amount REAL,
            tax_date TEXT,
            status TEXT DEFAULT 'pending',
            paid_date TEXT,
            FOREIGN KEY (receipt_id) REFERENCES goods_receipts(id)
        )
    """)

    # ========================
    #    INSERT DEFAULT DATA
    # ========================

    # Default Users
    c.execute("INSERT OR IGNORE INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
              ("admin", "admin123", "admin", "System Admin"))
    c.execute("INSERT OR IGNORE INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
              ("cashier1", "cash123", "cashier", "Cashier One"))

    # Default Taxes
    c.execute("INSERT OR IGNORE INTO taxes (name, rate, is_default) VALUES (?, ?, ?)", ("GST 17%", 17.0, 1))

    # Default UOMs
    c.execute("INSERT OR IGNORE INTO uoms (name, symbol) VALUES (?, ?)", ("Piece", "pcs"))
    c.execute("INSERT OR IGNORE INTO uoms (name, symbol) VALUES (?, ?)", ("Box", "box"))

    # Sample Categories
    c.execute("INSERT OR IGNORE INTO categories (id, name, parent_id, location_tag) VALUES (1, 'Grocery', NULL, 'A1')")
    c.execute("INSERT OR IGNORE INTO categories (id, name, parent_id, location_tag) VALUES (2, 'Beverages', 1, 'A2')")

    # Sample Suppliers
    c.execute("""
        INSERT OR IGNORE INTO suppliers (name, ntn, gst, address, payment_terms, order_days, lead_time_days)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "Procter & Gamble",
        "NTN-12345",
        "GST-67890",
        "Industrial Zone, Lahore",
        "Net 30 Days",
        json.dumps(["Monday", "Thursday"]),
        3
    ))

    # Sample Products
    c.execute("""
        INSERT OR IGNORE INTO products (name, company, barcode, category_id, supplier_id, tax_id, 
                                      base_uom_id, purchase_uom_id, cost_price, selling_price, stock, tax_type, gst_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Oral-B Toothbrush",
        "Procter & Gamble",
        "1234567890123",
        1,  # Grocery
        1,  # P&G
        1,  # GST 17%
        1,  # Piece
        2,  # Box
        200.0,
        250.0,
        120.0,
        "exclusive",  # tax_type
        17.0          # gst_rate
    ))

    # Sample UOM Conversion: 1 Box = 12 Pieces
    c.execute("""
        INSERT OR IGNORE INTO uom_conversions (product_id, from_uom_id, to_uom_id, factor)
        VALUES (?, ?, ?, ?)
    """, (1, 2, 1, 12.0))  # Box → Piece

    conn.commit()
    conn.close()
    print("✅ Clean database initialized")

def get_db_connection():
    return sqlite3.connect(DB_FILE)

# ========================
#    SAFE QUERY HELPERS
# ========================
def execute_query(query, params=(), fetch=False):
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(query, params)
        if fetch:
            result = c.fetchall()
            conn.commit()
            return result
        else:
            conn.commit()
            return c.lastrowid if query.strip().upper().startswith("INSERT") else None
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def fetch_all(query, params=()):
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(query, params)
        return c.fetchall()
    finally:
        if conn:
            conn.close()

def fetch_one(query, params=()):
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(query, params)
        return c.fetchone()
    finally:
        if conn:
            conn.close()