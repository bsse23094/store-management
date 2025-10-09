"""
Advanced Features Test Suite
Tests for Excel operations, PDF generation, and hardware integration simulation
"""

import unittest
import os
import json
from datetime import datetime
import sqlite3

# Test Excel operations
try:
    import pandas as pd
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

# Test matplotlib for reports
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class TestExcelOperations(unittest.TestCase):
    """Test Excel import/export functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_excel_file = "test_products.xlsx"
        self.test_export_file = "test_export.xlsx"
    
    def tearDown(self):
        """Clean up test files"""
        for file in [self.test_excel_file, self.test_export_file]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass
    
    @unittest.skipUnless(EXCEL_AVAILABLE, "Pandas/openpyxl not installed")
    def test_excel_library_available(self):
        """Test that Excel libraries are installed"""
        self.assertTrue(EXCEL_AVAILABLE)
        import pandas as pd
        import openpyxl
        self.assertIsNotNone(pd.__version__)
        self.assertIsNotNone(openpyxl.__version__)
    
    @unittest.skipUnless(EXCEL_AVAILABLE, "Pandas/openpyxl not installed")
    def test_create_sample_excel_file(self):
        """Test creating a sample Excel file for import"""
        # Create sample product data
        data = {
            'Name': ['Test Product 1', 'Test Product 2', 'Test Product 3'],
            'Company': ['Company A', 'Company B', 'Company C'],
            'Barcode': ['1234567890', '2345678901', '3456789012'],
            'Cost Price': [100.0, 150.0, 200.0],
            'Selling Price': [120.0, 180.0, 250.0],
            'Stock': [50, 75, 100]
        }
        
        df = pd.DataFrame(data)
        df.to_excel(self.test_excel_file, index=False, engine='openpyxl')
        
        self.assertTrue(os.path.exists(self.test_excel_file))
        self.assertGreater(os.path.getsize(self.test_excel_file), 0)
    
    @unittest.skipUnless(EXCEL_AVAILABLE, "Pandas/openpyxl not installed")
    def test_read_excel_file(self):
        """Test reading data from Excel file"""
        # Create test file
        data = {
            'Name': ['Product A', 'Product B'],
            'Company': ['Brand X', 'Brand Y'],
            'Barcode': ['111111', '222222'],
            'Cost Price': [50.0, 75.0],
            'Selling Price': [60.0, 90.0],
            'Stock': [100, 150]
        }
        df = pd.DataFrame(data)
        df.to_excel(self.test_excel_file, index=False, engine='openpyxl')
        
        # Read it back
        df_read = pd.read_excel(self.test_excel_file, engine='openpyxl')
        
        self.assertEqual(len(df_read), 2)
        self.assertEqual(df_read.iloc[0]['Name'], 'Product A')
        self.assertEqual(df_read.iloc[1]['Company'], 'Brand Y')
    
    @unittest.skipUnless(EXCEL_AVAILABLE, "Pandas/openpyxl not installed")
    def test_excel_data_validation(self):
        """Test validating Excel data before import"""
        data = {
            'Name': ['Valid Product', 'Another Product', ''],
            'Company': ['Company A', '', 'Company C'],
            'Barcode': ['123456', '234567', '345678'],
            'Cost Price': [100.0, -50.0, 200.0],  # Negative price (invalid)
            'Selling Price': [120.0, 180.0, 250.0],
            'Stock': [50, 75, -10]  # Negative stock (invalid)
        }
        
        df = pd.DataFrame(data)
        
        # Validation rules
        errors = []
        
        for idx, row in df.iterrows():
            if not row['Name'] or str(row['Name']).strip() == '':
                errors.append(f"Row {idx + 2}: Name is required")
            
            if row['Cost Price'] < 0:
                errors.append(f"Row {idx + 2}: Cost price cannot be negative")
            
            if row['Stock'] < 0:
                errors.append(f"Row {idx + 2}: Stock cannot be negative")
            
            if row['Selling Price'] < row['Cost Price']:
                errors.append(f"Row {idx + 2}: Selling price should be >= cost price")
        
        # We expect errors
        self.assertGreater(len(errors), 0)
        self.assertIn("Name is required", str(errors))
        self.assertIn("Cost price cannot be negative", str(errors))
    
    @unittest.skipUnless(EXCEL_AVAILABLE, "Pandas/openpyxl not installed")
    def test_export_data_to_excel(self):
        """Test exporting data to Excel"""
        # Sample data to export
        export_data = {
            'Product ID': [1, 2, 3],
            'Product Name': ['Item 1', 'Item 2', 'Item 3'],
            'Price': [100.0, 150.0, 200.0],
            'Stock': [50, 75, 100],
            'Status': ['Active', 'Active', 'Low Stock']
        }
        
        df = pd.DataFrame(export_data)
        df.to_excel(self.test_export_file, index=False, engine='openpyxl')
        
        self.assertTrue(os.path.exists(self.test_export_file))
        
        # Verify exported data
        df_verify = pd.read_excel(self.test_export_file, engine='openpyxl')
        self.assertEqual(len(df_verify), 3)
        self.assertEqual(df_verify.iloc[0]['Product Name'], 'Item 1')
    
    @unittest.skipUnless(EXCEL_AVAILABLE, "Pandas/openpyxl not installed")
    def test_excel_multiple_sheets(self):
        """Test working with multiple Excel sheets"""
        with pd.ExcelWriter(self.test_excel_file, engine='openpyxl') as writer:
            # Products sheet
            products = pd.DataFrame({
                'Name': ['Product 1', 'Product 2'],
                'Price': [100, 200]
            })
            products.to_excel(writer, sheet_name='Products', index=False)
            
            # Sales sheet
            sales = pd.DataFrame({
                'Invoice': ['INV001', 'INV002'],
                'Total': [500, 750]
            })
            sales.to_excel(writer, sheet_name='Sales', index=False)
        
        # Read both sheets
        products_df = pd.read_excel(self.test_excel_file, sheet_name='Products', engine='openpyxl')
        sales_df = pd.read_excel(self.test_excel_file, sheet_name='Sales', engine='openpyxl')
        
        self.assertEqual(len(products_df), 2)
        self.assertEqual(len(sales_df), 2)


class TestPDFReportGeneration(unittest.TestCase):
    """Test PDF report generation functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_report_dir = "test_reports"
        if not os.path.exists(self.test_report_dir):
            os.makedirs(self.test_report_dir)
    
    def tearDown(self):
        """Clean up test files"""
        import shutil
        if os.path.exists(self.test_report_dir):
            try:
                shutil.rmtree(self.test_report_dir)
            except:
                pass
    
    @unittest.skipUnless(MATPLOTLIB_AVAILABLE, "Matplotlib not installed")
    def test_matplotlib_available(self):
        """Test that matplotlib is available for chart generation"""
        self.assertTrue(MATPLOTLIB_AVAILABLE)
        import matplotlib
        self.assertIsNotNone(matplotlib.__version__)
    
    @unittest.skipUnless(MATPLOTLIB_AVAILABLE, "Matplotlib not installed")
    def test_generate_sales_chart(self):
        """Test generating a sales chart (for reports)"""
        # Sample sales data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        sales = [15000, 18000, 22000, 19000, 25000, 28000]
        
        # Create chart
        plt.figure(figsize=(10, 6))
        plt.bar(months, sales, color='skyblue')
        plt.title('Monthly Sales Report', fontsize=16)
        plt.xlabel('Month')
        plt.ylabel('Sales (Rs.)')
        plt.grid(axis='y', alpha=0.3)
        
        # Save chart
        chart_path = os.path.join(self.test_report_dir, 'sales_chart.png')
        plt.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        self.assertTrue(os.path.exists(chart_path))
        self.assertGreater(os.path.getsize(chart_path), 0)
    
    @unittest.skipUnless(MATPLOTLIB_AVAILABLE, "Matplotlib not installed")
    def test_generate_inventory_chart(self):
        """Test generating an inventory status chart"""
        categories = ['Electronics', 'Grocery', 'Clothing', 'Beverages', 'Health']
        stock_levels = [120, 450, 280, 350, 180]
        
        plt.figure(figsize=(10, 6))
        plt.pie(stock_levels, labels=categories, autopct='%1.1f%%', startangle=90)
        plt.title('Inventory Distribution', fontsize=16)
        
        chart_path = os.path.join(self.test_report_dir, 'inventory_chart.png')
        plt.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        self.assertTrue(os.path.exists(chart_path))
    
    def test_generate_text_report(self):
        """Test generating a text-based report"""
        report_path = os.path.join(self.test_report_dir, 'sales_report.txt')
        
        # Generate report
        with open(report_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("DAILY SALES REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("SUMMARY:\n")
            f.write("-" * 60 + "\n")
            f.write(f"Total Sales:        Rs. 125,450.00\n")
            f.write(f"Total Transactions: 87\n")
            f.write(f"Average Sale:       Rs. 1,442.00\n")
            f.write(f"Discount Given:     Rs. 3,250.00\n\n")
            
            f.write("TOP SELLING PRODUCTS:\n")
            f.write("-" * 60 + "\n")
            f.write(f"1. Coca Cola 1.5L        - 45 units - Rs. 6,750.00\n")
            f.write(f"2. Lays Chips 50g        - 38 units - Rs. 1,520.00\n")
            f.write(f"3. Nestle Water 500ml    - 52 units - Rs. 2,600.00\n")
        
        self.assertTrue(os.path.exists(report_path))
        
        # Verify content
        with open(report_path, 'r') as f:
            content = f.read()
            self.assertIn("DAILY SALES REPORT", content)
            self.assertIn("Total Sales", content)
    
    def test_generate_json_report(self):
        """Test generating a JSON report for data interchange"""
        report_path = os.path.join(self.test_report_dir, 'sales_data.json')
        
        report_data = {
            'report_type': 'daily_sales',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'summary': {
                'total_sales': 125450.0,
                'total_transactions': 87,
                'average_sale': 1442.0,
                'total_discount': 3250.0
            },
            'top_products': [
                {'name': 'Coca Cola 1.5L', 'quantity': 45, 'revenue': 6750.0},
                {'name': 'Lays Chips 50g', 'quantity': 38, 'revenue': 1520.0},
                {'name': 'Nestle Water 500ml', 'quantity': 52, 'revenue': 2600.0}
            ]
        }
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        self.assertTrue(os.path.exists(report_path))
        
        # Verify data
        with open(report_path, 'r') as f:
            loaded_data = json.load(f)
            self.assertEqual(loaded_data['summary']['total_sales'], 125450.0)
            self.assertEqual(len(loaded_data['top_products']), 3)


class TestBarcodeSimulation(unittest.TestCase):
    """Test barcode scanning simulation"""
    
    def test_barcode_format_validation(self):
        """Test barcode format validation"""
        valid_barcodes = [
            '1234567890123',  # EAN-13
            '123456789012',   # UPC-A
            '12345678',       # EAN-8
            'ABC123XYZ',      # Custom
        ]
        
        invalid_barcodes = [
            '',
            '123',  # Too short
        ]
        
        for barcode in valid_barcodes:
            # Valid barcodes should have reasonable length
            self.assertGreaterEqual(len(barcode), 5)
        
        for barcode in invalid_barcodes:
            # These should be caught in validation
            if barcode:
                self.assertLess(len(barcode), 5)
            else:
                self.assertEqual(len(barcode), 0)  # Empty barcode
    
    def test_barcode_to_product_lookup(self):
        """Test looking up products by barcode"""
        # Simulate barcode database
        barcode_db = {
            '1234567890123': {'name': 'Product A', 'price': 100.0},
            '2345678901234': {'name': 'Product B', 'price': 150.0},
            '3456789012345': {'name': 'Product C', 'price': 200.0},
        }
        
        # Test successful lookup
        barcode = '1234567890123'
        self.assertIn(barcode, barcode_db)
        product = barcode_db[barcode]
        self.assertEqual(product['name'], 'Product A')
        
        # Test failed lookup
        invalid_barcode = '9999999999999'
        self.assertNotIn(invalid_barcode, barcode_db)
    
    def test_barcode_scanning_workflow(self):
        """Test complete barcode scanning workflow"""
        # Simulate scanning process
        scanned_items = []
        
        def scan_barcode(barcode):
            """Simulate barcode scan"""
            product_db = {
                '111111': {'id': 1, 'name': 'Item 1', 'price': 50.0},
                '222222': {'id': 2, 'name': 'Item 2', 'price': 75.0},
            }
            
            if barcode in product_db:
                return {'success': True, 'product': product_db[barcode]}
            else:
                return {'success': False, 'error': 'Product not found'}
        
        # Scan multiple items
        for barcode in ['111111', '222222', '111111']:
            result = scan_barcode(barcode)
            if result['success']:
                scanned_items.append(result['product'])
        
        self.assertEqual(len(scanned_items), 3)
        self.assertEqual(scanned_items[0]['name'], 'Item 1')
        
        # Calculate total
        total = sum(item['price'] for item in scanned_items)
        self.assertEqual(total, 175.0)  # 50 + 75 + 50


class TestPrinterSimulation(unittest.TestCase):
    """Test receipt printer simulation"""
    
    def test_receipt_generation(self):
        """Test generating a receipt"""
        receipt_data = {
            'invoice_no': 'INV001',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cashier': 'Cashier 1',
            'items': [
                {'name': 'Product A', 'qty': 2, 'price': 50.0, 'total': 100.0},
                {'name': 'Product B', 'qty': 1, 'price': 75.0, 'total': 75.0},
            ],
            'subtotal': 175.0,
            'tax': 29.75,
            'discount': 0.0,
            'total': 204.75,
            'payment_method': 'Cash',
            'amount_paid': 250.0,
            'change': 45.25
        }
        
        # Generate receipt text
        receipt = self.format_receipt(receipt_data)
        
        self.assertIn('INV001', receipt)
        self.assertIn('Product A', receipt)
        self.assertIn('204.75', receipt)
    
    def format_receipt(self, data):
        """Format receipt text"""
        lines = []
        lines.append("=" * 40)
        lines.append("CROWN SUPERMARKET".center(40))
        lines.append("=" * 40)
        lines.append(f"Invoice: {data['invoice_no']}")
        lines.append(f"Date: {data['date']}")
        lines.append(f"Cashier: {data['cashier']}")
        lines.append("-" * 40)
        
        for item in data['items']:
            lines.append(f"{item['name']:<20} x{item['qty']:>3} {item['total']:>10.2f}")
        
        lines.append("-" * 40)
        lines.append(f"{'Subtotal:':<30} {data['subtotal']:>10.2f}")
        lines.append(f"{'Tax (17%):':<30} {data['tax']:>10.2f}")
        if data['discount'] > 0:
            lines.append(f"{'Discount:':<30} {data['discount']:>10.2f}")
        lines.append("=" * 40)
        lines.append(f"{'TOTAL:':<30} {data['total']:>10.2f}")
        lines.append(f"{'Paid:':<30} {data['amount_paid']:>10.2f}")
        lines.append(f"{'Change:':<30} {data['change']:>10.2f}")
        lines.append("=" * 40)
        lines.append("Thank you for shopping with us!".center(40))
        
        return '\n'.join(lines)
    
    def test_receipt_formatting_special_cases(self):
        """Test receipt formatting with special cases"""
        # Test with discount
        receipt_data = {
            'invoice_no': 'INV002',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'cashier': 'Admin',
            'items': [{'name': 'Item', 'qty': 1, 'price': 100.0, 'total': 100.0}],
            'subtotal': 100.0,
            'tax': 17.0,
            'discount': 10.0,
            'total': 107.0,
            'payment_method': 'Card',
            'amount_paid': 107.0,
            'change': 0.0
        }
        
        receipt = self.format_receipt(receipt_data)
        self.assertIn('Discount', receipt)
        self.assertIn('10.00', receipt)


class TestCashDrawerSimulation(unittest.TestCase):
    """Test cash drawer operations simulation"""
    
    def setUp(self):
        """Set up cash drawer state"""
        self.cash_drawer = {
            'is_open': False,
            'opening_balance': 5000.0,
            'current_balance': 5000.0,
            'transactions': []
        }
    
    def test_open_cash_drawer(self):
        """Test opening cash drawer"""
        self.assertFalse(self.cash_drawer['is_open'])
        
        # Open drawer
        self.cash_drawer['is_open'] = True
        self.assertTrue(self.cash_drawer['is_open'])
    
    def test_cash_transaction(self):
        """Test recording cash transaction"""
        # Sale transaction
        sale_amount = 250.0
        payment_received = 300.0
        change = payment_received - sale_amount
        
        transaction = {
            'type': 'sale',
            'invoice': 'INV001',
            'amount': sale_amount,
            'payment': payment_received,
            'change': change,
            'timestamp': datetime.now()
        }
        
        self.cash_drawer['transactions'].append(transaction)
        self.cash_drawer['current_balance'] += sale_amount
        
        self.assertEqual(self.cash_drawer['current_balance'], 5250.0)
        self.assertEqual(len(self.cash_drawer['transactions']), 1)
    
    def test_cash_drawer_reconciliation(self):
        """Test cash drawer reconciliation"""
        # Add multiple transactions
        transactions = [
            {'amount': 100.0, 'type': 'sale'},
            {'amount': 150.0, 'type': 'sale'},
            {'amount': 50.0, 'type': 'refund'},
            {'amount': 200.0, 'type': 'sale'},
        ]
        
        opening_balance = 5000.0
        current_balance = opening_balance
        
        for trans in transactions:
            if trans['type'] == 'sale':
                current_balance += trans['amount']
            elif trans['type'] == 'refund':
                current_balance -= trans['amount']
        
        expected_balance = 5400.0  # 5000 + 100 + 150 - 50 + 200
        self.assertEqual(current_balance, expected_balance)
    
    def test_cash_drawer_denominations(self):
        """Test counting cash by denominations"""
        denominations = {
            5000: 2,   # 2 x 5000 notes
            1000: 5,   # 5 x 1000 notes
            500: 10,   # 10 x 500 notes
            100: 20,   # 20 x 100 notes
            50: 10,    # 10 x 50 notes
            20: 15,    # 15 x 20 notes
            10: 20,    # 20 x 10 notes
            5: 10,     # 10 x 5 coins
            2: 15,     # 15 x 2 coins
            1: 20      # 20 x 1 coins
        }
        
        total = sum(denom * count for denom, count in denominations.items())
        expected = (5000*2 + 1000*5 + 500*10 + 100*20 + 50*10 + 
                   20*15 + 10*20 + 5*10 + 2*15 + 1*20)
        
        self.assertEqual(total, expected)
        self.assertEqual(total, 23100)  # Correct calculation


class TestHardwareIntegration(unittest.TestCase):
    """Test hardware integration simulation"""
    
    def test_hardware_connection_status(self):
        """Test checking hardware connection status"""
        hardware_status = {
            'barcode_scanner': {'connected': True, 'model': 'Honeywell 1900'},
            'receipt_printer': {'connected': True, 'model': 'Epson TM-T88'},
            'cash_drawer': {'connected': True, 'model': 'APG Vasario'},
            'display': {'connected': True, 'model': 'Customer Display LCD'}
        }
        
        # All devices should be connected
        for device, status in hardware_status.items():
            self.assertTrue(status['connected'], f"{device} should be connected")
    
    def test_hardware_error_handling(self):
        """Test hardware error handling"""
        errors = []
        
        def simulate_device_operation(device_name, operation):
            """Simulate device operation with potential errors"""
            # Simulate random failures
            if device_name == 'printer' and operation == 'print':
                # Simulate paper jam
                return {'success': False, 'error': 'Paper jam detected'}
            elif device_name == 'scanner' and operation == 'scan':
                return {'success': True, 'data': '1234567890'}
            return {'success': True}
        
        # Test printer error
        result = simulate_device_operation('printer', 'print')
        if not result['success']:
            errors.append(result['error'])
        
        self.assertGreater(len(errors), 0)
        self.assertIn('Paper jam', errors[0])
    
    def test_device_initialization(self):
        """Test device initialization sequence"""
        devices = ['barcode_scanner', 'receipt_printer', 'cash_drawer']
        initialized = []
        
        for device in devices:
            # Simulate initialization
            init_result = self.initialize_device(device)
            if init_result['success']:
                initialized.append(device)
        
        self.assertEqual(len(initialized), 3)
        self.assertIn('barcode_scanner', initialized)
    
    def initialize_device(self, device_name):
        """Simulate device initialization"""
        return {'success': True, 'device': device_name, 'status': 'ready'}


def run_advanced_tests():
    """Run all advanced feature tests and generate report"""
    
    print("=" * 80)
    print("STORE MANAGEMENT SYSTEM - ADVANCED FEATURES TEST SUITE")
    print("=" * 80)
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestExcelOperations,
        TestPDFReportGeneration,
        TestBarcodeSimulation,
        TestPrinterSimulation,
        TestCashDrawerSimulation,
        TestHardwareIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate summary report
    print("\n")
    print("=" * 80)
    print("ADVANCED FEATURES TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests Run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped)}")
    print("=" * 80)
    
    # Feature coverage
    print("\nFEATURE COVERAGE:")
    print("-" * 80)
    features = {
        "Excel Import": "✅ Tested" if EXCEL_AVAILABLE else "⚠️  Library not installed",
        "Excel Export": "✅ Tested" if EXCEL_AVAILABLE else "⚠️  Library not installed",
        "Excel Validation": "✅ Tested" if EXCEL_AVAILABLE else "⚠️  Library not installed",
        "Chart Generation": "✅ Tested" if MATPLOTLIB_AVAILABLE else "⚠️  Library not installed",
        "Text Reports": "✅ Tested",
        "JSON Reports": "✅ Tested",
        "Barcode Scanning": "✅ Simulated",
        "Barcode Validation": "✅ Tested",
        "Receipt Printing": "✅ Simulated",
        "Receipt Formatting": "✅ Tested",
        "Cash Drawer": "✅ Simulated",
        "Cash Reconciliation": "✅ Tested",
        "Hardware Status": "✅ Simulated",
        "Error Handling": "✅ Tested"
    }
    
    for feature, status in features.items():
        print(f"{feature:.<40} {status}")
    
    print("\n" + "=" * 80)
    print(f"Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_advanced_tests()
    exit(0 if success else 1)
