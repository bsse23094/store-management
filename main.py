# main.py
import tkinter as tk
from database import init_db
from gui.login import LoginWindow

if __name__ == "__main__":
    # Initialize database (creates tables + sample data)
    init_db()

    # Create main window
    root = tk.Tk()
    root.title("🏪 Enterprise POS System")
    root.geometry("1200x700")

    # Launch login screen
    LoginWindow(root)

    # Start the app
    root.mainloop()