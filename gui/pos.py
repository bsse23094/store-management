# gui/pos.py
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from datetime import datetime
from database import get_db_connection
from utils import clear_window, show_error, show_info, show_warning

class POSWindow:
    def __init__(self, root, user, return_mode=False, invoice_no=None):
        self.root = root
        self.user = user
        self.return_mode = return_mode
        self.original_invoice_no = invoice_no
        self.cart = []
        self.invoice_no = invoice_no or f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.setup_ui()
        if return_mode and invoice_no:
            self.load_return_invoice(invoice_no)

    def setup_ui(self):
        clear_window(self.root)
        title = "↩️ SALE RETURN" if self.return_mode else "💵 NEW SALE"
        self.root.title(f"{title} - Crown Supermarket POS")
        self.root.configure(bg="#0d1b2a")  # Dark blue background

        # === TOP BAR ===
        top_frame = tk.Frame(self.root, bg="#1b263b", height=80)
        top_frame.pack(fill=tk.X)

        # Left: Crown Logo + Date/Time
        left_top = tk.Frame(top_frame, bg="#1b263b")
        left_top.pack(side=tk.LEFT, padx=20)

        tk.Label(left_top, text="👑 CROWN SUPERMARKET", font=("Arial", 16, "bold"), fg="gold", bg="#1b263b").pack(anchor="w")
        self.datetime_label = tk.Label(left_top, text="", font=("Arial", 10), fg="#90e0ef", bg="#1b263b")
        self.datetime_label.pack(anchor="w")
        self.update_datetime()

        # Center: Operator + Customer Info
        center_top = tk.Frame(top_frame, bg="#1b263b")
        center_top.pack(side=tk.LEFT, padx=40)

        tk.Label(center_top, text=f"👤 Operator: {self.user['full_name']}", font=("Arial", 11), fg="white", bg="#1b263b").pack(anchor="w", pady=(5,0))

        # Customer Info
        cust_frame = tk.Frame(center_top, bg="#1b263b")
        cust_frame.pack(anchor="w", pady=(10,0))

        tk.Label(cust_frame, text="Customer:", font=("Arial", 10), fg="white", bg="#1b263b").pack(side=tk.LEFT)
        self.customer_var = tk.StringVar(value="Walk-in Customer")
        tk.Entry(cust_frame, textvariable=self.customer_var, font=("Arial", 11), width=25, bg="#0d1b2a", fg="white", insertbackground="white").pack(side=tk.LEFT, padx=5)

        tk.Label(cust_frame, text=" | Phone:", font=("Arial", 10), fg="white", bg="#1b263b").pack(side=tk.LEFT, padx=(10,5))
        self.phone_var = tk.StringVar()
        tk.Entry(cust_frame, textvariable=self.phone_var, font=("Arial", 11), width=15, bg="#0d1b2a", fg="white", insertbackground="white").pack(side=tk.LEFT)

        tk.Label(cust_frame, text=" | Loyalty Card:", font=("Arial", 10), fg="white", bg="#1b263b").pack(side=tk.LEFT, padx=(10,5))
        self.loyalty_var = tk.StringVar()
        loyalty_entry = tk.Entry(cust_frame, textvariable=self.loyalty_var, font=("Arial", 11), width=15, bg="#0d1b2a", fg="white", insertbackground="white")
        loyalty_entry.pack(side=tk.LEFT)
        loyalty_entry.bind("<Return>", self.on_loyalty_scan)

        # Right: Invoice No
        right_top = tk.Frame(top_frame, bg="#1b263b")
        right_top.pack(side=tk.RIGHT, padx=20)
        tk.Label(right_top, text=f"📄 Invoice: {self.invoice_no}", font=("Arial", 12, "bold"), fg="gold", bg="#1b263b").pack(pady=10)
        if self.return_mode:
            tk.Label(right_top, text="MODE: SALE RETURN", font=("Arial", 10, "bold"), fg="red", bg="#1b263b").pack()

        # === SEARCH BAR ===
        search_frame = tk.Frame(self.root, bg="#0d1b2a", pady=15)
        search_frame.pack(fill=tk.X, padx=30)

        tk.Label(search_frame, text="🔍 Scan Barcode or Search Product:", font=("Arial", 12), fg="white", bg="#0d1b2a").pack(anchor="w")

        # Search Entry
        entry_frame = tk.Frame(search_frame, bg="#0d1b2a")
        entry_frame.pack(fill=tk.X, pady=5)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(entry_frame, textvariable=self.search_var, font=("Arial", 14), width=50, bg="#1b263b", fg="white", insertbackground="white")
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.focus()
        self.search_entry.bind("<Return>", self.add_to_cart)
        self.search_entry.bind("<KeyRelease>", self.on_search_change)

        # Manual Add Button
        tk.Button(entry_frame, text="➕ Add Manually", font=("Arial", 11), bg="#0d1b2a", fg="gold", relief=tk.FLAT,
                  command=self.add_manually).pack(side=tk.RIGHT, padx=10)

        # Search Dropdown (hidden by default)
        self.dropdown_frame = tk.Frame(search_frame, bg="white", relief=tk.RAISED, borderwidth=1)
        self.dropdown_frame.place_forget()  # Hidden initially

        self.dropdown_listbox = tk.Listbox(self.dropdown_frame, font=("Arial", 12), height=5, bg="white", fg="#0d1b2a")
        self.dropdown_listbox.pack(fill=tk.BOTH, expand=True)
        self.dropdown_listbox.bind("<Double-Button-1>", self.on_dropdown_select)

        # === CART DISPLAY ===
        cart_frame = tk.Frame(self.root, bg="#0d1b2a", padx=30, pady=10)
        cart_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(cart_frame, text="🛒 CURRENT ORDER", font=("Arial", 14, "bold"), fg="gold", bg="#0d1b2a").pack(anchor="w", pady=(0,10))

        # Cart Treeview
        tree_frame = tk.Frame(cart_frame, bg="white", relief=tk.RAISED, borderwidth=1)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.cart_tree = ttk.Treeview(tree_frame, columns=("Item", "Qty", "Price", "Total"), show="headings", height=15)
        self.cart_tree.heading("Item", text="Item")
        self.cart_tree.heading("Qty", text="Qty")
        self.cart_tree.heading("Price", text="Price")
        self.cart_tree.heading("Total", text="Total")
        self.cart_tree.column("Item", width=400)
        self.cart_tree.column("Qty", width=100)
        self.cart_tree.column("Price", width=150)
        self.cart_tree.column("Total", width=150)
        self.cart_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.cart_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cart_tree.configure(yscrollcommand=scrollbar.set)

        # Style Treeview for dark theme
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="#0d1b2a", fieldbackground="white", font=("Arial", 11))
        style.configure("Treeview.Heading", background="#1b263b", foreground="gold", font=("Arial", 11, "bold"))
        style.map("Treeview", background=[('selected', '#0d1b2a')], foreground=[('selected', 'gold')])

        # === BOTTOM ACTION BAR ===
        bottom_frame = tk.Frame(self.root, bg="#1b263b", height=100)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Left: Payment Method
        payment_frame = tk.Frame(bottom_frame, bg="#1b263b")
        payment_frame.pack(side=tk.LEFT, padx=30, pady=20)

        tk.Label(payment_frame, text="💳 Payment Method:", font=("Arial", 12), fg="white", bg="#1b263b").pack(anchor="w")
        self.payment_var = tk.StringVar(value="cash")
        tk.Radiobutton(payment_frame, text="Cash", variable=self.payment_var, value="cash", font=("Arial", 11),
                       bg="#1b263b", fg="white", selectcolor="#0d1b2a", activebackground="#1b263b").pack(anchor="w")
        tk.Radiobutton(payment_frame, text="Credit Card", variable=self.payment_var, value="credit_card", font=("Arial", 11),
                       bg="#1b263b", fg="white", selectcolor="#0d1b2a", activebackground="#1b263b").pack(anchor="w")

        # Center: Totals
        totals_frame = tk.Frame(bottom_frame, bg="#1b263b")
        totals_frame.pack(side=tk.LEFT, padx=60, pady=20)

        self.subtotal_var = tk.StringVar(value="Rs. 0.00")
        self.discount_var = tk.DoubleVar(value=0.0)
        self.total_var = tk.StringVar(value="Rs. 0.00")

        tk.Label(totals_frame, text="Subtotal:", font=("Arial", 12), fg="white", bg="#1b263b").pack(anchor="w")
        tk.Label(totals_frame, textvariable=self.subtotal_var, font=("Arial", 14, "bold"), fg="gold", bg="#1b263b").pack(anchor="w", pady=(0,5))

        disc_frame = tk.Frame(totals_frame, bg="#1b263b")
        disc_frame.pack(anchor="w", pady=(5,5))
        tk.Label(disc_frame, text="Discount (Rs.):", font=("Arial", 11), fg="white", bg="#1b263b").pack(side=tk.LEFT)
        tk.Entry(disc_frame, textvariable=self.discount_var, font=("Arial", 11), width=8, bg="#0d1b2a", fg="white").pack(side=tk.LEFT, padx=5)
        self.discount_var.trace("w", lambda *args: self.update_cart_display())

        tk.Label(totals_frame, text="TOTAL:", font=("Arial", 14, "bold"), fg="white", bg="#1b263b").pack(anchor="w", pady=(10,5))
        tk.Label(totals_frame, textvariable=self.total_var, font=("Arial", 18, "bold"), fg="gold", bg="#1b263b").pack(anchor="w")

        # Right: Action Buttons
        btn_frame = tk.Frame(bottom_frame, bg="#1b263b")
        btn_frame.pack(side=tk.RIGHT, padx=30, pady=20)

        buttons = [
            ("📌 Put on Hold", self.hold_invoice, "#FFA500"),
            ("🖨️ Save & Print", self.complete_sale, "#2E8B57"),
            ("↩️ Sale Return", self.start_return_from_pos, "#DC143C"),
            ("❌ Cancel", self.go_back, "#A9A9A9")
        ]

        for text, cmd, color in buttons:
            tk.Button(btn_frame, text=text, font=("Arial", 11, "bold"), bg=color, fg="white", width=15, height=2,
                      command=cmd).pack(pady=5)

    def update_datetime(self):
        now = datetime.now().strftime("%A, %d %B %Y - %I:%M:%S %p")
        self.datetime_label.config(text=now)
        self.root.after(1000, self.update_datetime)  # Update every second

    def on_loyalty_scan(self, event=None):
        card_no = self.loyalty_var.get().strip()
        if not card_no:
            return

        # In real system: query loyalty DB
        # For demo: just set customer name based on card
        fake_customers = {
            "L12345": "Ali Khan - 0300-1234567",
            "L67890": "Sana Malik - 0321-7654321",
            "L11223": "Omar Farooq - 0333-9998888"
        }

        if card_no in fake_customers:
            parts = fake_customers[card_no].split(" - ")
            self.customer_var.set(parts[0])
            self.phone_var.set(parts[1])
            show_info("Loyalty Card", f"Welcome {parts[0]}!")
        else:
            show_warning("Not Found", "Loyalty card not registered.")

    def on_search_change(self, event=None):
        query = self.search_var.get().strip()
        if len(query) < 2:
            self.dropdown_frame.place_forget()
            return

        # Show dropdown
        x = self.search_entry.winfo_rootx() - self.root.winfo_rootx()
        y = self.search_entry.winfo_rooty() - self.root.winfo_rooty() + self.search_entry.winfo_height()
        self.dropdown_frame.place(x=x, y=y, width=self.search_entry.winfo_width())

        # Clear & populate
        self.dropdown_listbox.delete(0, tk.END)
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, name, price, barcode FROM products WHERE name LIKE ? OR barcode LIKE ? LIMIT 5",
                  (f"%{query}%", f"%{query}%"))
        self.search_results = c.fetchall()
        conn.close()

        for row in self.search_results:
            display = f"{row[1]} - Rs. {row[2]:.2f} (Barcode: {row[3]})"
            self.dropdown_listbox.insert(tk.END, display)

    def on_dropdown_select(self, event=None):
        selection = self.dropdown_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        product = self.search_results[index]
        self.search_var.set("")  # Clear search
        self.dropdown_frame.place_forget()
        self.add_product_to_cart(product)

    def add_manually(self):
        # Show product selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Product Manually")
        dialog.geometry("500x400")
        dialog.configure(bg="#0d1b2a")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Select Product:", font=("Arial", 14, "bold"), fg="gold", bg="#0d1b2a").pack(pady=20)

        # Listbox
        listbox = tk.Listbox(dialog, font=("Arial", 12), bg="white", fg="#0d1b2a", height=15)
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, name, price, stock FROM products ORDER BY name")
        products = c.fetchall()
        conn.close()

        for p in products:
            listbox.insert(tk.END, f"{p[1]} - Rs. {p[2]:.2f} (Stock: {p[3]})")

        def on_select():
            selection = listbox.curselection()
            if selection:
                product = products[selection[0]]
                dialog.destroy()
                self.add_product_to_cart(product)

        tk.Button(dialog, text="Add Selected", font=("Arial", 12), bg="green", fg="white", command=on_select).pack(pady=10)
        tk.Button(dialog, text="Cancel", font=("Arial", 12), bg="gray", fg="white", command=dialog.destroy).pack()

    def add_to_cart(self, event=None):
        query = self.search_var.get().strip()
        if not query:
            return

        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if barcode matches multiple products
        c.execute("""
            SELECT p.id, p.name, p.selling_price, p.stock, p.barcode,
                   pv.variant_value as size
            FROM products p
            LEFT JOIN product_variants pv ON p.id = pv.product_id AND pv.variant_name = 'Size'
            WHERE p.barcode = ? OR p.id IN (
                SELECT product_id FROM product_variants WHERE barcode = ?
            )
        """, (query, query))
        
        products = c.fetchall()
        conn.close()

        if not products:
            show_warning("Not Found", "Product not found.")
            return

        # If only one product, add it directly
        if len(products) == 1:
            product = products[0]
            if not self.return_mode and product[3] <= 0:
                show_warning("Out of Stock", f"{product[1]} is out of stock!")
                return
            self.search_var.set("")
            self.dropdown_frame.place_forget()
            self.add_product_to_cart_from_db(product)
        else:
            # Multiple products found - show selection dialog
            self.show_duplicate_barcode_dialog(query, products)

    def show_duplicate_barcode_dialog(self, barcode, products):
        """Show dialog when multiple products have the same barcode"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Product")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg="white")

        tk.Label(dialog, text=f"⚠️ Multiple products found for barcode: {barcode}", 
                 font=("Arial", 12, "bold"), bg="white", fg="red").pack(pady=10)

        # Listbox with product details
        list_frame = tk.Frame(dialog, bg="white")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        listbox = tk.Listbox(list_frame, font=("Arial", 11), height=10, bg="white", fg="#0d1b2a")
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.configure(yscrollcommand=scrollbar.set)

        # Populate list
        for prod in products:
            name = prod[1]
            size = prod[5] if prod[5] else "Standard"
            price = f"Rs. {prod[2]:.2f}" if prod[2] is not None else "Rs. 0.00"
            stock = f"Stock: {prod[3]}" if prod[3] is not None else "Stock: 0"
            display = f"{name} | Size: {size} | {price} | {stock}"
            listbox.insert(tk.END, display)

        def on_select():
            selection = listbox.curselection()
            if selection:
                product = products[selection[0]]
                dialog.destroy()
                self.search_var.set("")
                self.dropdown_frame.place_forget()
                self.add_product_to_cart_from_db(product)

        def on_cancel():
            dialog.destroy()
            self.search_var.set("")

        # Buttons
        btn_frame = tk.Frame(dialog, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Select", font=("Arial", 12, "bold"), bg="green", fg="white",
                  width=12, command=on_select).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="Cancel", font=("Arial", 12, "bold"), bg="gray", fg="white",
                  width=12, command=on_cancel).pack(side=tk.LEFT, padx=10)

        # Bind double-click
        listbox.bind("<Double-1>", lambda e: on_select())
        listbox.focus()

    def add_product_to_cart_from_db(self, product):
        """Add product from database query result"""
        # Check if product already in cart
        existing_item = None
        for item in self.cart:
            if item['id'] == product[0]:
                existing_item = item
                break

        if existing_item:
            existing_item['qty'] += 1.0
            existing_item['total'] = existing_item['qty'] * existing_item['price']
        else:
            item = {
                'id': product[0],
                'name': product[1],
                'price': product[2] if product[2] is not None else 0.0,
                'qty': 1.0
            }
            item['total'] = item['price'] * item['qty']
            self.cart.append(item)

        self.update_cart_display()

    def add_product_to_cart(self, product):
        """Add product from manual selection (legacy method)"""
        # Check if product already in cart
        existing_item = None
        for item in self.cart:
            if item['id'] == product[0]:
                existing_item = item
                break

        if existing_item:
            existing_item['qty'] += 1.0
            existing_item['total'] = existing_item['qty'] * existing_item['price']
        else:
            item = {
                'id': product[0],
                'name': product[1],
                'price': product[2],
                'qty': 1.0
            }
            item['total'] = item['price'] * item['qty']
            self.cart.append(item)

        self.update_cart_display()

    def update_cart_display(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        subtotal = 0
        for item in self.cart:
            self.cart_tree.insert("", "end", values=(
                item['name'],
                f"{item['qty']:.2f}",
                f"Rs. {item['price']:.2f}",
                f"Rs. {item['total']:.2f}"
            ))
            subtotal += item['total']

        discount = self.discount_var.get() or 0.0
        total = subtotal - discount

        self.subtotal_var.set(f"Rs. {subtotal:,.2f}")
        self.total_var.set(f"Rs. {total:,.2f}")

    def complete_sale(self):
        if not self.cart:
            show_warning("Empty Cart", "Add items before completing sale.")
            return

        customer = self.customer_var.get().strip() or "Walk-in Customer"
        phone = self.phone_var.get().strip()
        discount = self.discount_var.get() or 0.0
        subtotal = sum(item['total'] for item in self.cart)
        total = subtotal - discount
        payment_method = self.payment_var.get()

        conn = get_db_connection()
        c = conn.cursor()

        try:
            c.execute("""
                INSERT INTO sales (invoice_no, customer_name, total, discount, payment_method, is_held, cashier_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (self.invoice_no, f"{customer} | {phone}" if phone else customer, total, discount, payment_method, 0, self.user['id']))

            sale_id = c.lastrowid

            for item in self.cart:
                c.execute("""
                    INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, total_price)
                    VALUES (?, ?, ?, ?, ?)
                """, (sale_id, item['id'], item['qty'], item['price'], item['total']))

                # Reduce stock
                c.execute("UPDATE products SET stock = stock - ? WHERE id = ?",
                          (item['qty'], item['id']))

            conn.commit()
            show_info("Success", f"✅ Sale completed!\nInvoice: {self.invoice_no}\nTotal: Rs. {total:,.2f}")
            self.go_back()

        except Exception as e:
            conn.rollback()
            show_error("Error", f"Sale failed: {str(e)}")
        finally:
            conn.close()

    def hold_invoice(self):
        if not self.cart:
            show_warning("Empty Cart", "Add items before holding invoice.")
            return

        customer = self.customer_var.get().strip() or "Walk-in Customer"
        phone = self.phone_var.get().strip()
        discount = self.discount_var.get() or 0.0
        subtotal = sum(item['total'] for item in self.cart)
        total = subtotal - discount

        conn = get_db_connection()
        c = conn.cursor()

        try:
            c.execute("""
                INSERT INTO sales (invoice_no, customer_name, total, discount, payment_method, is_held, cashier_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (self.invoice_no, f"{customer} | {phone}" if phone else customer, total, discount, "cash", 1, self.user['id']))

            sale_id = c.lastrowid

            for item in self.cart:
                c.execute("""
                    INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, total_price)
                    VALUES (?, ?, ?, ?, ?)
                """, (sale_id, item['id'], item['qty'], item['price'], item['total']))

            conn.commit()
            show_info("Held", f"📌 Invoice {self.invoice_no} held for {customer}")
            self.go_back()

        except Exception as e:
            conn.rollback()
            show_error("Error", f"Hold failed: {str(e)}")
        finally:
            conn.close()

    def start_return_from_pos(self):
        invoice_no = simpledialog.askstring("Sale Return", "Enter Invoice Number to return:")
        if not invoice_no:
            return

        from .pos import POSWindow  # Avoid circular import at top
        POSWindow(self.root, self.user, return_mode=True, invoice_no=invoice_no)

    def load_return_invoice(self, invoice_no):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, customer_name, discount FROM sales WHERE invoice_no = ? AND is_return = 0", (invoice_no,))
        sale = c.fetchone()

        if not sale:
            show_error("Not Found", "Invoice not found or already returned.")
            conn.close()
            self.go_back()
            return

        c.execute("""
            SELECT si.product_id, p.name, si.quantity, si.unit_price, si.total_price
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            WHERE si.sale_id = ?
        """, (sale[0],))
        items = c.fetchall()
        conn.close()

        # Parse customer name and phone
        customer_info = sale[1].split(" | ")
        self.customer_var.set(customer_info[0])
        if len(customer_info) > 1:
            self.phone_var.set(customer_info[1])

        if sale[2]:
            self.discount_var.set(sale[2])

        self.cart = []
        for item in items:
            self.cart.append({
                'id': item[0],
                'name': item[1],
                'price': item[3],
                'qty': -item[2]  # Negative for return
            })
        self.update_cart_display()

    def go_back(self):
        from .main_menu import MainMenu
        MainMenu(self.root, self.user)