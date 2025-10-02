# gui/ordering/purchase_orders.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from database import fetch_all, fetch_one, execute_query
from utils import clear_window

class PurchaseOrderWindow:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.po_number = f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.items = []
        self.setup_ui()
        self.load_suppliers()

    def setup_ui(self):
        clear_window(self.root)
        self.root.title(f"📝 Create Purchase Order - {self.po_number}")
        self.root.configure(bg="#0d1b2a")

        # Header
        header = tk.Frame(self.root, bg="#1b263b", height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text=f"📝 CREATE PURCHASE ORDER: {self.po_number}", font=("Arial", 16, "bold"), 
                 fg="gold", bg="#1b263b").pack(pady=15)

        # Supplier Selection
        supplier_frame = tk.Frame(self.root, bg="white")
        supplier_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(supplier_frame, text="Select Supplier:", font=("Arial", 12), bg="white").pack(side=tk.LEFT)
        self.supplier_var = tk.StringVar()
        self.supplier_combo = ttk.Combobox(supplier_frame, textvariable=self.supplier_var, state="readonly", width=30)
        self.supplier_combo.pack(side=tk.LEFT, padx=10)

        # Product Selection
        product_frame = tk.Frame(self.root, bg="white")
        product_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(product_frame, text="Add Product:", font=("Arial", 12), bg="white").pack(side=tk.LEFT)
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(product_frame, textvariable=self.product_var, state="readonly", width=30)
        self.product_combo.pack(side=tk.LEFT, padx=10)

        tk.Label(product_frame, text="Qty:", font=("Arial", 12), bg="white").pack(side=tk.LEFT, padx=(10,5))
        self.qty_var = tk.DoubleVar(value=1.0)
        tk.Entry(product_frame, textvariable=self.qty_var, width=10).pack(side=tk.LEFT)

        tk.Button(product_frame, text="➕ Add to PO", command=self.add_item).pack(side=tk.LEFT, padx=10)

        # Items Table
        table_frame = tk.Frame(self.root, bg="white", relief=tk.RAISED, borderwidth=1)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("Product", "Qty Ordered", "Cost Price", "Total")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Totals
        totals_frame = tk.Frame(self.root, bg="white")
        totals_frame.pack(fill=tk.X, padx=20, pady=10)

        self.total_var = tk.StringVar(value="Total: Rs. 0.00")
        tk.Label(totals_frame, textvariable=self.total_var, font=("Arial", 14, "bold"), fg="green").pack()

        # Action Buttons
        btn_frame = tk.Frame(self.root, bg="white")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(btn_frame, text="💾 Save Draft", font=("Arial", 12), bg="#FFA500", fg="white",
                  command=self.save_draft).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="📤 Send PO", font=("Arial", 12), bg="#2E8B57", fg="white",
                  command=self.send_po).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="❌ Cancel", font=("Arial", 12), bg="#A9A9A9", fg="white",
                  command=self.go_back).pack(side=tk.LEFT, padx=5)

    def load_suppliers(self):
        suppliers = [row[0] for row in fetch_all("SELECT name FROM suppliers ORDER BY name")]
        self.supplier_combo['values'] = suppliers
        self.supplier_combo.bind("<<ComboboxSelected>>", self.load_products)

    def load_products(self, event=None):
        supplier_name = self.supplier_var.get()
        if not supplier_name:
            return

        # Get supplier ID
        supplier = fetch_one("SELECT id FROM suppliers WHERE name = ?", (supplier_name,))
        if not supplier:
            return

        # Load products from this supplier
        products = fetch_all("""
            SELECT p.name, p.id 
            FROM products p 
            WHERE p.supplier_id = ? 
            ORDER BY p.name
        """, (supplier[0],))
        
        product_names = [p[0] for p in products]
        self.product_combo['values'] = product_names
        self.products_map = {p[0]: p[1] for p in products}

    def add_item(self):
        product_name = self.product_var.get()
        qty = self.qty_var.get()
        
        if not product_name or qty <= 0:
            messagebox.showwarning("Invalid Input", "Please select a product and enter valid quantity.")
            return

        # Get product ID and cost price
        product_id = self.products_map.get(product_name)
        if not product_id:
            return

        # Get cost price (from supplier_prices or products table)
        cost_price = 0.0
        price_record = fetch_one("""
            SELECT cost_price FROM supplier_prices 
            WHERE product_id = ? AND supplier_id = (
                SELECT id FROM suppliers WHERE name = ?
            ) ORDER BY effective_date DESC LIMIT 1
        """, (product_id, self.supplier_var.get()))
        
        if price_record:
            cost_price = price_record[0]
        else:
            product = fetch_one("SELECT cost_price FROM products WHERE id = ?", (product_id,))
            if product:
                cost_price = product[0]

        # Check if already in PO
        existing_item = None
        for item in self.items:
            if item['product_id'] == product_id:
                existing_item = item
                break

        if existing_item:
            existing_item['qty'] += qty
            existing_item['total'] = existing_item['qty'] * existing_item['cost_price']
        else:
            item = {
                'product_id': product_id,
                'product_name': product_name,
                'qty': qty,
                'cost_price': cost_price,
                'total': qty * cost_price
            }
            self.items.append(item)

        self.update_display()

    def update_display(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        total = 0
        for item in self.items:
            self.tree.insert("", "end", values=(
                item['product_name'],
                f"{item['qty']:.2f}",
                f"Rs. {item['cost_price']:.2f}",
                f"Rs. {item['total']:.2f}"
            ))
            total += item['total']

        self.total_var.set(f"Total: Rs. {total:,.2f}")

    def save_draft(self):
        if not self.items:
            messagebox.showwarning("Empty PO", "Add items before saving.")
            return

        if not self.supplier_var.get():
            messagebox.showwarning("No Supplier", "Please select a supplier.")
            return

        supplier = fetch_one("SELECT id FROM suppliers WHERE name = ?", (self.supplier_var.get(),))
        if not supplier:
            return

        try:
            # Create PO
            po_id = execute_query("""
                INSERT INTO purchase_orders (po_number, supplier_id, total_amount, created_by, status)
                VALUES (?, ?, ?, ?, 'draft')
            """, (self.po_number, supplier[0], float(self.total_var.get().split()[-1].replace(',', '')), self.user['id']))

            # Add items
            for item in self.items:
                execute_query("""
                    INSERT INTO po_items (po_id, product_id, quantity_ordered, cost_price)
                    VALUES (?, ?, ?, ?)
                """, (po_id, item['product_id'], item['qty'], item['cost_price']))

            messagebox.showinfo("Success", f"Draft PO {self.po_number} saved!")
            self.go_back()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PO: {str(e)}")

    def send_po(self):
        if not self.items:
            messagebox.showwarning("Empty PO", "Add items before sending.")
            return

        if not self.supplier_var.get():
            messagebox.showwarning("No Supplier", "Please select a supplier.")
            return

        if messagebox.askyesno("Confirm", "Send this PO to supplier?"):
            self.save_draft()  # This also sets status to 'sent' in real implementation

    def go_back(self):
        from .ordering_main import OrderingDashboard
        OrderingDashboard(self.root, self.user)