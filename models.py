# database.py
import sqlite3
import os

DB_FILE = "store.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Users
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'cashier')),
            full_name TEXT
        )
    """)

    # Products
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock REAL DEFAULT 0,
            barcode TEXT UNIQUE
        )
    """)

    # Sales
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

    # Sale Items
    c.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER,
            product_id INTEGER,
            quantity REAL,
            unit_price REAL,
            total_price REAL,
            FOREIGN KEY (sale_id) REFERENCES sales(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # Create default admin
    c.execute("INSERT OR IGNORE INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
              ("admin", "admin123", "admin", "System Admin"))

    # Add sample products
    sample_products = [
        ("Coca Cola 500ml", 2.50, 100, "12345678"),
        ("Lays Chips", 1.80, 80, "87654321"),
        ("Nescafe Instant", 5.00, 50, "11223344"),
        ("Bread Loaf", 3.20, 60, "55667788"),
        ("Milk 1L", 1.99, 120, "99887766")
    ]
    for name, price, stock, barcode in sample_products:
        c.execute("INSERT OR IGNORE INTO products (name, price, stock, barcode) VALUES (?, ?, ?, ?)",
                  (name, price, stock, barcode))

    conn.commit()
    conn.close()
    print("✅ Database initialized with sample products")

def get_db_connection():
    return sqlite3.connect(DB_FILE)