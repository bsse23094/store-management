# gui/ordering/smart_order.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import calendar
from utils import clear_window
from database import fetch_all, fetch_one, execute_query

class SmartOrderTab:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.setup_ui()
        self.load_suppliers()
        self.items_to_order = []

    def setup_ui(self):
        # Header
        header = tk.Frame(self.parent, bg="#1b263b", height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="🧠 Smart Order Suggestion", font=("Arial", 16, "bold"), fg="gold", bg="#1b263b").pack(pady=15)

        # Analysis Controls
        control_frame = tk.Frame(self.parent, bg="white")
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        # Days of Stock Needed
        tk.Label(control_frame, text="Days of Stock Needed:", font=("Arial", 10), bg="white").pack(side=tk.LEFT)
        self.days_var = tk.IntVar(value=7)
        tk.Spinbox(control_frame, from_=1, to=90, textvariable=self.days_var, width=5).pack(side=tk.LEFT, padx=5)

        # Analysis Period
        tk.Label(control_frame, text="Analysis Period:", font=("Arial", 10), bg="white").pack(side=tk.LEFT, padx=(15,5))
        self.period_var = tk.StringVar(value="Last 30 Days")
        period_options = ["Last 15 Days", "Last 30 Days", "Same Period Last Month", "Same Period Last Year"]
        self.period_combo = ttk.Combobox(control_frame, textvariable=self.period_var, values=period_options, state="readonly", width=20)
        self.period_combo.pack(side=tk.LEFT, padx=5)

        # Supplier Filter
        tk.Label(control_frame, text="Supplier:", font=("Arial", 10), bg="white").pack(side=tk.LEFT, padx=(15,5))
        self.supplier_var = tk.StringVar(value="All Suppliers")
        self.supplier_combo = ttk.Combobox(control_frame, textvariable=self.supplier_var, state="readonly", width=18)
        self.supplier_combo.pack(side=tk.LEFT, padx=5)

        # Analyze Button
        tk.Button(control_frame, text="🔍 Analyze & Suggest", font=("Arial", 10, "bold"), bg="#1E90FF", fg="white", command=self.analyze_orders).pack(side=tk.LEFT, padx=10)

        # Items Table
        tree_frame = tk.Frame(self.parent, bg="white", relief=tk.RAISED, borderwidth=1)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("Product", "Current Stock", "Daily Consumption", "Days Needed", "Suggested Qty", "Supplier", "Cost", "Actions")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        col_widths = {
            "Product": 180,
            "Current Stock": 90,
            "Daily Consumption": 110,
            "Days Needed": 70,
            "Suggested Qty": 90,
            "Supplier": 140,
            "Cost": 70,
            "Actions": 100
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 100))
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="#0d1b2a", fieldbackground="white", font=("Arial", 9))
        style.configure("Treeview.Heading", background="#1b263b", foreground="gold", font=("Arial", 9, "bold"))
        style.map("Treeview", background=[('selected', '#0d1b2a')], foreground=[('selected', 'gold')])

        # Action Buttons
        btn_frame = tk.Frame(self.parent, bg="white")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(btn_frame, text="🖨️ Generate POs", font=("Arial", 11, "bold"), bg="#2E8B57", fg="white", command=self.generate_pos).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="🔄 Refresh", font=("Arial", 11, "bold"), bg="#1E90FF", fg="white", command=self.analyze_orders).pack(side=tk.RIGHT, padx=5)

    def load_suppliers(self):
        suppliers = ["All Suppliers"] + [row[0] for row in fetch_all("SELECT name FROM suppliers ORDER BY name")]
        self.supplier_combo['values'] = suppliers

    def get_analysis_dates(self):
        """Get start/end dates based on selected period"""
        period_label = self.period_var.get()
        today = datetime.now().date()
        
        if period_label == "Last 15 Days":
            start_date = today - timedelta(days=15)
            end_date = today
        elif period_label == "Last 30 Days":
            start_date = today - timedelta(days=30)
            end_date = today
        elif period_label == "Same Period Last Month":
            if today.day == 1:
                last_month = today.replace(day=1) - timedelta(days=1)
                start_date = last_month.replace(day=1)
                end_date = last_month
            else:
                days_in_last_month = calendar.monthrange(today.year, today.month-1 if today.month > 1 else 12)[1]
                end_day = min(today.day, days_in_last_month)
                start_date = today.replace(month=today.month-1 if today.month > 1 else 12, 
                                         year=today.year if today.month > 1 else today.year-1, 
                                         day=1)
                end_date = start_date.replace(day=end_day)
        elif period_label == "Same Period Last Year":
            try:
                start_date = today.replace(year=today.year-1)
                end_date = today.replace(year=today.year-1)
            except ValueError:
                start_date = today.replace(year=today.year-1, day=28)
                end_date = today.replace(year=today.year-1, day=28)
        else:
            return None, None

        return start_date, end_date

    def analyze_orders(self):
        """Analyze sales and suggest items to order"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        start_date, end_date = self.get_analysis_dates()
        if start_date is None:
            return

        supplier_filter = self.supplier_var.get()
        supplier_id = None
        if supplier_filter != "All Suppliers":
            sup = fetch_one("SELECT id FROM suppliers WHERE name = ?", (supplier_filter,))
            if sup:
                supplier_id = sup[0]

        products_query = """
            SELECT p.id, p.name, p.stock, p.category_id,
                   sp.supplier_id, s.name as supplier_name, sp.cost_price,
                   s.lead_time_days
            FROM products p
            JOIN supplier_prices sp ON p.id = sp.product_id
            JOIN suppliers s ON sp.supplier_id = s.id
            WHERE sp.is_active = 1
        """
        params = []
        if supplier_id:
            products_query += " AND s.id = ?"
            params.append(supplier_id)
        
        products = fetch_all(products_query, params)
        self.items_to_order = []
        days_needed = self.days_var.get()
        
        for prod in products:
            product_id, name, current_stock, category_id, sup_id, sup_name, cost_price, lead_time = prod
            
            sales_query = """
                SELECT SUM(si.quantity) as total_qty, COUNT(DISTINCT DATE(s.created_at)) as sale_days
                FROM sales s
                JOIN sale_items si ON s.id = si.sale_id
                WHERE si.product_id = ?
                AND DATE(s.created_at) BETWEEN ? AND ?
                AND s.is_return = 0
            """
            sales_data = fetch_one(sales_query, (product_id, start_date, end_date))
            
            total_sales = sales_data[0] if sales_data and sales_data[0] else 0
            sale_days = sales_data[1] if sales_data and sales_data[1] else 1
            daily_consumption = total_sales / sale_days if sale_days > 0 else 0
            
            suggested_qty = (daily_consumption * days_needed) - current_stock
            suggested_qty = max(0, round(suggested_qty, 2))
            
            if suggested_qty > 0:
                item_data = {
                    'product_id': product_id,
                    'name': name,
                    'current_stock': current_stock,
                    'daily_consumption': daily_consumption,
                    'days_needed': days_needed,
                    'suggested_qty': suggested_qty,
                    'supplier_id': sup_id,
                    'supplier_name': sup_name,
                    'cost_price': cost_price or 0.0
                }
                self.items_to_order.append(item_data)
                
                self.tree.insert("", "end", values=(
                    item_data['name'],
                    f"{item_data['current_stock']:.2f}",
                    f"{item_data['daily_consumption']:.2f}",
                    item_data['days_needed'],
                    f"{item_data['suggested_qty']:.2f}",
                    item_data['supplier_name'],
                    f"Rs. {item_data['cost_price']:.2f}",
                    "✏️ Edit"
                ))

    def generate_pos(self):
        """Generate POs grouped by supplier"""
        if not self.items_to_order:
            messagebox.showwarning("No Items", "No items to order.")
            return

        po_groups = {}
        for item in self.items_to_order:
            sup_id = item['supplier_id']
            if sup_id not in po_groups:
                po_groups[sup_id] = []
            po_groups[sup_id].append(item)

        created_pos = []
        for sup_id, items in po_groups.items():
            try:
                po_number = f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}"
                total_amount = sum(item['suggested_qty'] * item['cost_price'] for item in items)
                
                po_id = execute_query("""
                    INSERT INTO purchase_orders (po_number, supplier_id, total_amount, created_by, status)
                    VALUES (?, ?, ?, ?, 'draft')
                """, (po_number, sup_id, total_amount, self.user['id']))

                for item in items:
                    execute_query("""
                        INSERT INTO po_items (po_id, product_id, quantity_ordered, cost_price)
                        VALUES (?, ?, ?, ?)
                    """, (po_id, item['product_id'], item['suggested_qty'], item['cost_price']))

                created_pos.append((po_number, sup_id))
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create PO: {str(e)}")
                return

        messagebox.showinfo("Success", f"✅ {len(created_pos)} POs created successfully!")

    def go_back(self):
        from .ordering_main import OrderingDashboard
        OrderingDashboard(self.root, self.user)