# gui/ordering/ordering_main.py
import tkinter as tk
from tkinter import ttk
from utils import clear_window

class OrderingDashboard:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        clear_window(self.root)
        self.root.title("📦 Ordering System - Crown Supermarket")
        self.root.configure(bg="#0d1b2a")

        # === TOP BAR ===
        top_frame = tk.Frame(self.root, bg="#1b263b", height=80)
        top_frame.pack(fill=tk.X)

        tk.Label(top_frame, text="👑 CROWN SUPERMARKET", font=("Arial", 16, "bold"), fg="gold", bg="#1b263b").pack(side=tk.LEFT, padx=20)
        tk.Label(top_frame, text="📦 ORDERING DASHBOARD", font=("Arial", 14), fg="white", bg="#1b263b").pack(side=tk.LEFT, padx=10)
        tk.Label(top_frame, text=f"👤 {self.user['full_name']}", font=("Arial", 12), fg="#90e0ef", bg="#1b263b").pack(side=tk.RIGHT, padx=20)

        # === TABS ===
        tab_frame = tk.Frame(self.root, bg="#0d1b2a")
        tab_frame.pack(fill=tk.X, padx=20, pady=20)

        tabs = [
            ("🧠 Smart Order", self.create_po),
            ("📥 Receive Goods", self.receive_goods),
            ("↩️ Returns", self.return_damaged),
            ("📊 Reports", self.show_reports)
        ]

        for text, command in tabs:
            tk.Button(tab_frame, text=text, font=("Arial", 12, "bold"), bg="#1b263b", fg="white",
                      relief=tk.FLAT, padx=15, pady=8, command=command).pack(side=tk.LEFT, padx=5)

        # Back Button
        tk.Button(tab_frame, text="⬅️ Back to Main Menu", font=("Arial", 12, "bold"), bg="#A9A9A9", fg="white",
                  relief=tk.FLAT, padx=15, pady=8, command=self.go_back).pack(side=tk.RIGHT, padx=20)

        # === CONTENT AREA ===
        self.content_frame = tk.Frame(self.root, bg="white")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,20))

        self.show_welcome()

    def show_welcome(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        tk.Label(self.content_frame, text="📦 Welcome to Ordering System", font=("Arial", 20, "bold"), bg="white", fg="#0d1b2a").pack(pady=50)
        tk.Label(self.content_frame, text="Use tabs above to manage purchase orders, receive goods, and handle returns.", 
                 font=("Arial", 12), bg="white", fg="#666", wraplength=800).pack(pady=10)

    def create_po(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        from .smart_order import SmartOrderTab
        SmartOrderTab(self.content_frame, self.user)

    def receive_goods(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        from .receive_goods import ReceiveGoodsWindow
        ReceiveGoodsWindow(self.content_frame, self.user)

    def return_damaged(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        tk.Label(self.content_frame, text="↩️ Damaged Goods Returns (Coming Soon)", font=("Arial", 18), bg="white").pack(pady=50)

    def show_reports(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        tk.Label(self.content_frame, text="📊 Supplier Performance Reports (Coming Soon)", font=("Arial", 18), bg="white").pack(pady=50)

    def go_back(self):
        from ..main_menu import MainMenu
        MainMenu(self.root, self.user)