# gui/main_menu.py
import tkinter as tk
from tkinter import ttk
from utils import clear_window

class MainMenu:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        clear_window(self.root)
        self.root.title("🏪 Crown Supermarket Dashboard")
        self.root.configure(bg="#0d1b2a")

        # === SIDEBAR ===
        sidebar = tk.Frame(self.root, bg="#1b263b", width=220)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Logo
        tk.Label(sidebar, text="CROWN", font=("Arial", 20, "bold"), fg="gold", bg="#1b263b").pack(pady=(30, 5))
        tk.Label(sidebar, text="SUPERMARKET", font=("Arial", 10, "bold"), fg="white", bg="#1b263b").pack()

        # User Info
        tk.Label(sidebar, text=f"👤 {self.user['full_name']}", font=("Arial", 11), fg="white", bg="#1b263b").pack(pady=(40, 5))
        tk.Label(sidebar, text=f"({self.user['role'].title()})", font=("Arial", 9), fg="#90e0ef", bg="#1b263b").pack(pady=(0, 30))

        # Navigation Buttons
        buttons = self.get_nav_buttons()
        for text, command, icon in buttons:
            btn = tk.Button(
                sidebar,
                text=f"{icon} {text}",
                font=("Arial", 12),
                bg="#1b263b" if icon != "🚪" else "#770F0F",
                fg="white",
                width=18,
                height=2,
                relief=tk.FLAT,
                anchor="w",
                padx=20,
                command=command,
                cursor="hand2"
            )
            btn.pack(pady=5, padx=10)

        # === MAIN CONTENT AREA ===
        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.show_welcome()

    def get_nav_buttons(self):
        buttons = [
            ("POS", self.open_pos, "💵"),
            ("Hold Invoice", self.open_held_invoices, "📌"),
        ]

        # Admin/Manager only
        if self.user['role'] in ['admin', 'manager']:
            buttons.extend([
                ("Inventory", self.open_inventory, "📦"),
                ("Ordering", self.open_ordering, "🛒"),
                ("Sales History", self.open_sales_history, "📊"),
            ])

        buttons.append(("Logout", self.logout, "🚪"))
        return buttons

    def show_welcome(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        tk.Label(self.main_frame, text="🎉 Welcome to Crown Supermarket", font=("Arial", 24, "bold"), bg="white", fg="#0d1b2a").pack(pady=50)
        tk.Label(self.main_frame, text=f"Logged in as: {self.user['full_name']} ({self.user['role'].title()})", font=("Arial", 14), bg="white").pack(pady=10)
        tk.Label(self.main_frame, text="Use the sidebar to navigate", font=("Arial", 12), bg="white", fg="#666", wraplength=800).pack(pady=30)

    def open_pos(self):
        from .pos import POSWindow
        POSWindow(self.root, self.user)

    def open_held_invoices(self):
        from .held_invoices import HeldInvoicesWindow
        HeldInvoicesWindow(self.root, self.user)

    def open_inventory(self):
        from .inventory.inventory_main import InventoryDashboard
        InventoryDashboard(self.root, self.user)

    def open_ordering(self):
        from .ordering.ordering_main import OrderingDashboard
        OrderingDashboard(self.root, self.user)

    def open_sales_history(self):
        from .sales_history import SalesHistoryWindow
        SalesHistoryWindow(self.root, self.user)

    def logout(self):
        from .login import LoginWindow
        LoginWindow(self.root)