# gui/ordering/receive_goods.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from utils import clear_window
from database import fetch_all, fetch_one, execute_query


class ReceiveGoodsWindow:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.is_frame = isinstance(parent, tk.Frame)
        self.direct_var = tk.BooleanVar(value=False)
        self.setup_ui()
        self.load_pos()

    def setup_ui(self):
        if self.is_frame:
            clear_window(self.parent)
            self.root = self.parent
            self.root.configure(bg="#0d1b2a")
        else:
            clear_window(self.parent)
            self.parent.title("📥 Advanced Goods Receipt - Crown Supermarket")
            self.parent.configure(bg="#0d1b2a")
            self.root = self.parent

        # Header
        header = tk.Frame(self.root, bg="#1b263b", height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="📥 ADVANCED GOODS RECEIPT", font=("Arial", 16, "bold"), fg="gold", bg="#1b263b").pack(pady=15)

        # Direct Receipt Toggle
        toggle_frame = tk.Frame(self.root, bg="white")
        toggle_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Checkbutton(
            toggle_frame,
            text="Receive goods without PO (Direct Receipt)",
            variable=self.direct_var,
            bg="white",
            command=self.toggle_direct_mode
        ).pack(side=tk.LEFT)

        # PO Selection
        po_frame = tk.Frame(self.root, bg="white")
        po_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(po_frame, text="Select Purchase Order:", font=("Arial", 12), bg="white").pack(side=tk.LEFT)
        self.po_var = tk.StringVar()
        self.po_combo = ttk.Combobox(po_frame, textvariable=self.po_var, state="readonly", width=30)
        self.po_combo.pack(side=tk.LEFT, padx=10)
        self.po_combo.bind("<<ComboboxSelected>>", self.load_po_items)

        # GST Calculation Method Selection
        gst_frame = tk.Frame(self.root, bg="#e8f4f8", relief=tk.RAISED, borderwidth=2)
        gst_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(gst_frame, text="📊 GST Calculation Method:", font=("Arial", 11, "bold"), bg="#e8f4f8", fg="#0d47a1").pack(side=tk.LEFT, padx=(10, 5))
        
        self.gst_method_var = tk.StringVar(value="trade_price")
        gst_methods = [
            ("Applicable on Trade Price (GST% × Trade Price)", "trade_price"),
            ("Included in Retail Price (Retail × GST% / (100 + GST%))", "retail_inclusive")
        ]
        
        for text, value in gst_methods:
            tk.Radiobutton(
                gst_frame,
                text=text,
                variable=self.gst_method_var,
                value=value,
                bg="#e8f4f8",
                font=("Arial", 10),
                command=self.recalculate_all_items
            ).pack(side=tk.LEFT, padx=10)

        # Items Table
        table_frame = tk.Frame(self.root, bg="white", relief=tk.RAISED, borderwidth=1)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("Product", "PO Qty", "Received", "FOC", "Trade Price", "Discount%", "GST%", "Retail Price", "UOM", "Cost Price")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        col_widths = {
            "Product": 170,
            "PO Qty": 65,
            "Received": 75,
            "FOC": 55,
            "Trade Price": 85,
            "Discount%": 75,
            "GST%": 60,
            "Retail Price": 85,
            "UOM": 65,
            "Cost Price": 85
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 100))
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Button-3>", self.show_edit_menu)

        # Action Buttons
        btn_frame = tk.Frame(self.root, bg="white")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(btn_frame, text="💾 Save Receipt", font=("Arial", 12, "bold"), bg="#2E8B57", fg="white",
                  command=self.save_receipt).pack(side=tk.RIGHT, padx=5)
        
        if not self.is_frame:
            tk.Button(btn_frame, text="❌ Cancel", font=("Arial", 12, "bold"), bg="#A9A9A9", fg="white",
                      command=self.parent.destroy).pack(side=tk.RIGHT, padx=5)
        else:
            tk.Button(btn_frame, text="⬅️ Back to Dashboard", font=("Arial", 12, "bold"), bg="#A9A9A9", fg="white",
                      command=self.go_back).pack(side=tk.RIGHT, padx=5)

        self.receipt_items = []
        self.po_items = []

    def toggle_direct_mode(self):
        if self.direct_var.get():
            self.po_combo.set('')
            self.po_combo.configure(state="disabled")
            if not hasattr(self, 'add_item_btn'):
                self.add_item_btn = tk.Button(
                    self.root, 
                    text="➕ Add Product", 
                    command=self.add_manual_item,
                    bg="#1b263b", fg="white"
                )
                self.add_item_btn.pack(pady=5)
            self.load_empty_table()
        else:
            self.po_combo.configure(state="readonly")
            if hasattr(self, 'add_item_btn'):
                self.add_item_btn.pack_forget()
            self.load_pos()

    def recalculate_all_items(self):
        """Recalculate all items when GST method changes"""
        for row_id in self.tree.get_children():
            item_idx = self.tree.index(row_id)
            if item_idx < len(self.po_items):
                item_data = self.po_items[item_idx]
                self.recalculate_item(row_id, item_data)

    def load_empty_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.po_items = []

    def load_pos(self):
        try:
            pos = fetch_all("""
                SELECT po.id, po.po_number, s.name as supplier_name
                FROM purchase_orders po
                JOIN suppliers s ON po.supplier_id = s.id
                WHERE po.status = 'sent'
                ORDER BY po.created_at DESC
            """)
            po_options = [f"{po[1]} - {po[2]}" for po in pos]
            self.po_combo['values'] = po_options
            self.po_data = {f"{po[1]} - {po[2]}": po[0] for po in pos}
        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to load POs: {e}")
            self.po_combo['values'] = []
            self.po_data = {}

    def load_po_items(self, event=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        selected_po = self.po_var.get()
        if not selected_po:
            return

        po_id = self.po_data[selected_po]
        items_list = fetch_all("""
            SELECT 
                pi.id, p.name, pi.quantity_ordered, pi.cost_price,
                pu.symbol as purchase_uom, p.id as product_id,
                p.gst_rate, p.tax_type
            FROM po_items pi
            JOIN products p ON pi.product_id = p.id
            JOIN uoms pu ON p.purchase_uom_id = pu.id
            WHERE pi.po_id = ?
        """, (po_id,))
        
        self.po_items = []
        for item in items_list:
            item_data = {
                'po_item_id': item[0],
                'product_name': item[1],
                'po_qty': item[2],
                'trade_price': item[3],
                'purchase_uom': item[4],
                'product_id': item[5],
                'gst_rate': item[6] or 17.0,
                'tax_type': item[7] or 'exclusive',
                'discount_percent': 0.0,
                'received_qty': 0.0,
                'foc_qty': 0.0
            }
            self.po_items.append(item_data)
            self.add_item_to_tree(item_data)

    def add_item_to_tree(self, item_data):
        # Calculate initial retail price
        trade_price = item_data['trade_price']
        discount_percent = item_data.get('discount_percent', 0.0)
        gst_rate = item_data.get('gst_rate', 17.0)
        
        # Apply discount to trade price
        discounted_trade = trade_price * (1 - discount_percent / 100)
        
        # Calculate retail price based on selected GST method
        gst_method = self.gst_method_var.get()
        
        if gst_method == "trade_price":
            # Method 1: GST applicable on trade price
            retail_price = discounted_trade * (1 + gst_rate / 100)
        else:  # retail_inclusive
            # Method 2: GST included in retail
            retail_price = discounted_trade
        
        row_id = self.tree.insert("", "end", values=(
            item_data['product_name'],
            f"{item_data['po_qty']:.2f}",
            f"{item_data.get('received_qty', 0.0):.2f}",
            f"{item_data.get('foc_qty', 0.0):.2f}",
            f"Rs. {trade_price:.2f}",
            f"{discount_percent:.1f}%",
            f"{gst_rate:.1f}%",
            f"Rs. {retail_price:.2f}",
            item_data['purchase_uom'],
            f"Rs. {discounted_trade:.2f}"
        ))





    def recalculate_item(self, row_id, item_data):
        received_qty = item_data.get('received_qty', 0.0)
        foc_qty = item_data.get('foc_qty', 0.0)
        trade_price = item_data['trade_price']
        discount_percent = item_data.get('discount_percent', 0.0)
        gst_rate = item_data.get('gst_rate', 17.0)
        
        # Apply discount to trade price
        discounted_trade = trade_price * (1 - discount_percent / 100)
        
        # Calculate total value (only paid quantity, not FOC)
        total_paid_qty = received_qty
        total_value = total_paid_qty * discounted_trade
        total_qty = received_qty + foc_qty
        
        # Cost price = total value / total quantity (including FOC)
        cost_price = total_value / total_qty if total_qty > 0 else 0.0

        # Calculate retail price based on selected GST method
        gst_method = self.gst_method_var.get()
        
        if gst_method == "trade_price":
            # Method 1: Applicable on Trade Price (GST% × Trade Price)
            # Retail = Discounted Trade + (GST% × Discounted Trade)
            retail_price = discounted_trade * (1 + gst_rate / 100)
        else:  # retail_inclusive
            # Method 2: Included in Retail Price
            # This means: retail_price already contains GST
            # GST Amount = Retail × GST% / (100 + GST%)
            # For calculation purposes, we keep retail = discounted trade
            # But store that GST is included
            retail_price = discounted_trade
            item_data['tax_type'] = 'inclusive'


        self.tree.item(row_id, values=(
            item_data['product_name'],
            f"{item_data['po_qty']:.2f}",
            f"{received_qty:.2f}",
            f"{foc_qty:.2f}",
            f"Rs. {trade_price:.2f}",
            f"{discount_percent:.1f}%",
            f"{gst_rate:.1f}%",
            f"Rs. {retail_price:.2f}",
            item_data['purchase_uom'],
            f"Rs. {cost_price:.2f}"
        ))
        item_data['cost_price'] = cost_price
        item_data['retail_price'] = retail_price
        item_data['discounted_trade'] = discounted_trade



    def show_edit_menu(self, event):
        row_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not row_id or col not in ("#2", "#3", "#4", "#5", "#6", "#7", "#8"):
            return
        item_idx = self.tree.index(row_id)
        if item_idx >= len(self.po_items):
            return
        item_data = self.po_items[item_idx]

        if col == "#2":  # PO Qty
            new_po_qty = simpledialog.askfloat("Edit PO Qty", "Purchase Order Quantity:", initialvalue=item_data.get('po_qty', 0.0))
            if new_po_qty is not None:
                if new_po_qty < 0:
                    new_po_qty = 0.0
                item_data['po_qty'] = float(new_po_qty)
                self.recalculate_item(row_id, item_data)
        elif col == "#3":  # Received Qty
            new_qty = simpledialog.askfloat("Edit Received Qty", "Received Quantity:", initialvalue=item_data.get('received_qty', 0.0))
            if new_qty is not None:
                if new_qty < 0:
                    new_qty = 0.0
                item_data['received_qty'] = float(new_qty)
                self.recalculate_item(row_id, item_data)
        elif col == "#4":  # FOC Qty
            new_foc = simpledialog.askfloat("Edit FOC Qty", "FOC Quantity:", initialvalue=item_data.get('foc_qty', 0.0))
            if new_foc is not None:
                if new_foc < 0:
                    new_foc = 0.0
                item_data['foc_qty'] = float(new_foc)
                self.recalculate_item(row_id, item_data)
        elif col == "#5":  # Trade Price
            new_val = simpledialog.askfloat("Edit Trade Price", "Trade Price (Rs):", initialvalue=item_data['trade_price'])
            if new_val is not None and new_val >= 0:
                item_data['trade_price'] = new_val
                self.recalculate_item(row_id, item_data)
        elif col == "#6":  # Discount%
            new_discount = simpledialog.askfloat("Edit Discount", "Discount (%):", initialvalue=item_data.get('discount_percent', 0.0))
            if new_discount is not None and 0 <= new_discount <= 100:
                item_data['discount_percent'] = new_discount
                self.recalculate_item(row_id, item_data)
        elif col == "#7":  # GST%
            new_gst = simpledialog.askfloat("Edit GST%", "GST Rate (%):", initialvalue=item_data['gst_rate'])
            if new_gst is not None and new_gst >= 0:
                item_data['gst_rate'] = new_gst
                self.recalculate_item(row_id, item_data)
        elif col == "#8":  # Retail Price
            new_val = simpledialog.askfloat("Edit Retail Price", "Retail Price (Rs):", initialvalue=item_data.get('retail_price', 0))
            if new_val is not None and new_val >= 0:
                trade = item_data['trade_price']
                discount = item_data.get('discount_percent', 0.0)
                discounted_trade = trade * (1 - discount / 100)
                
                if discounted_trade == 0:
                    messagebox.showwarning("Warning", "Set trade price first.")
                    return
                
                # Calculate GST based on retail vs discounted trade
                if new_val >= discounted_trade:
                    item_data['tax_type'] = 'exclusive'
                    item_data['gst_rate'] = ((new_val / discounted_trade) - 1) * 100
                else:
                    item_data['tax_type'] = 'inclusive'
                    item_data['gst_rate'] = 17.0
                item_data['retail_price'] = new_val
                self.recalculate_item(row_id, item_data)

    def select_product(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Product")
        dialog.geometry("600x400")
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Search Product:", bg="white").pack(pady=5)
        search_var = tk.StringVar()
        search_entry = tk.Entry(dialog, textvariable=search_var, width=50)
        search_entry.pack(pady=5)

        tree = ttk.Treeview(dialog, columns=("ID", "Name", "Trade Price", "GST%", "Tax Type", "UOM"), show="headings", height=10)
        for col in ("ID", "Name", "Trade Price", "GST%", "Tax Type", "UOM"):
            tree.heading(col, text=col)
            tree.column(col, width=80 if col == "Name" else 60)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        products = fetch_all("""
            SELECT p.id, p.name, p.cost_price, p.gst_rate, p.tax_type, u.symbol
            FROM products p
            JOIN uoms u ON p.purchase_uom_id = u.id
        """)
        for p in products:
            tree.insert("", "end", values=p)

        def on_search(*_):
            term = search_var.get().lower()
            for item in tree.get_children():
                tree.delete(item)
            for p in products:
                if term in p[1].lower():
                    tree.insert("", "end", values=p)
        search_var.trace("w", on_search)

        selected = [None]
        def on_select():
            sel = tree.selection()
            if sel:
                selected[0] = tree.item(sel[0], "values")
                dialog.destroy()
            else:
                messagebox.showwarning("No Selection", "Please select a product.")
        btn_frame = tk.Frame(dialog, bg="white")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Select", command=on_select, bg="#2E8B57", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy, bg="#A9A9A9", fg="white").pack(side=tk.LEFT, padx=5)
        dialog.wait_window()
        return selected[0]

    def add_manual_item(self):
        selected = self.select_product()
        if not selected:
            return
        product_id = int(selected[0])
        product_name = selected[1]
        trade_price = float(selected[2]) if selected[2] else 0.0
        gst_rate = float(selected[3]) if selected[3] else 17.0
        tax_type = selected[4] or 'exclusive'
        purchase_uom = selected[5] or 'pcs'

        item_data = {
            'po_item_id': None,
            'product_name': product_name,
            'po_qty': 0,
            'trade_price': trade_price,
            'purchase_uom': purchase_uom,
            'product_id': product_id,
            'gst_rate': gst_rate,
            'tax_type': tax_type,
            'discount_percent': 0.0,
            'received_qty': 0.0,
            'foc_qty': 0.0
        }
        self.po_items.append(item_data)
        self.add_item_to_tree(item_data)



    def save_receipt(self):
        if not self.po_items:
            messagebox.showwarning("No Items", "Add at least one item.")
            return

        has_received = any(
            (item.get('received_qty', 0) > 0) or (item.get('foc_qty', 0) > 0)
            for item in self.po_items
        )
        if not has_received:
            messagebox.showwarning("No Quantity", "Enter received or FOC quantities.")
            return

        is_direct = self.direct_var.get()
        receipt_number = f"GR{datetime.now().strftime('%Y%m%d%H%M%S')}"

        try:
            if is_direct:
                total_amount = sum(item.get('received_qty', 0) * item['trade_price'] for item in self.po_items)
                receipt_id = execute_query("""
                    INSERT INTO goods_receipts 
                    (receipt_number, po_id, supplier_id, total_amount, net_payable, received_by, is_direct_receipt)
                    VALUES (?, NULL, NULL, ?, ?, ?, 1)
                """, (receipt_number, total_amount, total_amount, self.user['id']))
            else:
                selected_po = self.po_var.get()
                if not selected_po:
                    messagebox.showwarning("No PO", "Select a purchase order.")
                    return
                po_id = self.po_data[selected_po]
                supplier_id = fetch_one("SELECT supplier_id FROM purchase_orders WHERE id = ?", (po_id,))[0]
                total_amount = sum(item.get('received_qty', 0) * item['trade_price'] for item in self.po_items)
                receipt_id = execute_query("""
                    INSERT INTO goods_receipts 
                    (receipt_number, po_id, supplier_id, total_amount, net_payable, received_by, is_direct_receipt)
                    VALUES (?, ?, ?, ?, ?, ?, 0)
                """, (receipt_number, po_id, supplier_id, total_amount, total_amount, self.user['id']))
                execute_query("""
                    UPDATE purchase_orders 
                    SET status = 'received', received_at = ?
                    WHERE id = ?
                """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), po_id))

            for item_data in self.po_items:
                received_qty = item_data.get('received_qty', 0.0)
                foc_qty = item_data.get('foc_qty', 0.0)
                if received_qty > 0 or foc_qty > 0:
                    base_uom_qty = received_qty + foc_qty
                    discount_percent = item_data.get('discount_percent', 0.0)
                    discounted_trade = item_data['trade_price'] * (1 - discount_percent / 100)
                    
                    execute_query("""
                        INSERT INTO goods_receipt_items 
                        (receipt_id, product_id, quantity_received, foc_quantity, 
                         quantity_in_base_uom, trade_price, retail_price, cost_price)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        receipt_id,
                        item_data['product_id'],
                        received_qty,
                        foc_qty,
                        base_uom_qty,
                        discounted_trade,  # Save discounted trade price
                        item_data['retail_price'],
                        item_data['cost_price']
                    ))
                    
                    # Update product with new cost and selling prices
                    execute_query("""
                        UPDATE products 
                        SET stock = stock + ?,
                            cost_price = ?,
                            selling_price = ?
                        WHERE id = ?
                    """, (base_uom_qty, item_data['cost_price'], item_data['retail_price'], item_data['product_id']))

            messagebox.showinfo("Success", f"✅ Goods receipt {receipt_number} saved!")
            if self.is_frame:
                self.go_back()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save receipt: {str(e)}")

    def go_back(self):
        from .ordering_main import OrderingDashboard
        OrderingDashboard(self.root, self.user)