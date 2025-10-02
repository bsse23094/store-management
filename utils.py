# utils.py
import tkinter as tk
from tkinter import messagebox

def clear_window(root):
    for widget in root.winfo_children():
        widget.destroy()

def show_error(title, message):
    messagebox.showerror(title, message)

def show_info(title, message):
    messagebox.showinfo(title, message)

def show_warning(title, message):
    messagebox.showwarning(title, message)

def ask_yes_no(title, message):
    return messagebox.askyesno(title, message)