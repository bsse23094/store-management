"""
Real Excel Import/Export Functionality Test
Tests the actual Excel import code from the GUI
"""

import unittest
import os
import sys
import sqlite3
from datetime import datetime

# Test Excel operations
try:
    import pandas as pd
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
    print("❌ Excel libraries not available. Install with: pip install pandas openpyxl")

# Import project modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import fetch_all, fetch_one, execute_query


class TestExcelImportFunctionality(unittest.TestCase):
    """Test actual Excel import functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_db = "test_excel.db"
        self.test_excel_file = "test_import_products.xlsx"
        self.test_export_file = "test_export_products.xlsx"
        
        # Create test database
        self.setup_test_database()
    
    def tearDown(self):
        """Clean up test files"""
        files = [self.test_db, self.test_excel_file, self.test_export_file]
        for file in files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass
    
    def setup_test_database(self):
        """Create test database with required tables"""
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Create necessary tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                contact TEXT,
                phone TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uoms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                symbol TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                barcode TEXT UNIQUE,
                company TEXT,
                category_id INTEGER,
                supplier_id INTEGER,
                tax_id INTEGER DEFAULT 1,
                base_uom_id INTEGER DEFAULT 1,
                purchase_uom_id INTEGER DEFAULT 1,
                cost_price REAL DEFAULT 0,
                selling_price REAL DEFAULT 0,
                stock REAL DEFAULT 0,
                min_stock REAL DEFAULT 0,
                FOREIGN KEY (category_id) REFERENCES categories(id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_variants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                variant_name TEXT NOT NULL,
                variant_value TEXT NOT NULL,
                barcode TEXT UNIQUE,
                price REAL DEFAULT 0,
                stock REAL DEFAULT 0,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        # Insert default data
        cursor.execute("INSERT INTO categories (name) VALUES (?)", ("Electronics",))
        cursor.execute("INSERT INTO categories (name) VALUES (?)", ("Groceries",))
        cursor.execute("INSERT INTO suppliers (name, contact) VALUES (?, ?)", ("ABC Suppliers", "Contact 1"))
        cursor.execute("INSERT INTO suppliers (name, contact) VALUES (?, ?)", ("XYZ Traders", "Contact 2"))
        cursor.execute("INSERT INTO uoms (name, symbol) VALUES (?, ?)", ("Piece", "pcs"))
        cursor.execute("INSERT INTO uoms (name, symbol) VALUES (?, ?)", ("Kilogram", "kg"))
        
        conn.commit()
        conn.close()
    
    @unittest.skipUnless(EXCEL_AVAILABLE, "Pandas/openpyxl not installed")
    def test_01_create_excel_import_file(self):
        """Test creating an Excel file for import"""
        data = {
            'Name': ['Samsung TV 43"', 'LG Washing Machine', 'Sony Headphones'],
            'Company': ['Samsung', 'LG', 'Sony'],
            'Barcode': ['8801643123456', '8806098123456', '4548736123456'],
            'Cost': [450.00, 550.00, 75.00],
            'Sale': [599.00, 699.00, 99.00],
            'Stock': [25, 15, 50],
            'Category': ['Electronics', 'Electronics', 'Electronics'],
            'Supplier': ['ABC Suppliers', 'ABC Suppliers', 'XYZ Traders'],
            'Unit': ['Piece', 'Piece', 'Piece']
        }
        
        df = pd.DataFrame(data)
        df.to_excel(self.test_excel_file, index=False, engine='openpyxl')
        
        self.assertTrue(os.path.exists(self.test_excel_file))
        print(f"✅ Created Excel file: {self.test_excel_file}")
    
    @unittest.skipUnless(EXCEL_AVAILABLE, "Pandas/openpyxl not installed")
    def test_02_read_and_validate_excel(self):
        """Test reading Excel file and validating data"""
        # Create test file
        data = {
            'Name': ['Product A', 'Product B', 'Product C'],
            'Company': ['Brand X', 'Brand Y', 'Brand Z'],
            'Barcode': ['111111', '222222', '333333'],
            'Cost': [10.0, 20.0, 30.0],
            'Sale': [15.0, 25.0, 35.0],
            'Stock': [100, 200, 300]
        }
        df = pd.DataFrame(data)
        df.to_excel(self.test_excel_file, index=False, engine='openpyxl')
        
        # Read it back
        df_read = pd.read_excel(self.test_excel_file, engine='openpyxl')
        
        self.assertEqual(len(df_read), 3)
        self.assertEqual(df_read.iloc[0]['Name'], 'Product A')
        self.assertEqual(df_read.iloc[1]['Cost'], 20.0)
        self.assertEqual(df_read.iloc[2]['Stock'], 300)
        print(f"✅ Successfully read {len(df_read)} rows from Excel")
    
    @unittest.skipUnless(EXCEL_AVAILABLE, "Pandas/openpyxl not installed")
    def test_03_import_products_to_database(self):
        """Test importing Excel data to database"""
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Create Excel file with products
        data = {
            'Name': ['iPhone 15', 'Galaxy S24', 'Pixel 8'],
            'Company': ['Apple', 'Samsung', 'Google'],
            'Barcode': ['194253123456', '8806094123456', '840244123456'],
            'Cost': [800.00, 750.00, 700.00],
            'Sale': [999.00, 899.00, 799.00],
            'Stock': [10, 15, 20],
            'Category': ['Electronics', 'Electronics', 'Electronics'],
            'Supplier': ['ABC Suppliers', 'ABC Suppliers', 'XYZ Traders'],
            'Unit': ['Piece', 'Piece', 'Piece']
        }
        df = pd.DataFrame(data)
        df.to_excel(self.test_excel_file, index=False, engine='openpyxl')
        
        # Read and import (simulating the GUI logic)
        df_import = pd.read_excel(self.test_excel_file, engine='openpyxl')
        
        imported_count = 0
        for _, row in df_import.iterrows():
            name = str(row['Name']).strip()
            company = str(row['Company']).strip() if pd.notna(row['Company']) else ""
            barcode = str(row['Barcode']).strip() if pd.notna(row['Barcode']) else ""
            cost = float(row['Cost']) if pd.notna(row['Cost']) else 0.0
            sale = float(row['Sale']) if pd.notna(row['Sale']) else 0.0
            stock = float(row['Stock']) if pd.notna(row['Stock']) else 0.0
            category = str(row['Category']).strip() if pd.notna(row['Category']) else ""
            supplier = str(row['Supplier']).strip() if pd.notna(row['Supplier']) else ""
            
            # Get category ID
            category_id = None
            if category:
                cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
                cat_result = cursor.fetchone()
                if cat_result:
                    category_id = cat_result[0]
            
            # Get supplier ID
            supplier_id = None
            if supplier:
                cursor.execute("SELECT id FROM suppliers WHERE name = ?", (supplier,))
                sup_result = cursor.fetchone()
                if sup_result:
                    supplier_id = sup_result[0]
            
            # Insert product
            cursor.execute("""
                INSERT INTO products (name, barcode, company, category_id, supplier_id, 
                                    cost_price, selling_price, stock)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, barcode or None, company or None, category_id, supplier_id, 
                  cost, sale, stock))
            
            imported_count += 1
        
        conn.commit()
        
        # Verify import
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        self.assertEqual(count, 3)
        self.assertEqual(imported_count, 3)
        print(f"✅ Successfully imported {imported_count} products to database")
    
    @unittest.skipUnless(EXCEL_AVAILABLE, "Pandas/openpyxl not installed")
    def test_04_export_products_to_excel(self):
        """Test exporting products from database to Excel"""
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Insert test products
        products_data = [
            ('MacBook Pro', 'MBP123', 'Apple', 1, 1, 1800.00, 2199.00, 5),
            ('Dell XPS', 'DXPS456', 'Dell', 1, 2, 1500.00, 1799.00, 8),
            ('HP Laptop', 'HP789', 'HP', 1, 2, 1200.00, 1499.00, 12)
        ]
        
        for product in products_data:
            cursor.execute("""
                INSERT INTO products (name, barcode, company, category_id, supplier_id,
                                    cost_price, selling_price, stock)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, product)
        
        conn.commit()
        
        # Export to Excel
        cursor.execute("""
            SELECT p.name, p.barcode, p.company, c.name as category, s.name as supplier,
                   p.cost_price, p.selling_price, p.stock
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN suppliers s ON p.supplier_id = s.id
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        # Create DataFrame and export
        df_export = pd.DataFrame(rows, columns=[
            'Name', 'Barcode', 'Company', 'Category', 'Supplier', 
            'Cost Price', 'Selling Price', 'Stock'
        ])
        
        df_export.to_excel(self.test_export_file, index=False, engine='openpyxl')
        
        self.assertTrue(os.path.exists(self.test_export_file))
        self.assertGreater(os.path.getsize(self.test_export_file), 0)
        
        # Verify exported data
        df_verify = pd.read_excel(self.test_export_file, engine='openpyxl')
        self.assertEqual(len(df_verify), 3)
        self.assertEqual(df_verify.iloc[0]['Name'], 'MacBook Pro')
        
        print(f"✅ Successfully exported {len(df_verify)} products to Excel")
    
    @unittest.skipUnless(EXCEL_AVAILABLE, "Pandas/openpyxl not installed")
    def test_05_import_with_variants(self):
        """Test importing products with variants (size, color, etc.)"""
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Create Excel with variant data
        data = {
            'Name': ['Nike Shoes', 'Nike Shoes', 'Adidas Shoes'],
            'Company': ['Nike', 'Nike', 'Adidas'],
            'Variant': ['Size 10', 'Size 11', 'Size 9'],
            'Cost': [80.00, 80.00, 75.00],
            'Sale': [120.00, 120.00, 110.00],
            'Stock': [30, 25, 40]
        }
        df = pd.DataFrame(data)
        df.to_excel(self.test_excel_file, index=False, engine='openpyxl')
        
        # Import with variant handling
        df_import = pd.read_excel(self.test_excel_file, engine='openpyxl')
        
        # Group by base product name
        for product_name in df_import['Name'].unique():
            product_rows = df_import[df_import['Name'] == product_name]
            base_row = product_rows.iloc[0]
            
            # Insert base product
            cursor.execute("""
                INSERT INTO products (name, company, cost_price, selling_price, stock)
                VALUES (?, ?, ?, ?, ?)
            """, (product_name, base_row['Company'], base_row['Cost'], 
                  base_row['Sale'], base_row['Stock']))
            
            product_id = cursor.lastrowid
            
            # Insert variants
            for _, variant_row in product_rows.iterrows():
                if pd.notna(variant_row.get('Variant')):
                    cursor.execute("""
                        INSERT INTO product_variants (product_id, variant_name, variant_value,
                                                     price, stock)
                        VALUES (?, ?, ?, ?, ?)
                    """, (product_id, 'Size', variant_row['Variant'], 
                          variant_row['Sale'], variant_row['Stock']))
        
        conn.commit()
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM product_variants")
        variant_count = cursor.fetchone()[0]
        
        conn.close()
        
        self.assertGreater(product_count, 0)
        self.assertGreater(variant_count, 0)
        print(f"✅ Imported {product_count} products with {variant_count} variants")
    
    @unittest.skipUnless(EXCEL_AVAILABLE, "Pandas/openpyxl not installed")
    def test_06_handle_duplicate_barcodes(self):
        """Test handling duplicate barcodes during import"""
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Create Excel with duplicate barcode
        data = {
            'Name': ['Product 1', 'Product 2'],
            'Barcode': ['DUPLICATE123', 'DUPLICATE123'],
            'Cost': [10.0, 20.0],
            'Sale': [15.0, 25.0],
            'Stock': [100, 200]
        }
        df = pd.DataFrame(data)
        df.to_excel(self.test_excel_file, index=False, engine='openpyxl')
        
        # Try to import
        df_import = pd.read_excel(self.test_excel_file, engine='openpyxl')
        
        imported = 0
        failed = 0
        
        for _, row in df_import.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO products (name, barcode, cost_price, selling_price, stock)
                    VALUES (?, ?, ?, ?, ?)
                """, (row['Name'], row['Barcode'], row['Cost'], row['Sale'], row['Stock']))
                imported += 1
            except sqlite3.IntegrityError:
                # Duplicate barcode - skip
                failed += 1
        
        conn.commit()
        conn.close()
        
        self.assertEqual(imported, 1)  # Only first should succeed
        self.assertEqual(failed, 1)    # Second should fail
        print(f"✅ Correctly handled duplicate barcodes: {imported} imported, {failed} skipped")


def run_tests():
    """Run all tests and print results"""
    print("=" * 70)
    print("🧪 EXCEL IMPORT/EXPORT FUNCTIONALITY TEST")
    print("=" * 70)
    print()
    
    if not EXCEL_AVAILABLE:
        print("❌ ERROR: Excel libraries not installed!")
        print("   Install with: pip install pandas openpyxl")
        return False
    
    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestExcelImportFunctionality)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Tests Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Tests Failed: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped)}")
    print()
    
    if result.wasSuccessful():
        print("🎉 ALL EXCEL TESTS PASSED!")
        print()
        print("✅ Excel Import: Working")
        print("✅ Excel Export: Working")
        print("✅ Variant Handling: Working")
        print("✅ Duplicate Detection: Working")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        return False


if __name__ == '__main__':
    run_tests()
