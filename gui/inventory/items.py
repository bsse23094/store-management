# gui/inventory/items.py
import tkinter as tk
from tkinter import ttk, messagebox, Menu, simpledialog
from database import fetch_all, fetch_one, execute_query

class ItemsManager:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.setup_ui()
        self.load_filters()
        self.load_items()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.parent, bg="#1b263b", height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="📦 Product Items", font=("Arial", 16, "bold"), fg="gold", bg="#1b263b").pack(pady=15)

        # Filter Bar
        filter_frame = tk.Frame(self.parent, bg="white")
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        # Category Filter
        tk.Label(filter_frame, text="Category:", font=("Arial", 10), bg="white").pack(side=tk.LEFT)
        self.category_var = tk.StringVar(value="All")
        self.category_combo = ttk.Combobox(filter_frame, textvariable=self.category_var, state="readonly", width=20)
        self.category_combo.pack(side=tk.LEFT, padx=5)

        # Supplier Filter
        tk.Label(filter_frame, text="Supplier:", font=("Arial", 10), bg="white").pack(side=tk.LEFT, padx=(20,5))
        self.supplier_var = tk.StringVar(value="All")
        self.supplier_combo = ttk.Combobox(filter_frame, textvariable=self.supplier_var, state="readonly", width=20)
        self.supplier_combo.pack(side=tk.LEFT, padx=5)

        # Company Filter
        tk.Label(filter_frame, text="Company:", font=("Arial", 10), bg="white").pack(side=tk.LEFT, padx=(20,5))
        self.company_var = tk.StringVar(value="All")
        self.company_combo = ttk.Combobox(filter_frame, textvariable=self.company_var, state="readonly", width=20)
        self.company_combo.pack(side=tk.LEFT, padx=5)

        # Tax Method Filter
        tk.Label(filter_frame, text="Tax Method:", font=("Arial", 10), bg="white").pack(side=tk.LEFT, padx=(20,5))
        self.tax_method_var = tk.StringVar(value="All")
        self.tax_method_combo = ttk.Combobox(filter_frame, textvariable=self.tax_method_var, state="readonly", width=25)
        self.tax_method_combo['values'] = [
            "All",
            "Applicable on Trade Price",
            "Included in Retail Price"
        ]
        self.tax_method_combo.pack(side=tk.LEFT, padx=5)

        # Bind events
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self.load_items())
        self.supplier_combo.bind("<<ComboboxSelected>>", lambda e: self.load_items())
        self.company_combo.bind("<<ComboboxSelected>>", lambda e: self.load_items())
        self.tax_method_combo.bind("<<ComboboxSelected>>", lambda e: self.load_items())

        # Action Buttons
        btn_frame = tk.Frame(self.parent, bg="white")
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(btn_frame, text="➕ Add Item", font=("Arial", 11, "bold"), bg="#2E8B57", fg="white",
                  command=self.add_item).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="📊 Bulk Add", font=("Arial", 11, "bold"), bg="#1E90FF", fg="white",
                  command=self.bulk_add).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="📥 Import Excel", font=("Arial", 11, "bold"), bg="#FFA500", fg="white",
                  command=self.import_excel).pack(side=tk.LEFT, padx=5)

        # Treeview
        tree_frame = tk.Frame(self.parent, bg="white", relief=tk.RAISED, borderwidth=1)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.columns = ("ID", "Barcode", "Company", "Name", "Variant", "Size", "Unit", "Category", "Supplier", "Cost", "Sale", "Stock", "Tax Method", "Location", "PropertyParams")
        self.tree = ttk.Treeview(tree_frame, columns=self.columns, show="headings", height=20)
        
        col_widths = {
            "ID": 50,
            "Barcode": 120,
            "Company": 150,
            "Name": 180,
            "Variant": 100,
            "Size": 80,
            "Unit": 80,
            "Category": 120,
            "Supplier": 120,
            "Cost": 80,
            "Sale": 80,
            "Stock": 80,
            "Tax Method": 120,
            "Location": 100,
            "PropertyParams": 100
        }
        
        for col in self.columns:
            self.tree.heading(col, text=col)
            width = col_widths.get(col, 100)
            anchor = "e" if col in ("Cost", "Sale", "Stock") else "center" if col == "ID" else "w"
            self.tree.column(col, width=width, anchor=anchor)

        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background="white", 
                        foreground="#0d1b2a", 
                        fieldbackground="white", 
                        font=("Arial", 10),
                        rowheight=26)
        style.configure("Treeview.Heading", 
                        background="#1b263b", 
                        foreground="gold", 
                        font=("Arial", 10, "bold"),
                        padding=3)
        style.map("Treeview", 
                  background=[('selected', '#0d1b2a')], 
                  foreground=[('selected', 'gold')])

        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Button-1>", self.on_tree_click)

        self.context_menu = Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="✏️ Edit", command=self.start_edit)
        self.context_menu.add_command(label="🗑️ Delete", command=self.delete_item)

        # Initialize attributes
        self.editing_item = None
        self.editing_column = None
        self.entry = None
        self.category_edit_combo = None
        self.supplier_edit_combo = None
        self.edit_columns_order = ["#2", "#3", "#4", "#5", "#6", "#7", "#8", "#9", "#10", "#11", "#12", "#13", "#14"]

    def load_filters(self):
        try:
            categories = ["All"] + [row[0] for row in fetch_all("SELECT name FROM categories ORDER BY name")]
            self.category_combo['values'] = categories

            suppliers = ["All"] + [row[0] for row in fetch_all("SELECT name FROM suppliers ORDER BY name")]
            self.supplier_combo['values'] = suppliers

            companies = ["All"] + [row[0] for row in fetch_all("SELECT DISTINCT company FROM products WHERE company IS NOT NULL AND company != '' ORDER BY company")]
            self.company_combo['values'] = companies
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load filters: {str(e)}")

    def load_items(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            base_query = """
                SELECT 
                    p.id, 
                    p.barcode, 
                    p.company, 
                    p.name,
                    (SELECT pv1.variant_value FROM product_variants pv1 WHERE pv1.product_id = p.id AND pv1.variant_name = 'Variant' LIMIT 1) AS variant,
                    (SELECT pv2.variant_value FROM product_variants pv2 WHERE pv2.product_id = p.id AND pv2.variant_name = 'Size' LIMIT 1) AS size,
                    u.name AS unit,
                    c.name AS category, 
                    s.name AS supplier,
                    p.cost_price, 
                    p.selling_price, 
                    p.stock,
                    c.location_tag,
                    p.tax_type
                FROM products p
                LEFT JOIN uoms u ON p.base_uom_id = u.id
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE 1=1
            """
            conditions = []
            params = []

            if self.category_var.get() != "All":
                conditions.append("c.name = ?")
                params.append(self.category_var.get())
            if self.supplier_var.get() != "All":
                conditions.append("s.name = ?")
                params.append(self.supplier_var.get())
            if self.company_var.get() != "All":
                conditions.append("p.company = ?")
                params.append(self.company_var.get())
            if self.tax_method_var.get() != "All":
                if self.tax_method_var.get() == "Applicable on Trade Price":
                    conditions.append("p.tax_type = 'exclusive'")
                elif self.tax_method_var.get() == "Included in Retail Price":
                    conditions.append("p.tax_type = 'inclusive'")

            if conditions:
                base_query += " AND " + " AND ".join(conditions)
            base_query += " ORDER BY p.name"

            items = fetch_all(base_query, params)

            for item in items:
                # Safe numeric conversion
                try:
                    cost_val = float(item[9]) if item[9] not in (None, "") else 0.0
                    cost = f"Rs. {cost_val:.2f}"
                except (ValueError, TypeError):
                    cost = "Rs. 0.00"
                    
                try:
                    sale_val = float(item[10]) if item[10] not in (None, "") else 0.0
                    sale = f"Rs. {sale_val:.2f}"
                except (ValueError, TypeError):
                    sale = "Rs. 0.00"
                    
                try:
                    stock_val = float(item[11]) if item[11] not in (None, "") else 0.0
                    stock = f"{stock_val:.2f}"
                except (ValueError, TypeError):
                    stock = "0.00"
                    
                location = item[12] if item[12] is not None else ""
                tax_method = "Applicable on Trade Price" if item[13] == "exclusive" else "Included in Retail Price" if item[13] == "inclusive" else "Applicable on Trade Price"
                self.tree.insert("", "end", iid=item[0], values=(
                    item[0], item[1], item[2], item[3], 
                    item[4] or "", item[5] or "", item[6] or "Piece",
                    item[7], item[8], cost, sale, stock, tax_method, location, "PropertyParams"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load items: {str(e)}")

    def add_item(self):
        try:
            new_id = execute_query("""
                INSERT INTO products (name, barcode, company, category_id, supplier_id, tax_id, base_uom_id, purchase_uom_id, cost_price, selling_price, stock)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("", "", "", None, None, 1, 1, 1, 0.0, 0.0, 0.0))
            
            self.tree.insert("", "end", iid=new_id, values=(
                new_id, "", "", "", "", "", "Piece", "", "", 
                "Rs. 0.00", "Rs. 0.00", "0.00", "Applicable on Trade Price", "", "PropertyParams"
            ))
            self.tree.selection_set(new_id)
            self.tree.focus(new_id)
            self.start_edit(column="#2")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {str(e)}")

    def bulk_add(self):
        from .bulk_add import BulkAddWindow
        BulkAddWindow(self.parent, self.user)

    def import_excel(self):
        from .excel_import import ExcelImportWindow
        ExcelImportWindow(self.parent, self.user)

    def on_double_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column not in ["#1", "#15"]:
                self.start_edit(column=column)

    def on_tree_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#15":
                item_id = self.tree.identify_row(event.y)
                if item_id:
                    from .item_properties import ItemPropertiesWindow
                    ItemPropertiesWindow(self.parent, int(item_id), self.user)

    def start_edit(self, column="#2"):
        selection = self.tree.selection()
        if not selection:
            return

        item_id = selection[0]
        self.editing_item = item_id
        self.editing_column = column

        # Special handling for Category column (#8)
        if column == "#8":
            self.start_category_edit(item_id)
            return
        # Special handling for Supplier column (#9)
        elif column == "#9":
            self.start_supplier_edit(item_id)
            return
        # Special handling for Tax Method column (#13)
        elif column == "#13":
            self.start_tax_method_edit(item_id)
            return

        # Get current value
        values = self.tree.item(item_id, "values")
        col_index = int(column[1:]) - 1
        current = values[col_index]

        # Special handling for price columns
        if col_index in (9, 10):  # Cost or Sale
            if current.startswith("Rs. "):
                current = current[4:]

        # Get cell bbox
        x, y, width, height = self.tree.bbox(item_id, column)
        if not x:
            self.tree.see(item_id)
            self.tree.update()
            x, y, width, height = self.tree.bbox(item_id, column)

        # Create entry
        self.entry = tk.Entry(self.tree, font=("Arial", 10), bg="#fff9c4", relief=tk.FLAT)
        self.entry.place(x=x, y=y, width=width, height=height)
        self.entry.insert(0, current)
        self.entry.select_range(0, tk.END)
        self.entry.focus()

        self.entry.bind("<Return>", self.handle_enter)
        self.entry.bind("<FocusOut>", self.cancel_edit)
        self.entry.bind("<Escape>", self.cancel_edit)

    def start_category_edit(self, item_id):
        """Show category dropdown for editing"""
        x, y, width, height = self.tree.bbox(item_id, "#8")
        if not x:
            self.tree.see(item_id)
            self.tree.update()
            x, y, width, height = self.tree.bbox(item_id, "#8")

        current_cat = self.tree.item(item_id, "values")[7]

        self.category_edit_combo = ttk.Combobox(self.tree, font=("Arial", 10), state="readonly")
        categories = [""] + [row[0] for row in fetch_all("SELECT name FROM categories ORDER BY name")]
        self.category_edit_combo['values'] = categories
        self.category_edit_combo.set(current_cat)
        self.category_edit_combo.place(x=x, y=y, width=width, height=height)
        self.category_edit_combo.focus()
        self.category_edit_combo.bind("<<ComboboxSelected>>", lambda e: self.save_category_edit(item_id))
        self.category_edit_combo.bind("<FocusOut>", lambda e: self.cancel_category_edit())
        self.category_edit_combo.bind("<Escape>", lambda e: self.cancel_category_edit())

    def save_category_edit(self, item_id):
        selected_cat = self.category_edit_combo.get()
        cat_id = None
        if selected_cat:
            cat = fetch_one("SELECT id FROM categories WHERE name = ?", (selected_cat,))
            if cat:
                cat_id = cat[0]
        try:
            execute_query("UPDATE products SET category_id = ? WHERE id = ?", (cat_id, int(item_id)))
            values = list(self.tree.item(item_id, "values"))
            values[7] = selected_cat
            self.tree.item(item_id, values=values)
            self.cancel_category_edit()
            messagebox.showinfo("Success", "Category updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update category: {str(e)}")

    def cancel_category_edit(self):
        if self.category_edit_combo:
            self.category_edit_combo.destroy()
            self.category_edit_combo = None

    def start_supplier_edit(self, item_id):
        """Show supplier dropdown for editing"""
        x, y, width, height = self.tree.bbox(item_id, "#9")
        if not x:
            self.tree.see(item_id)
            self.tree.update()
            x, y, width, height = self.tree.bbox(item_id, "#9")

        current_sup = self.tree.item(item_id, "values")[8]

        self.supplier_edit_combo = ttk.Combobox(self.tree, font=("Arial", 10), state="readonly")
        suppliers = [""] + [row[0] for row in fetch_all("SELECT name FROM suppliers ORDER BY name")]
        self.supplier_edit_combo['values'] = suppliers
        self.supplier_edit_combo.set(current_sup)
        self.supplier_edit_combo.place(x=x, y=y, width=width, height=height)
        self.supplier_edit_combo.focus()
        self.supplier_edit_combo.bind("<<ComboboxSelected>>", lambda e: self.save_supplier_edit(item_id))
        self.supplier_edit_combo.bind("<FocusOut>", lambda e: self.cancel_supplier_edit())
        self.supplier_edit_combo.bind("<Escape>", lambda e: self.cancel_supplier_edit())

    def save_supplier_edit(self, item_id):
        selected_sup = self.supplier_edit_combo.get()
        sup_id = None
        if selected_sup:
            sup = fetch_one("SELECT id FROM suppliers WHERE name = ?", (selected_sup,))
            if sup:
                sup_id = sup[0]
        try:
            execute_query("UPDATE products SET supplier_id = ? WHERE id = ?", (sup_id, int(item_id)))
            values = list(self.tree.item(item_id, "values"))
            values[8] = selected_sup
            self.tree.item(item_id, values=values)
            self.cancel_supplier_edit()
            messagebox.showinfo("Success", "Supplier updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update supplier: {str(e)}")

    def cancel_supplier_edit(self):
        if self.supplier_edit_combo:
            self.supplier_edit_combo.destroy()
            self.supplier_edit_combo = None

    def start_tax_method_edit(self, item_id):
        """Show tax method dropdown for editing"""
        x, y, width, height = self.tree.bbox(item_id, "#13")
        if not x:
            self.tree.see(item_id)
            self.tree.update()
            x, y, width, height = self.tree.bbox(item_id, "#13")

        current_tax_method = self.tree.item(item_id, "values")[12]

        self.tax_method_edit_combo = ttk.Combobox(self.tree, font=("Arial", 10), state="readonly")
        tax_methods = [
            "Applicable on Trade Price",
            "Included in Retail Price"
        ]
        self.tax_method_edit_combo['values'] = tax_methods
        self.tax_method_edit_combo.set(current_tax_method)
        self.tax_method_edit_combo.place(x=x, y=y, width=width, height=height)
        self.tax_method_edit_combo.focus()
        self.tax_method_edit_combo.bind("<<ComboboxSelected>>", lambda e: self.save_tax_method_edit(item_id))
        self.tax_method_edit_combo.bind("<FocusOut>", lambda e: self.cancel_tax_method_edit())
        self.tax_method_edit_combo.bind("<Escape>", lambda e: self.cancel_tax_method_edit())

    def save_tax_method_edit(self, item_id):
        selected_method = self.tax_method_edit_combo.get()
        tax_type = "exclusive" if selected_method == "Applicable on Trade Price" else "inclusive"
        
        try:
            execute_query("UPDATE products SET tax_type = ? WHERE id = ?", (tax_type, int(item_id)))
            values = list(self.tree.item(item_id, "values"))
            values[12] = selected_method
            self.tree.item(item_id, values=values)
            self.cancel_tax_method_edit()
            messagebox.showinfo("Success", "Tax method updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update tax method: {str(e)}")

    def cancel_tax_method_edit(self):
        if hasattr(self, 'tax_method_edit_combo') and self.tax_method_edit_combo:
            self.tax_method_edit_combo.destroy()
            self.tax_method_edit_combo = None

    def handle_enter(self, event=None):
        if not self.entry or not self.editing_item:
            return

        new_value = self.entry.get().strip()
        col_index = int(self.editing_column[1:]) - 1

        values = list(self.tree.item(self.editing_item, "values"))
        if col_index in (9, 10):
            try:
                num_val = float(new_value) if new_value else 0.0
                values[col_index] = f"Rs. {num_val:.2f}"
                db_value = num_val
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number.")
                return
        else:
            values[col_index] = new_value
            db_value = new_value

        self.tree.item(self.editing_item, values=values)

        col_to_field = {
            1: "barcode",
            2: "company",
            3: "name",
            8: "cost_price",
            9: "selling_price"
        }
        if col_index in col_to_field:
            try:
                execute_query(f"UPDATE products SET {col_to_field[col_index]} = ? WHERE id = ?", (db_value, int(self.editing_item)))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
                return

        current_item = self.editing_item
        
        try:
            current_pos = self.edit_columns_order.index(self.editing_column)
            if current_pos < len(self.edit_columns_order) - 1:
                next_column = self.edit_columns_order[current_pos + 1]
                self.cleanup_edit()
                self.tree.selection_set(current_item)
                self.tree.focus(current_item)
                self.start_edit(column=next_column)
            else:
                self.cleanup_edit()
                messagebox.showinfo("Success", "Item saved successfully!")
        except ValueError:
            self.cleanup_edit()

    def cancel_edit(self, event=None):
        self.cleanup_edit()

    def cleanup_edit(self):
        if self.entry:
            self.entry.destroy()
            self.entry = None
        self.editing_item = None
        self.editing_column = None

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def delete_item(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Select an item to delete.")
            return

        item_id = int(selection[0])
        if messagebox.askyesno("Confirm", "Delete this item?"):
            try:
                execute_query("DELETE FROM products WHERE id = ?", (item_id,))
                self.tree.delete(selection[0])
                messagebox.showinfo("Success", "Item deleted!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete item: {str(e)}")