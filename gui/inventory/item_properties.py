# gui/inventory/item_properties.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog  # ✅ Added simpledialog
from database import fetch_all, fetch_one, execute_query

class ItemPropertiesWindow:
    def __init__(self, parent, product_id, user):
        self.product_id = product_id
        self.user = user
        self.window = tk.Toplevel(parent)
        self.window.title("PropertyParams Product Properties")
        self.window.geometry("900x700")
        self.window.configure(bg="#0d1b2a")
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.basic_frame = tk.Frame(notebook, bg="white")
        notebook.add(self.basic_frame, text="Basic Info")

        self.barcodes_frame = tk.Frame(notebook, bg="white")
        notebook.add(self.barcodes_frame, text="Barcodes")

        self.suppliers_frame = tk.Frame(notebook, bg="white")
        notebook.add(self.suppliers_frame, text="Suppliers & Cost")

        self.price_frame = tk.Frame(notebook, bg="white")
        notebook.add(self.price_frame, text="Price & Tax")

        self.history_frame = tk.Frame(notebook, bg="white")
        notebook.add(self.history_frame, text="Transaction History")

        self.build_basic_tab()
        self.build_barcodes_tab()
        self.build_suppliers_tab()
        self.build_price_tab()
        self.build_history_tab()

    def build_basic_tab(self):
        tk.Label(self.basic_frame, text="Product Details", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        fields = [
            ("Product ID:", "id_var"),
            ("Name:", "name_var"),
            ("Company (Manufacturer):", "company_var"),
            ("Variant:", "variant_var"),
            ("Size:", "size_var"),
            ("Base Unit:", "unit_var"),
            ("Category:", "category_var"),
        ]

        self.basic_vars = {}
        for label_text, var_name in fields:
            frame = tk.Frame(self.basic_frame, bg="white")
            frame.pack(fill=tk.X, padx=20, pady=5)
            tk.Label(frame, text=label_text, font=("Arial", 11), bg="white", width=25, anchor="w").pack(side=tk.LEFT)
            var = tk.StringVar()
            self.basic_vars[var_name] = var
            tk.Entry(frame, textvariable=var, font=("Arial", 11), width=40).pack(side=tk.LEFT)

        tk.Button(self.basic_frame, text="💾 Save Changes", font=("Arial", 12, "bold"), bg="#2E8B57", fg="white",
                  command=self.save_basic).pack(pady=20)

    def build_price_tab(self):
        tk.Label(self.price_frame, text="Price & Tax Configuration", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        # Cost and Selling Price
        price_frame = tk.Frame(self.price_frame, bg="white")
        price_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(price_frame, text="Cost Price:", font=("Arial", 11), bg="white", width=20, anchor="w").pack(side=tk.LEFT)
        self.cost_price_var = tk.DoubleVar(value=0.0)
        tk.Entry(price_frame, textvariable=self.cost_price_var, font=("Arial", 11), width=15).pack(side=tk.LEFT, padx=10)

        tk.Label(price_frame, text="Selling Price:", font=("Arial", 11), bg="white", width=20, anchor="w").pack(side=tk.LEFT, padx=(30,10))
        self.selling_price_var = tk.DoubleVar(value=0.0)
        tk.Entry(price_frame, textvariable=self.selling_price_var, font=("Arial", 11), width=15).pack(side=tk.LEFT)

        # GST Configuration
        gst_frame = tk.Frame(self.price_frame, bg="white")
        gst_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(gst_frame, text="GST Rate (%):", font=("Arial", 11), bg="white", width=20, anchor="w").pack(side=tk.LEFT)
        self.gst_rate_var = tk.DoubleVar(value=17.0)
        tk.Entry(gst_frame, textvariable=self.gst_rate_var, font=("Arial", 11), width=10).pack(side=tk.LEFT, padx=10)

        tk.Label(gst_frame, text="Tax Type:", font=("Arial", 11), bg="white", width=20, anchor="w").pack(side=tk.LEFT, padx=(30,10))
        self.tax_type_var = tk.StringVar(value="exclusive")
        tax_combo = ttk.Combobox(gst_frame, textvariable=self.tax_type_var, values=["exclusive", "inclusive"], state="readonly", width=15)
        tax_combo.pack(side=tk.LEFT)

        # Save Button
        tk.Button(self.price_frame, text="💾 Save Price & Tax", font=("Arial", 12, "bold"), bg="#2E8B57", fg="white",
                  command=self.save_price_tax).pack(pady=20)




    def build_barcodes_tab(self):
        tk.Label(self.barcodes_frame, text="Barcodes", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        barcode_frame = tk.Frame(self.barcodes_frame, bg="white")
        barcode_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.barcode_tree = ttk.Treeview(barcode_frame, columns=("Barcode", "Type"), show="headings", height=8)
        self.barcode_tree.heading("Barcode", text="Barcode")
        self.barcode_tree.heading("Type", text="Type")
        self.barcode_tree.column("Barcode", width=200)
        self.barcode_tree.column("Type", width=100)
        self.barcode_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scroll = ttk.Scrollbar(barcode_frame, orient=tk.VERTICAL, command=self.barcode_tree.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.barcode_tree.configure(yscrollcommand=v_scroll.set)

        btn_frame = tk.Frame(self.barcodes_frame, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="➕ Add Barcode", command=self.add_barcode).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑️ Remove Barcode", command=self.remove_barcode).pack(side=tk.LEFT, padx=5)

    def build_suppliers_tab(self):
        tk.Label(self.suppliers_frame, text="Suppliers & Cost Prices", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        supplier_frame = tk.Frame(self.suppliers_frame, bg="white")
        supplier_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.supplier_tree = ttk.Treeview(supplier_frame, columns=("Supplier", "Cost Price", "Last Updated"), show="headings", height=8)
        self.supplier_tree.heading("Supplier", text="Supplier")
        self.supplier_tree.heading("Cost Price", text="Cost Price")
        self.supplier_tree.heading("Last Updated", text="Last Updated")
        self.supplier_tree.column("Supplier", width=200)
        self.supplier_tree.column("Cost Price", width=120)
        self.supplier_tree.column("Last Updated", width=150)
        self.supplier_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scroll = ttk.Scrollbar(supplier_frame, orient=tk.VERTICAL, command=self.supplier_tree.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.supplier_tree.configure(yscrollcommand=v_scroll.set)

        btn_frame = tk.Frame(self.suppliers_frame, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="➕ Add Supplier Price", command=self.add_supplier_price).pack(side=tk.LEFT, padx=5)

    def build_price_tab(self):
        tk.Label(self.price_frame, text="Sale Price History", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        price_frame = tk.Frame(self.price_frame, bg="white")
        price_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.price_tree = ttk.Treeview(price_frame, columns=("Price", "Updated By", "Date"), show="headings", height=8)
        self.price_tree.heading("Price", text="Sale Price")
        self.price_tree.heading("Updated By", text="Updated By")
        self.price_tree.heading("Date", text="Date")
        self.price_tree.column("Price", width=120)
        self.price_tree.column("Updated By", width=150)
        self.price_tree.column("Date", width=180)
        self.price_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scroll = ttk.Scrollbar(price_frame, orient=tk.VERTICAL, command=self.price_tree.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.price_tree.configure(yscrollcommand=v_scroll.set)

        tk.Button(self.price_frame, text="💰 Update Sale Price", command=self.update_sale_price).pack(pady=10)

    def build_history_tab(self):
        tk.Label(self.history_frame, text="Transaction History", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        tk.Label(self.history_frame, text="Recent Sales", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=20)
        sales_frame = tk.Frame(self.history_frame, bg="white")
        sales_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        self.sales_tree = ttk.Treeview(sales_frame, columns=("Invoice", "Qty", "Price", "Date"), show="headings", height=5)
        self.sales_tree.heading("Invoice", text="Invoice")
        self.sales_tree.heading("Qty", text="Qty")
        self.sales_tree.heading("Price", text="Price")
        self.sales_tree.heading("Date", text="Date")
        self.sales_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(self.history_frame, text="Recent Purchases", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=20, pady=(20,0))
        purchase_frame = tk.Frame(self.history_frame, bg="white")
        purchase_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        self.purchase_tree = ttk.Treeview(purchase_frame, columns=("Supplier", "Qty", "Cost", "Date"), show="headings", height=5)
        self.purchase_tree.heading("Supplier", text="Supplier")
        self.purchase_tree.heading("Qty", text="Qty")
        self.purchase_tree.heading("Cost", text="Cost")
        self.purchase_tree.heading("Date", text="Date")
        self.purchase_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def load_data(self):
        # Basic Info
        product = fetch_one("SELECT id, name, company, category_id, cost_price, selling_price, gst_rate, tax_type FROM products WHERE id = ?", (self.product_id,))
        if product:
            self.basic_vars["id_var"].set(product[0])
            self.basic_vars["name_var"].set(product[1])
            self.basic_vars["company_var"].set(product[2] or "")
            self.cost_price_var.set(product[4] or 0.0)
            self.selling_price_var.set(product[5] or 0.0)
            self.gst_rate_var.set(product[6] or 17.0)
            self.tax_type_var.set(product[7] or "exclusive")
            
            cat = fetch_one("SELECT name FROM categories WHERE id = ?", (product[3],))
            self.basic_vars["category_var"].set(cat[0] if cat else "")

            # Load Barcodes - MAIN BARCODE + VARIANTS
            self.load_barcodes(product[4])  # product[4] is main barcode

        # Variant/Size
        variant = fetch_one("SELECT variant_value FROM product_variants WHERE product_id = ? AND variant_name = 'Variant' LIMIT 1", (self.product_id,))
        if variant:
            self.basic_vars["variant_var"].set(variant[0])
        else:
            self.basic_vars["variant_var"].set("")

        size = fetch_one("SELECT variant_value FROM product_variants WHERE product_id = ? AND variant_name = 'Size' LIMIT 1", (self.product_id,))
        if size:
            self.basic_vars["size_var"].set(size[0])
        else:
            self.basic_vars["size_var"].set("")

        # Base Unit
        uom = fetch_one("SELECT u.name FROM uoms u JOIN products p ON p.base_uom_id = u.id WHERE p.id = ?", (self.product_id,))
        self.basic_vars["unit_var"].set(uom[0] if uom else "Piece")

        # Suppliers & Cost
        suppliers = fetch_all("""
            SELECT s.name, sp.cost_price, sp.effective_date
            FROM supplier_prices sp
            JOIN suppliers s ON sp.supplier_id = s.id
            WHERE sp.product_id = ?
            ORDER BY sp.effective_date DESC
        """, (self.product_id,))
        for sup in suppliers:
            self.supplier_tree.insert("", "end", values=(sup[0], f"Rs. {sup[1]:.2f}", sup[2]))

        # Price History
        prices = fetch_all("""
            SELECT ph.selling_price, u.full_name, ph.effective_date
            FROM price_history ph
            JOIN users u ON ph.updated_by = u.id
            WHERE ph.product_id = ?
            ORDER BY ph.effective_date DESC
        """, (self.product_id,))
        for price in prices:
            self.price_tree.insert("", "end", values=(f"Rs. {price[0]:.2f}", price[1], price[2]))

        # Sales History
        sales = fetch_all("""
            SELECT s.invoice_no, si.quantity, si.unit_price, s.created_at
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            WHERE si.product_id = ?
            ORDER BY s.created_at DESC
            LIMIT 5
        """, (self.product_id,))
        for sale in sales:
            self.sales_tree.insert("", "end", values=(sale[0], sale[1], f"Rs. {sale[2]:.2f}", sale[3]))

        # Purchase History
        purchases = fetch_all("""
            SELECT s.name, 100, sp.cost_price, sp.effective_date
            FROM supplier_prices sp
            JOIN suppliers s ON sp.supplier_id = s.id
            WHERE sp.product_id = ?
            ORDER BY sp.effective_date DESC
            LIMIT 5
        """, (self.product_id,))
        for pur in purchases:
            self.purchase_tree.insert("", "end", values=(pur[0], pur[1], f"Rs. {pur[2]:.2f}", pur[2]))

    def load_barcodes(self, main_barcode):
        """Load main barcode + variant barcodes"""
        # Clear existing
        for item in self.barcode_tree.get_children():
            self.barcode_tree.delete(item)
        
        # Add main barcode
        if main_barcode:
            self.barcode_tree.insert("", "end", values=(main_barcode, "Main Product"))
        
        # Add variant barcodes
        barcodes = fetch_all("SELECT barcode FROM product_variants WHERE product_id = ? AND barcode IS NOT NULL AND barcode != ''", (self.product_id,))
        for bc in barcodes:
            self.barcode_tree.insert("", "end", values=(bc[0], "Variant"))

    def save_price_tax(self):
        try:
            cost_price = self.cost_price_var.get()
            selling_price = self.selling_price_var.get()
            gst_rate = self.gst_rate_var.get()
            tax_type = self.tax_type_var.get()
            
            execute_query("""
                UPDATE products 
                SET cost_price = ?, selling_price = ?, gst_rate = ?, tax_type = ? 
                WHERE id = ?
            """, (cost_price, selling_price, gst_rate, tax_type, self.product_id))
            
            messagebox.showinfo("Success", "Price and tax settings updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")

    def save_basic(self):
        try:
            name = self.basic_vars["name_var"].get()
            company = self.basic_vars["company_var"].get()
            execute_query("UPDATE products SET name = ?, company = ? WHERE id = ?", (name, company, self.product_id))
            messagebox.showinfo("Success", "Basic info updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")

    def add_barcode(self):
        # ✅ FIXED: Use simpledialog.askstring
        barcode = simpledialog.askstring("Add Barcode", "Enter new barcode:")
        if barcode:
            try:
                execute_query("INSERT INTO product_variants (product_id, variant_name, variant_value, barcode, price, stock) VALUES (?, ?, ?, ?, ?, ?)",
                              (self.product_id, "Barcode", "Additional", barcode, 0.0, 0))
                self.barcode_tree.insert("", "end", values=(barcode, "Additional"))
                messagebox.showinfo("Success", "Barcode added!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add barcode: {str(e)}")

    def remove_barcode(self):
        selection = self.barcode_tree.selection()
        if not selection:
            return
        barcode = self.barcode_tree.item(selection[0], "values")[0]
        if messagebox.askyesno("Confirm", f"Remove barcode {barcode}?"):
            try:
                # Try to delete from variants first
                execute_query("DELETE FROM product_variants WHERE barcode = ? AND product_id = ?", (barcode, self.product_id))
                # If it's the main barcode, clear it
                product = fetch_one("SELECT barcode FROM products WHERE id = ?", (self.product_id,))
                if product and product[0] == barcode:
                    execute_query("UPDATE products SET barcode = NULL WHERE id = ?", (self.product_id,))
                self.barcode_tree.delete(selection[0])
                messagebox.showinfo("Success", "Barcode removed!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove barcode: {str(e)}")

    def add_supplier_price(self):
        messagebox.showinfo("Coming Soon", "Supplier price entry will be implemented.")

    def update_sale_price(self):
        current = self.basic_vars.get("sale_price_var", tk.StringVar(value="0.00")).get()
        new_price = simpledialog.askstring("Update Price", "Enter new sale price:", initialvalue=current)
        if new_price:
            try:
                price_val = float(new_price)
                execute_query("UPDATE products SET selling_price = ? WHERE id = ?", (price_val, self.product_id))
                execute_query("INSERT INTO price_history (product_id, selling_price, updated_by) VALUES (?, ?, ?)",
                              (self.product_id, price_val, self.user['id']))
                messagebox.showinfo("Success", "Sale price updated!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid price: {str(e)}")