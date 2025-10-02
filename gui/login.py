# gui/login.py
import tkinter as tk
from tkinter import messagebox
from database import get_db_connection
from utils import clear_window

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.check_auto_login()

    def setup_ui(self):
        clear_window(self.root)
        self.root.title("🔐 Crown Supermarket - Login")
        self.root.geometry("800x500")
        self.root.configure(bg="white")

        # === LEFT PANEL (Dark Blue Branding) ===
        left_frame = tk.Frame(self.root, bg="#0d1b2a", width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        left_frame.pack_propagate(False)

        tk.Label(left_frame, text="CROWN", font=("Arial", 36, "bold"), fg="gold", bg="#0d1b2a").pack(pady=(80, 10))
        tk.Label(left_frame, text="SUPERMARKET", font=("Arial", 24, "bold"), fg="white", bg="#0d1b2a").pack(pady=(0, 20))
        tk.Label(left_frame, text="POS SYSTEM", font=("Arial", 16), fg="#90e0ef", bg="#0d1b2a").pack()
        tk.Label(left_frame, text="© 2025 Crown Retail Solutions", font=("Arial", 10), fg="#90e0ef", bg="#0d1b2a").pack(side=tk.BOTTOM, pady=20)

        # === RIGHT PANEL (Login Form) ===
        right_frame = tk.Frame(self.root, bg="white", width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=40, pady=60)
        right_frame.pack_propagate(False)

        tk.Label(right_frame, text="Login to Continue", font=("Arial", 20, "bold"), bg="white", fg="#0d1b2a").pack(pady=(0, 30))

        # Username
        tk.Label(right_frame, text="👤 Username", font=("Arial", 12), bg="white", anchor="w").pack(fill=tk.X)
        self.username_entry = tk.Entry(right_frame, font=("Arial", 14), width=30, relief=tk.FLAT, highlightbackground="#ccc", highlightthickness=1)
        self.username_entry.pack(pady=(5, 20), ipady=5)
        self.username_entry.focus()

        # Password
        tk.Label(right_frame, text="🔐 Password", font=("Arial", 12), bg="white", anchor="w").pack(fill=tk.X)
        self.password_entry = tk.Entry(right_frame, font=("Arial", 14), width=30, show="*", relief=tk.FLAT, highlightbackground="#ccc", highlightthickness=1)
        self.password_entry.pack(pady=(5, 20), ipady=5)
        self.password_entry.bind("<Return>", lambda e: self.login())

        # Login Button
        login_btn = tk.Button(
            right_frame,
            text="LOGIN",
            font=("Arial", 14, "bold"),
            bg="#0d1b2a",
            fg="white",
            width=20,
            height=2,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.login
        )
        login_btn.pack(pady=20)

        # Footer
        tk.Label(right_frame, text="Contact IT for account issues", font=("Arial", 9), bg="white", fg="#666").pack(side=tk.BOTTOM, pady=(40, 0))

    def check_auto_login(self):
        """Check for auto_login.py and auto-login if exists"""
        try:
            from auto_login import AUTO_LOGIN
            print(f"🔑 Auto-login enabled for user: {AUTO_LOGIN.get('username', 'unknown')}")
            # Auto-login after 1.5 seconds (shows login screen briefly)
            self.root.after(1500, lambda: self.perform_auto_login(
                AUTO_LOGIN.get('username', ''),
                AUTO_LOGIN.get('password', '')
            ))
        except ImportError:
            # auto_login.py doesn't exist - proceed normally
            pass
        except Exception as e:
            print(f"⚠️ Auto-login error: {e}")
            pass

    def perform_auto_login(self, username, password):
        """Perform the actual auto-login"""
        if username and password:
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, username)
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, password)
            self.login()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Missing Info", "Please enter both username and password.")
            return

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, username, role, full_name FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            user_data = {
                'id': user[0],
                'username': user[1],
                'role': user[2],
                'full_name': user[3]
            }

            # Redirect based on role
            if user_data['role'] == 'cashier':
                from .pos import POSWindow
                POSWindow(self.root, user_data)
            else:
                from .main_menu import MainMenu
                MainMenu(self.root, user_data)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")