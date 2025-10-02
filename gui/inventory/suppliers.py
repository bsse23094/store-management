# gui/inventory/suppliers.py
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from utils import clear_window
from database import fetch_all, fetch_one, execute_query

class SuppliersManager:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.setup_ui()
        self.load_suppliers()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.parent, bg="#1b263b", height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="🚚 Supplier Directory", font=("Arial", 16, "bold"), fg="gold", bg="#1b263b").pack(pady=15)

        # Action Buttons
        btn_frame = tk.Frame(self.parent, bg="white")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(btn_frame, text="➕ Add Supplier", font=("Arial", 11, "bold"), bg="#2E8B57", fg="white",
                  command=self.add_supplier).pack(side=tk.LEFT, padx=5)

        # Suppliers Table
        tree_frame = tk.Frame(self.parent, bg="white", relief=tk.RAISED, borderwidth=1)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("ID", "Name", "NTN", "GST", "Address", "Payment Terms", "Order Days", "Reps", "Actions")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        col_widths = {
            "ID": 50,
            "Name": 150,
            "NTN": 100,
            "GST": 100,
            "Address": 200,
            "Payment Terms": 120,
            "Order Days": 120,
            "Reps": 80,
            "Actions": 120
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            width = col_widths.get(col, 100)
            anchor = "center" if col == "ID" else "w"
            self.tree.column(col, width=width, anchor=anchor)

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
        style.configure("Treeview", background="white", foreground="#0d1b2a", fieldbackground="white", font=("Arial", 10))
        style.configure("Treeview.Heading", background="#1b263b", foreground="gold", font=("Arial", 10, "bold"))
        style.map("Treeview", background=[('selected', '#0d1b2a')], foreground=[('selected', 'gold')])

        # Bind double-click to edit
        self.tree.bind("<Double-1>", self.edit_supplier)

    def load_suppliers(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            suppliers = fetch_all("""
                SELECT id, name, ntn, gst, address, payment_terms, order_days
                FROM suppliers
                ORDER BY name
            """)

            for sup in suppliers:
                # Get rep count
                rep_count = fetch_one("SELECT COUNT(*) FROM supplier_reps WHERE supplier_id = ?", (sup[0],))
                reps = rep_count[0] if rep_count else 0
                
                # Format order days
                order_days = sup[6] or "None"
                if order_days != "None":
                    try:
                        import json
                        days_list = json.loads(order_days)
                        order_days = ", ".join(days_list)
                    except:
                        pass

                self.tree.insert("", "end", iid=sup[0], values=(
                    sup[0], sup[1], sup[2] or "", sup[3] or "", sup[4] or "", 
                    sup[5] or "", order_days, f"{reps} reps", "✏️ 🗑️ 👥"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load suppliers: {str(e)}")

    def add_supplier(self):
        dialog = SupplierDialog(self.parent, self.user, None, self.load_suppliers)
        dialog.window.grab_set()

    def edit_supplier(self, event=None):
        selection = self.tree.selection()
        if not selection:
            return
            
        supplier_id = int(selection[0])
        dialog = SupplierDialog(self.parent, self.user, supplier_id, self.load_suppliers)
        dialog.window.grab_set()

    def delete_supplier(self, supplier_id):
        if messagebox.askyesno("Confirm Delete", "Delete this supplier and all representatives?"):
            try:
                execute_query("DELETE FROM supplier_reps WHERE supplier_id = ?", (supplier_id,))
                execute_query("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
                self.load_suppliers()
                messagebox.showinfo("Success", "Supplier deleted!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {str(e)}")

    def view_reps(self, supplier_id):
        reps_window = tk.Toplevel(self.parent)
        reps_window.title("👥 Supplier Representatives")
        reps_window.geometry("600x400")
        reps_window.configure(bg="white")

        tk.Label(reps_window, text="Representatives", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        # Get supplier name
        sup = fetch_one("SELECT name FROM suppliers WHERE id = ?", (supplier_id,))
        if sup:
            tk.Label(reps_window, text=f"For: {sup[0]}", font=("Arial", 10), bg="white", fg="gray").pack()

        # Reps table
        cols = ("Name", "Designation", "Contact")
        rep_tree = ttk.Treeview(reps_window, columns=cols, show="headings", height=10)
        for col in cols:
            rep_tree.heading(col, text=col)
            rep_tree.column(col, width=180)
        rep_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Load reps
        reps = fetch_all("SELECT name, designation, contact FROM supplier_reps WHERE supplier_id = ?", (supplier_id,))
        for rep in reps:
            rep_tree.insert("", "end", values=rep)

        # Add Rep Button
        def add_rep():
            AddRepDialog(reps_window, supplier_id, lambda: self.load_reps_in_window(rep_tree, supplier_id))

        tk.Button(reps_window, text="➕ Add Representative", command=add_rep).pack(pady=10)

    def load_reps_in_window(self, tree, supplier_id):
        for item in tree.get_children():
            tree.delete(item)
        reps = fetch_all("SELECT name, designation, contact FROM supplier_reps WHERE supplier_id = ?", (supplier_id,))
        for rep in reps:
            tree.insert("", "end", values=rep)


class SupplierDialog:
    def __init__(self, parent, user, supplier_id, refresh_callback):
        self.parent = parent
        self.user = user
        self.supplier_id = supplier_id
        self.refresh_callback = refresh_callback
        self.window = tk.Toplevel(parent)
        self.window.title("➕ Add Supplier" if supplier_id is None else "✏️ Edit Supplier")
        self.window.geometry("700x600")
        self.window.configure(bg="white")
        self.setup_ui()
        if supplier_id:
            self.load_supplier_data()

    def setup_ui(self):
        # Scrollable frame
        canvas = tk.Canvas(self.window, bg="white")
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Supplier Info
        tk.Label(scrollable_frame, text="Supplier Information", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        fields = [
            ("Supplier Name*", "name"),
            ("NTN", "ntn"),
            ("GST", "gst"),
            ("Address", "address"),
            ("Payment Terms", "payment_terms")
        ]

        self.entries = {}
        for label, field in fields:
            frame = tk.Frame(scrollable_frame, bg="white")
            frame.pack(fill=tk.X, padx=20, pady=5)
            tk.Label(frame, text=label, font=("Arial", 11), bg="white", width=20, anchor="w").pack(side=tk.LEFT)
            entry = tk.Entry(frame, font=("Arial", 11), width=40)
            entry.pack(side=tk.LEFT)
            self.entries[field] = entry

        # Order Days
        tk.Label(scrollable_frame, text="Order Days", font=("Arial", 14, "bold"), bg="white").pack(pady=(20, 10))
        
        days_frame = tk.Frame(scrollable_frame, bg="white")
        days_frame.pack(fill=tk.X, padx=20)
        
        self.day_vars = {}
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for i, day in enumerate(days):
            var = tk.BooleanVar()
            self.day_vars[day] = var
            tk.Checkbutton(days_frame, text=day, variable=var, bg="white", font=("Arial", 10)).grid(row=i//4, column=i%4, sticky="w", padx=10, pady=2)

        # Representatives Section
        tk.Label(scrollable_frame, text="Representatives", font=("Arial", 14, "bold"), bg="white").pack(pady=(20, 10))
        
        self.reps_frame = tk.Frame(scrollable_frame, bg="white")
        self.reps_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(scrollable_frame, text="➕ Add Representative", font=("Arial", 11), bg="#1E90FF", fg="white",
                  command=self.add_rep_row).pack(pady=10)

        # Action Buttons
        btn_frame = tk.Frame(scrollable_frame, bg="white")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="💾 Save Supplier", font=("Arial", 12, "bold"), bg="#2E8B57", fg="white",
                  command=self.save_supplier).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Cancel", font=("Arial", 12, "bold"), bg="#A9A9A9", fg="white",
                  command=self.window.destroy).pack(side=tk.LEFT, padx=10)

        self.rep_rows = []

    def add_rep_row(self):
        rep_frame = tk.Frame(self.reps_frame, bg="white")
        rep_frame.pack(fill=tk.X, pady=5)
        
        entries = {}
        fields = [("Name*", "name"), ("Designation", "designation"), ("Contact*", "contact")]
        
        for label, field in fields:
            frame = tk.Frame(rep_frame, bg="white")
            frame.pack(side=tk.LEFT, padx=5)
            tk.Label(frame, text=label, font=("Arial", 9), bg="white").pack()
            entry = tk.Entry(frame, font=("Arial", 9), width=15)
            entry.pack()
            entries[field] = entry
        
        # Remove button
        remove_btn = tk.Button(rep_frame, text="🗑️", command=lambda f=rep_frame: f.destroy())
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        entries['frame'] = rep_frame
        self.rep_rows.append(entries)

    def load_supplier_data(self):
        sup = fetch_one("""
            SELECT name, ntn, gst, address, payment_terms, order_days
            FROM suppliers WHERE id = ?
        """, (self.supplier_id,))
        
        if sup:
            self.entries['name'].insert(0, sup[0] or "")
            self.entries['ntn'].insert(0, sup[1] or "")
            self.entries['gst'].insert(0, sup[2] or "")
            self.entries['address'].insert(0, sup[3] or "")
            self.entries['payment_terms'].insert(0, sup[4] or "")
            
            # Load order days
            if sup[5]:
                try:
                    import json
                    days_list = json.loads(sup[5])
                    for day in days_list:
                        if day in self.day_vars:
                            self.day_vars[day].set(True)
                except:
                    pass
            
            # Load representatives
            reps = fetch_all("SELECT name, designation, contact FROM supplier_reps WHERE supplier_id = ?", (self.supplier_id,))
            for rep in reps:
                self.add_rep_row()
                self.rep_rows[-1]['name'].insert(0, rep[0] or "")
                self.rep_rows[-1]['designation'].insert(0, rep[1] or "")
                self.rep_rows[-1]['contact'].insert(0, rep[2] or "")

    def save_supplier(self):
        name = self.entries['name'].get().strip()
        if not name:
            messagebox.showwarning("Missing Info", "Supplier name is required.")
            return

        # Get order days
        selected_days = [day for day, var in self.day_vars.items() if var.get()]
        order_days_json = json.dumps(selected_days) if selected_days else None

        try:
            if self.supplier_id is None:
                # Insert new supplier
                self.supplier_id = execute_query("""
                    INSERT OR IGNORE INTO suppliers (name, ntn, gst, address, payment_terms, order_days)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    name,
                    self.entries['ntn'].get().strip() or None,
                    self.entries['gst'].get().strip() or None,
                    self.entries['address'].get().strip() or None,
                    self.entries['payment_terms'].get().strip() or None,
                    order_days_json
                ))
            else:
                # Update existing supplier
                execute_query("""
                    UPDATE suppliers SET name = ?, ntn = ?, gst = ?, address = ?, payment_terms = ?, order_days = ?
                    WHERE id = ?
                """, (
                    name,
                    self.entries['ntn'].get().strip() or None,
                    self.entries['gst'].get().strip() or None,
                    self.entries['address'].get().strip() or None,
                    self.entries['payment_terms'].get().strip() or None,
                    order_days_json,
                    self.supplier_id
                ))

            # Save representatives
            execute_query("DELETE FROM supplier_reps WHERE supplier_id = ?", (self.supplier_id,))
            
            for rep in self.rep_rows:
                name_val = rep['name'].get().strip()
                contact_val = rep['contact'].get().strip()
                if name_val and contact_val:
                    execute_query("""
                        INSERT INTO supplier_reps (supplier_id, name, designation, contact)
                        VALUES (?, ?, ?, ?)
                    """, (
                        self.supplier_id,
                        name_val,
                        rep['designation'].get().strip() or None,
                        contact_val
                    ))

            messagebox.showinfo("Success", "Supplier saved successfully!")
            self.refresh_callback()
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save supplier: {str(e)}")


class AddRepDialog:
    def __init__(self, parent, supplier_id, refresh_callback):
        self.parent = parent
        self.supplier_id = supplier_id
        self.refresh_callback = refresh_callback
        self.window = tk.Toplevel(parent)
        self.window.title("➕ Add Representative")
        self.window.geometry("400x250")
        self.window.configure(bg="white")
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.window, text="Add Representative", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        fields = [("Name*", "name"), ("Designation", "designation"), ("Contact*", "contact")]
        self.entries = {}
        
        for label, field in fields:
            frame = tk.Frame(self.window, bg="white")
            frame.pack(fill=tk.X, padx=20, pady=5)
            tk.Label(frame, text=label, font=("Arial", 11), bg="white").pack(anchor="w")
            entry = tk.Entry(frame, font=("Arial", 11), width=30)
            entry.pack(fill=tk.X)
            self.entries[field] = entry

        btn_frame = tk.Frame(self.window, bg="white")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="💾 Save", font=("Arial", 12, "bold"), bg="#2E8B57", fg="white",
                  command=self.save_rep).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="❌ Cancel", font=("Arial", 12, "bold"), bg="#A9A9A9", fg="white",
                  command=self.window.destroy).pack(side=tk.LEFT, padx=10)

    def save_rep(self):
        name = self.entries['name'].get().strip()
        contact = self.entries['contact'].get().strip()
        
        if not name or not contact:
            messagebox.showwarning("Missing Info", "Name and Contact are required.")
            return

        try:
            execute_query("""
                INSERT INTO supplier_reps (supplier_id, name, designation, contact)
                VALUES (?, ?, ?, ?)
            """, (
                self.supplier_id,
                name,
                self.entries['designation'].get().strip() or None,
                contact
            ))
            
            messagebox.showinfo("Success", "Representative added!")
            self.refresh_callback()
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add representative: {str(e)}")