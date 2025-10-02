# gui/held_invoices.py
import tkinter as tk
from utils import clear_window

class HeldInvoicesWindow:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        clear_window(self.root)
        self.root.title("📌 Held Invoices")

        tk.Label(self.root, text="📌 Held Invoices (Coming Soon)", font=("Arial", 18, "bold")).pack(pady=50)
        tk.Button(self.root, text="Back to Menu", command=self.go_back).pack(pady=20)

    def go_back(self):
        from .main_menu import MainMenu
        MainMenu(self.root, self.user)