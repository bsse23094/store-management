# gui/inventory/excel_import.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from database import fetch_all, execute_query, fetch_one

class ExcelImportWindow:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.window = tk.Toplevel(parent)
        self.window.title("📥 Import Excel - Crown Supermarket")
        self.window.geometry("1000x700")
        self.window.configure(bg="#0d1b2a")
        self.setup_ui()
        self.data = None
        self.column_mapping = {}

    def setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg="#1b263b", height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="📥 Import Excel File", font=("Arial", 16, "bold"), fg="gold", bg="#1b263b").pack(pady=15)

        # File Selection
        file_frame = tk.Frame(self.window, bg="#0d1b2a")
        file_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(file_frame, text="📁 Select Excel File", font=("Arial", 12, "bold"), bg="#1E90FF", fg="white",
                  command=self.select_file).pack(side=tk.LEFT, padx=5)

        self.file_label = tk.Label(file_frame, text="No file selected", font=("Arial", 10), fg="white", bg="#0d1b2a")
        self.file_label.pack(side=tk.LEFT, padx=10)

        # Mapping Frame
        self.mapping_frame = tk.Frame(self.window, bg="white", relief=tk.RAISED, borderwidth=1)
        self.mapping_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Action Buttons
        btn_frame = tk.Frame(self.window, bg="#0d1b2a")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        self.import_btn = tk.Button(btn_frame, text="💾 Import Data", font=("Arial", 12, "bold"), bg="#2E8B57", fg="white",
                                   command=self.import_data, state=tk.DISABLED)
        self.import_btn.pack(side=tk.RIGHT, padx=5)

        self.preview_btn = tk.Button(btn_frame, text="🔍 Preview Data", font=("Arial", 12, "bold"), bg="#FFA500", fg="white",
                                    command=self.show_preview, state=tk.DISABLED)
        self.preview_btn.pack(side=tk.RIGHT, padx=5)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return

        try:
            # Read Excel file
            if file_path.endswith('.xlsx'):
                self.data = pd.read_excel(file_path, engine='openpyxl')
            else:
                self.data = pd.read_excel(file_path, engine='xlrd')
            
            self.file_label.config(text=f"Selected: {file_path.split('/')[-1]}")
            self.setup_column_mapping()
            self.preview_btn.config(state=tk.NORMAL)
            self.import_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read Excel file:\n{str(e)}")

    def setup_column_mapping(self):
        """Create column mapping interface"""
        # Clear existing widgets
        for widget in self.mapping_frame.winfo_children():
            widget.destroy()

        if self.data is None or self.data.empty:
            tk.Label(self.mapping_frame, text="No data to map", font=("Arial", 12), bg="white").pack(pady=20)
            return

        tk.Label(self.mapping_frame, text="Map Excel Columns to Product Fields", 
                 font=("Arial", 14, "bold"), bg="white", fg="#0d1b2a").pack(pady=10)

        # Get Excel columns
        excel_columns = list(self.data.columns)
        product_fields = ["Barcode", "Company", "Name", "Variant", "Size", "Unit", "Category", "Supplier", "Cost", "Sale", "Stock"]

        # Load dropdown options
        categories = [row[0] for row in fetch_all("SELECT name FROM categories ORDER BY name")]
        suppliers = [row[0] for row in fetch_all("SELECT name FROM suppliers ORDER BY name")]
        companies = [row[0] for row in fetch_all("SELECT DISTINCT company FROM products WHERE company IS NOT NULL AND company != '' ORDER BY company")]
        units = [row[0] for row in fetch_all("SELECT name FROM uoms ORDER BY name")]

        # Create mapping frame
        mapping_container = tk.Frame(self.mapping_frame, bg="white")
        mapping_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        canvas = tk.Canvas(mapping_container, bg="white")
        scrollbar = ttk.Scrollbar(mapping_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create mapping rows
        self.mapping_vars = {}
        for i, field in enumerate(product_fields):
            row_frame = tk.Frame(scrollable_frame, bg="white")
            row_frame.pack(fill=tk.X, pady=5)

            tk.Label(row_frame, text=field, font=("Arial", 11, "bold"), bg="white", width=15, anchor="w").pack(side=tk.LEFT, padx=(0, 10))

            # Create combobox with Excel columns + "Skip"
            options = ["Skip"] + excel_columns
            var = tk.StringVar(value="Skip")
            self.mapping_vars[field] = var
            
            combo = ttk.Combobox(row_frame, textvariable=var, values=options, state="readonly", width=30)
            combo.pack(side=tk.LEFT)
            
            # Auto-map if column names match
            for col in excel_columns:
                if field.lower() in col.lower() or col.lower() in field.lower():
                    var.set(col)
                    break

    def show_preview(self):
        """Show data preview"""
        if self.data is None or self.data.empty:
            messagebox.showwarning("No Data", "No data to preview.")
            return

        # Create preview window
        preview = tk.Toplevel(self.window)
        preview.title("🔍 Data Preview")
        preview.geometry("800x600")
        preview.configure(bg="white")

        tk.Label(preview, text="Preview (First 5 Rows)", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        # Create treeview
        tree_frame = tk.Frame(preview, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = list(self.data.columns)
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # Insert first 5 rows
        for i, row in self.data.head(5).iterrows():
            tree.insert("", "end", values=list(row))

        tree.pack(fill=tk.BOTH, expand=True)

        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

    def import_data(self):
        """Import mapped data to database"""
        if self.data is None or self.data.empty:
            messagebox.showwarning("No Data", "No data to import.")
            return

        # Get mapping
        mapping = {}
        for field, var in self.mapping_vars.items():
            excel_col = var.get()
            if excel_col != "Skip":
                mapping[field] = excel_col

        if not mapping:
            messagebox.showwarning("No Mapping", "Please map at least one column.")
            return

        # Confirm import
        if not messagebox.askyesno("Confirm Import", f"Import {len(self.data)} rows?"):
            return

        try:
            imported_count = 0
            for _, row in self.data.iterrows():
                # Extract values based on mapping
                values = {}
                for field, excel_col in mapping.items():
                    values[field] = str(row[excel_col]).strip() if pd.notna(row[excel_col]) else ""

                # Skip if no name
                if not values.get("Name", "").strip():
                    continue

                # Get values with defaults
                barcode = values.get("Barcode", "")
                company = values.get("Company", "")
                name = values.get("Name", "")
                variant = values.get("Variant", "")
                size = values.get("Size", "")
                unit = values.get("Unit", "Piece")
                category = values.get("Category", "")
                supplier = values.get("Supplier", "")
                cost = values.get("Cost", "0")
                sale = values.get("Sale", "0")
                stock = values.get("Stock", "0")

                # Convert to numbers
                try:
                    cost_val = float(cost) if cost else 0.0
                    sale_val = float(sale) if sale else 0.0
                    stock_val = float(stock) if stock else 0.0
                except ValueError:
                    continue  # Skip invalid rows

                # Get IDs
                category_id = None
                if category:
                    cat = fetch_one("SELECT id FROM categories WHERE name = ?", (category,))
                    if cat:
                        category_id = cat[0]

                supplier_id = None
                if supplier:
                    sup = fetch_one("SELECT id FROM suppliers WHERE name = ?", (supplier,))
                    if sup:
                        supplier_id = sup[0]

                unit_id = 1
                if unit:
                    uom = fetch_one("SELECT id FROM uoms WHERE name = ?", (unit,))
                    if uom:
                        unit_id = uom[0]

                # Insert product
                product_id = execute_query("""
                    INSERT INTO products (name, barcode, company, category_id, supplier_id, tax_id, base_uom_id, purchase_uom_id, cost_price, selling_price, stock)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, barcode or None, company or None, category_id, supplier_id, 1, unit_id, unit_id, cost_val, sale_val, stock_val))

                # Insert variants
                if variant:
                    execute_query("""
                        INSERT INTO product_variants (product_id, variant_name, variant_value, barcode, price, stock)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (product_id, "Variant", variant, None, sale_val, stock_val))

                if size:
                    execute_query("""
                        INSERT INTO product_variants (product_id, variant_name, variant_value, barcode, price, stock)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (product_id, "Size", size, None, sale_val, stock_val))

                imported_count += 1

            messagebox.showinfo("Success", f"✅ {imported_count} items imported successfully!")
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Import failed:\n{str(e)}")