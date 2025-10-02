# gui/inventory/inventory_main.py
import tkinter as tk
from tkinter import ttk
from utils import clear_window

class InventoryDashboard:
    def go_back(self):
        from ..main_menu import MainMenu
        MainMenu(self.root, self.user)
    
    
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        clear_window(self.root)
        self.root.title("📦 Inventory Management - Crown Supermarket")
        self.root.configure(bg="#0d1b2a")

        # === TOP BAR ===
        top_frame = tk.Frame(self.root, bg="#1b263b", height=80)
        top_frame.pack(fill=tk.X)

        tk.Label(top_frame, text="👑 CROWN SUPERMARKET", font=("Arial", 16, "bold"), fg="gold", bg="#1b263b").pack(side=tk.LEFT, padx=20)
        tk.Label(top_frame, text="📦 INVENTORY DASHBOARD", font=("Arial", 14), fg="white", bg="#1b263b").pack(side=tk.LEFT, padx=10)
        tk.Label(top_frame, text=f"👤 {self.user['full_name']}", font=("Arial", 12), fg="#90e0ef", bg="#1b263b").pack(side=tk.RIGHT, padx=20)

        # === TABS ===
        tab_frame = tk.Frame(self.root, bg="#0d1b2a")
        tab_frame.pack(fill=tk.X, padx=20, pady=20)

        tabs = [
            ("🏷️ Categories", self.open_categories),
            ("📦 Items", self.open_items),
            ("🚚 Suppliers", self.open_suppliers),
            ("🧾 Taxes", self.open_taxes),
            ("📏 UOM", self.open_uom)
        ]

        for text, command in tabs:
            tk.Button(tab_frame, text=text, font=("Arial", 12, "bold"), bg="#1b263b", fg="white",
                      relief=tk.FLAT, padx=15, pady=8, command=command).pack(side=tk.LEFT, padx=5)

        
        # Back Button (far right)
        tk.Button(tab_frame, text="⬅️ Back to Main Menu", font=("Arial", 12, "bold"), bg="#A9A9A9", fg="white",
        relief=tk.FLAT, padx=15, pady=8, command=self.go_back).pack(side=tk.RIGHT, padx=20)
                
        
        # === CONTENT AREA ===
        self.content_frame = tk.Frame(self.root, bg="white")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,20))

        self.show_welcome()

    def show_welcome(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        tk.Label(self.content_frame, text="📦 Welcome to Inventory Management", font=("Arial", 20, "bold"), bg="white", fg="#0d1b2a").pack(pady=50)
        tk.Label(self.content_frame, text="Use tabs above to manage categories, items, suppliers, taxes, and units of measurement.", 
                 font=("Arial", 12), bg="white", fg="#666", wraplength=800).pack(pady=10)

    def open_categories(self):
        from .categories import CategoriesManager
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        CategoriesManager(self.content_frame, self.user)

    def open_items(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        from .items import ItemsManager
        ItemsManager(self.content_frame, self.user)

    def open_suppliers(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        from .suppliers import SuppliersManager
        SuppliersManager(self.content_frame, self.user)

    def open_taxes(self):
        tk.Label(self.content_frame, text="🧾 Taxes Module (Coming Soon)", font=("Arial", 18), bg="white").pack(pady=50)

    def open_uom(self):
        tk.Label(self.content_frame, text="📏 UOM Module (Coming Soon)", font=("Arial", 18), bg="white").pack(pady=50)