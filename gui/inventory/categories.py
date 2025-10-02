# gui/inventory/categories.py
import tkinter as tk
from tkinter import ttk, messagebox, Menu
from database import get_db_connection

class CategoriesManager:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.setup_ui()
        self.load_categories()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.parent, bg="#1b263b", height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="🏷️ Product Categories", font=("Arial", 16, "bold"), fg="gold", bg="#1b263b").pack(pady=15)

        # Action Buttons
        btn_frame = tk.Frame(self.parent, bg="white")
        btn_frame.pack(fill=tk.X, pady=10)

        tk.Button(btn_frame, text="➕ Add Category", font=("Arial", 11, "bold"), bg="#2E8B57", fg="white",
                  command=self.add_empty_row).pack(side=tk.LEFT, padx=10)

        # Navigation Arrows - HORIZONTAL
        arrow_frame = tk.Frame(btn_frame, bg="white", relief=tk.RAISED, borderwidth=1)
        arrow_frame.pack(side=tk.LEFT, padx=30)

        self.move_left_btn = tk.Button(arrow_frame, text="◀️", font=("Arial", 12, "bold"), width=4, height=1,
                                       bg="#4682B4", fg="white", relief=tk.FLAT, command=self.move_left)
        self.move_left_btn.pack(side=tk.LEFT, padx=2)

        up_down_frame = tk.Frame(arrow_frame, bg="white")
        up_down_frame.pack(side=tk.LEFT, padx=2)
        self.move_up_btn = tk.Button(up_down_frame, text="▲", font=("Arial", 10, "bold"), width=4, height=1,
                                     bg="#4682B4", fg="white", relief=tk.FLAT, command=self.move_up)
        self.move_up_btn.pack()
        self.move_down_btn = tk.Button(up_down_frame, text="▼", font=("Arial", 10, "bold"), width=4, height=1,
                                       bg="#4682B4", fg="white", relief=tk.FLAT, command=self.move_down)
        self.move_down_btn.pack()

        self.move_right_btn = tk.Button(arrow_frame, text="▶️", font=("Arial", 12, "bold"), width=4, height=1,
                                        bg="#4682B4", fg="white", relief=tk.FLAT, command=self.move_right)
        self.move_right_btn.pack(side=tk.LEFT, padx=2)

        # Treeview
        tree_frame = tk.Frame(self.parent, bg="white", relief=tk.RAISED, borderwidth=1)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Location"), show="tree headings", height=20)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Category Name")
        self.tree.heading("Location", text="Location Tag")
        self.tree.column("#0", width=300, minwidth=200)
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Name", width=300)
        self.tree.column("Location", width=150)

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
                        font=("Arial", 11),
                        rowheight=28)
        style.configure("Treeview.Heading", 
                        background="#1b263b", 
                        foreground="gold", 
                        font=("Arial", 11, "bold"),
                        padding=5)
        style.map("Treeview", 
                  background=[('selected', '#0d1b2a')], 
                  foreground=[('selected', 'gold')])

        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)

        self.context_menu = Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="✏️ Edit", command=self.start_edit)
        self.context_menu.add_command(label="🗑️ Delete", command=self.delete_category)

        self.editing_item = None
        self.editing_column = None
        self.entry = None

    def save_expanded_state(self):
        """Save which nodes are expanded"""
        self.expanded_nodes = []
        def traverse(item):
            if self.tree.item(item, "open"):
                self.expanded_nodes.append(item)
            for child in self.tree.get_children(item):
                traverse(child)
        for child in self.tree.get_children():
            traverse(child)

    def restore_expanded_state(self):
        """Re-expand nodes that were expanded before reload"""
        def traverse(item):
            if item in self.expanded_nodes:
                self.tree.item(item, open=True)
            for child in self.tree.get_children(item):
                traverse(child)
        for child in self.tree.get_children():
            traverse(child)

    def load_categories(self):
        # Save expanded state before reload
        self.save_expanded_state()
        
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, name, parent_id, location_tag FROM categories ORDER BY name")
        categories = c.fetchall()
        conn.close()

        self.category_map = {cat[0]: cat for cat in categories}

        # Insert root categories
        for cat in categories:
            if cat[2] is None:
                loc = cat[3] if cat[3] is not None else ""
                self.tree.insert("", "end", iid=cat[0], text=cat[1], values=(cat[0], cat[1], loc))

        # Insert child categories recursively
        def insert_children(parent_id, parent_iid):
            for cat in categories:
                if cat[2] == parent_id:
                    loc = cat[3] if cat[3] is not None else ""
                    child_iid = self.tree.insert(parent_iid, "end", iid=cat[0], text=cat[1], values=(cat[0], cat[1], loc))
                    insert_children(cat[0], child_iid)

        for cat in categories:
            if cat[2] is None:
                insert_children(cat[0], str(cat[0]))
        
        # Restore expanded state
        self.restore_expanded_state()

    def add_empty_row(self):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO categories (name, parent_id, location_tag) VALUES (?, ?, ?)", ("", None, ""))
        new_id = c.lastrowid
        conn.commit()
        conn.close()

        self.tree.insert("", "end", iid=new_id, text="", values=(new_id, "", ""))
        self.tree.selection_set(new_id)
        self.tree.focus(new_id)
        self.start_edit(column="Name")

    def on_double_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            self.start_edit(column=column)

    def start_edit(self, column="Name"):
        selection = self.tree.selection()
        if not selection:
            return

        item_id = selection[0]
        self.editing_item = item_id

        col_map = {"#2": "Name", "#3": "Location"}
        col_name = col_map.get(column, "Name")
        self.editing_column = col_name

        values = self.tree.item(item_id, "values")
        current = values[1] if col_name == "Name" else values[2]

        x, y, width, height = self.tree.bbox(item_id, column)
        if not x:
            self.tree.see(item_id)
            self.tree.update()
            x, y, width, height = self.tree.bbox(item_id, column)

        self.entry = tk.Entry(self.tree, font=("Arial", 11), bg="#fff9c4", relief=tk.FLAT)
        self.entry.place(x=x, y=y, width=width, height=height)
        self.entry.insert(0, current)
        self.entry.select_range(0, tk.END)
        self.entry.focus()

        self.entry.bind("<Return>", self.save_edit)
        self.entry.bind("<FocusOut>", self.cancel_edit)
        self.entry.bind("<Escape>", self.cancel_edit)

    def save_edit(self, event=None):
        if not self.entry or not self.editing_item:
            return

        new_value = self.entry.get().strip()
        col_index = 1 if self.editing_column == "Name" else 2

        values = list(self.tree.item(self.editing_item, "values"))
        values[col_index] = new_value
        self.tree.item(self.editing_item, values=values)
        if self.editing_column == "Name":
            self.tree.item(self.editing_item, text=new_value)

        conn = get_db_connection()
        c = conn.cursor()
        if self.editing_column == "Name":
            c.execute("UPDATE categories SET name = ? WHERE id = ?", (new_value, int(self.editing_item)))
        else:
            loc_val = new_value if new_value != "" else None
            c.execute("UPDATE categories SET location_tag = ? WHERE id = ?", (loc_val, int(self.editing_item)))
        conn.commit()
        conn.close()

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

    def delete_category(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Select a category to delete.")
            return

        category_id = int(selection[0])
        cat = self.category_map.get(category_id)
        if not cat:
            return

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM categories WHERE parent_id = ?", (category_id,))
        has_children = c.fetchone()[0] > 0
        conn.close()

        if has_children:
            messagebox.showwarning("Cannot Delete", "Delete sub-categories first.")
            return

        if messagebox.askyesno("Confirm", f"Delete category '{cat[1]}'?"):
            conn = get_db_connection()
            c = conn.cursor()
            try:
                c.execute("DELETE FROM categories WHERE id = ?", (category_id,))
                conn.commit()
                self.tree.delete(selection[0])
                messagebox.showinfo("Success", "Category deleted!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
            finally:
                conn.close()

    # =============== NAVIGATION ARROWS ===============
    def move_up(self):
        self._move_sibling(-1)

    def move_down(self):
        self._move_sibling(1)

    def move_left(self):
        selection = self.tree.selection()
        if not selection:
            return

        item_id = selection[0]
        parent = self.tree.parent(item_id)
        if not parent:
            messagebox.showinfo("Info", "Already at top level.")
            return

        grandparent = self.tree.parent(parent)
        self._change_parent(item_id, grandparent if grandparent else "")

    def move_right(self):
        selection = self.tree.selection()
        if not selection:
            return

        item_id = selection[0]
        prev_item = self.tree.prev(item_id)
        if not prev_item:
            messagebox.showinfo("Info", "No item above to become parent.")
            return

        self._change_parent(item_id, prev_item)

    def _move_sibling(self, direction):
        selection = self.tree.selection()
        if not selection:
            return

        item_id = selection[0]
        parent = self.tree.parent(item_id)
        siblings = list(self.tree.get_children(parent))
        if len(siblings) < 2:
            return

        idx = siblings.index(item_id)
        new_idx = idx + direction
        if 0 <= new_idx < len(siblings):
            self.tree.move(item_id, parent, new_idx)
            self.tree.selection_set(item_id)

    def _change_parent(self, item_id, new_parent_id):
        conn = get_db_connection()
        c = conn.cursor()
        try:
            parent_id = int(new_parent_id) if new_parent_id else None
            c.execute("UPDATE categories SET parent_id = ? WHERE id = ?", (parent_id, int(item_id)))
            conn.commit()
            self.load_categories()  # This now preserves expanded state!
            self.tree.selection_set(item_id)
        except Exception as e:
            messagebox.showerror("Error", f"Move failed: {str(e)}")
        finally:
            conn.close()