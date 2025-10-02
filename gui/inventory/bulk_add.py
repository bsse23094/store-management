# gui/inventory/bulk_add.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import fetch_all, execute_query, fetch_one

class BulkAddWindow:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Bulk Add Items - Crown Supermarket")
        self.window.geometry("1200x700")
        self.window.configure(bg="#0d1b2a")
        self.setup_ui()
        self.load_dropdown_data()
        self.add_empty_row()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg="#1b263b", height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="📊 Bulk Add Items", font=("Arial", 16, "bold"), fg="gold", bg="#1b263b").pack(pady=15)
        tk.Label(header, text="Press Enter in any cell to move to next row. Save all when done.", 
                 font=("Arial", 10), fg="#90e0ef", bg="#1b263b").pack()

        # Action Buttons
        btn_frame = tk.Frame(self.window, bg="#0d1b2a")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(btn_frame, text="💾 Save All Items", font=("Arial", 12, "bold"), bg="#2E8B57", fg="white",
                  command=self.save_all).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="➕ Add Row", font=("Arial", 12, "bold"), bg="#1E90FF", fg="white",
                  command=self.add_empty_row).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="❌ Cancel", font=("Arial", 12, "bold"), bg="#A9A9A9", fg="white",
                  command=self.window.destroy).pack(side=tk.LEFT, padx=5)

        # Main container with scrollbars
        main_frame = tk.Frame(self.window, bg="white", relief=tk.RAISED, borderwidth=1)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Canvas and scrollbars
        self.canvas = tk.Canvas(main_frame, bg="white")
        self.v_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(main_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Scrollable frame inside canvas
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Pack everything
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Configure the scrollable frame
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # Column configuration
        self.headers = ["Barcode", "Company", "Name", "Variant", "Size", "Unit", "Category", "Supplier", "Cost", "Sale", "Stock"]
        self.column_widths = [120, 150, 200, 100, 80, 80, 120, 120, 80, 80, 80]  # Widths in pixels
        
        # Create the header row (fixed at top)
        self.create_header_row()
        
        # Bind mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)

    def on_frame_configure(self, event):
        """Update scroll region when frame size changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Keep header row at top when scrolling"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def create_header_row(self):
        """Create fixed header row"""
        self.header_frame = tk.Frame(self.scrollable_frame, bg="#1b263b")
        self.header_frame.grid(row=0, column=0, sticky="ew")
        
        # Configure header columns
        total_width = 0
        for col, (header, width) in enumerate(zip(self.headers, self.column_widths)):
            self.header_frame.grid_columnconfigure(col, minsize=width)
            total_width += width
            
            label = tk.Label(
                self.header_frame, 
                text=header, 
                font=("Arial", 10, "bold"), 
                bg="#1b263b", 
                fg="gold",
                padx=8,
                pady=6,
                width=0  # Let minsize control width
            )
            label.grid(row=0, column=col, sticky="ew", padx=1, pady=1)
        
        # Set minimum width for scrollable frame
        self.scrollable_frame.grid_columnconfigure(0, minsize=total_width)

    def _on_mousewheel(self, event):
        """Vertical scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_shift_mousewheel(self, event):
        """Horizontal scrolling with Shift + Mousewheel"""
        self.canvas.xview_scroll(int(-1*(event.delta/120)), "units")

    def load_dropdown_data(self):
        """Load dropdown options for auto-suggest"""
        try:
            self.categories = [row[0] for row in fetch_all("SELECT name FROM categories ORDER BY name")]
            self.suppliers = [row[0] for row in fetch_all("SELECT name FROM suppliers ORDER BY name")]
            self.companies = [row[0] for row in fetch_all("SELECT DISTINCT company FROM products WHERE company IS NOT NULL AND company != '' ORDER BY company")]
            self.units = [row[0] for row in fetch_all("SELECT name FROM uoms ORDER BY name")]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dropdown: {str(e)}")
            self.categories = []
            self.suppliers = []
            self.companies = []
            self.units = ["Piece", "Box", "Carton", "Kilogram", "Liter"]

    def add_empty_row(self, prev_row_data=None):
        """Add a new row with proper column widths"""
        # Get current row count (skip header row)
        current_row = len(self.scrollable_frame.grid_slaves()) - 1  # -1 for header
        
        row_frame = tk.Frame(self.scrollable_frame, bg="white")
        row_frame.grid(row=current_row + 1, column=0, sticky="ew")  # +1 to skip header
        
        # Configure row columns with exact widths
        total_width = 0
        for col, width in enumerate(self.column_widths):
            row_frame.grid_columnconfigure(col, minsize=width)
            total_width += width

        row_entries = []
        
        # Get previous row data for auto-suggest
        if prev_row_data is None and hasattr(self, 'entries') and self.entries:
            prev_row_data = self.entries[-1]

        for col, (header, width) in enumerate(zip(self.headers, self.column_widths)):
            if header == "Company" and self.companies:
                widget = ttk.Combobox(row_frame, values=self.companies, state="normal", width=0)
                if prev_row_data and col < len(prev_row_data):
                    widget.set(prev_row_data[col].get() if hasattr(prev_row_data[col], 'get') else prev_row_data[col])
            elif header == "Category" and self.categories:
                widget = ttk.Combobox(row_frame, values=self.categories, state="normal", width=0)
                if prev_row_data and col < len(prev_row_data):
                    widget.set(prev_row_data[col].get() if hasattr(prev_row_data[col], 'get') else prev_row_data[col])
            elif header == "Supplier" and self.suppliers:
                widget = ttk.Combobox(row_frame, values=self.suppliers, state="normal", width=0)
                if prev_row_data and col < len(prev_row_data):
                    widget.set(prev_row_data[col].get() if hasattr(prev_row_data[col], 'get') else prev_row_data[col])
            elif header == "Unit" and self.units:
                widget = ttk.Combobox(row_frame, values=self.units, state="normal", width=0)
                widget.set("Piece")
            else:
                widget = tk.Entry(row_frame, font=("Arial", 10), width=0)
                if prev_row_data and col < len(prev_row_data):
                    val = prev_row_data[col].get() if hasattr(prev_row_data[col], 'get') else prev_row_data[col]
                    widget.insert(0, val)
                widget.bind("<Return>", lambda e, r=row_entries: self.handle_enter_in_row(r))
            
            widget.grid(row=0, column=col, sticky="ew", padx=1, pady=1)
            row_entries.append(widget)

        if not hasattr(self, 'entries'):
            self.entries = []
        self.entries.append(row_entries)
        
        # Focus first cell
        if row_entries:
            row_entries[0].focus()

        # Update scroll region
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def handle_enter_in_row(self, row_entries):
        """When Enter is pressed in a row, add a new row below"""
        row_data = []
        for entry in row_entries:
            if hasattr(entry, 'get'):
                row_data.append(entry.get())
            else:
                row_data.append("")
        
        self.add_empty_row(row_data)

    def save_all(self):
        """Save all items to database"""
        if not hasattr(self, 'entries') or not self.entries:
            messagebox.showwarning("No Data", "No items to save.")
            return

        saved_count = 0
        for row_entries in self.entries:
            try:
                values = []
                for entry in row_entries:
                    if hasattr(entry, 'get'):
                        values.append(entry.get().strip())
                    else:
                        values.append("")
                
                if not any(values):
                    continue

                barcode, company, name, variant, size, unit, category, supplier, cost, sale, stock = values + [""] * (11 - len(values))

                if not name:
                    messagebox.showwarning("Missing Data", "Product name is required.")
                    return

                try:
                    cost_val = float(cost) if cost else 0.0
                    sale_val = float(sale) if sale else 0.0
                    stock_val = float(stock) if stock else 0.0
                except ValueError:
                    messagebox.showerror("Invalid Input", "Cost, Sale, and Stock must be numbers.")
                    return

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

                product_id = execute_query("""
                    INSERT INTO products (name, barcode, company, category_id, supplier_id, tax_id, base_uom_id, purchase_uom_id, cost_price, selling_price, stock)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, barcode or None, company or None, category_id, supplier_id, 1, unit_id, unit_id, cost_val, sale_val, stock_val))

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

                saved_count += 1

            except Exception as e:
                messagebox.showerror("Error", f"Failed to save item '{name}': {str(e)}")
                return

        messagebox.showinfo("Success", f"✅ {saved_count} items saved successfully!")
        self.window.destroy()