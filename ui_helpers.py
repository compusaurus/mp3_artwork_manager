# utils/ui_helpers.py
import tkinter as tk

def center_window(window: tk.Toplevel, parent: tk.Tk):
    """
    Center a window over its parent.
    """
    window.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (window.winfo_width() // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (window.winfo_height() // 2)
    window.geometry(f"+{x}+{y}")


def update_listbox(listbox: tk.Listbox, items: list):
    """
    Clear and update a Tkinter listbox with new items.
    """
    listbox.delete(0, tk.END)
    for item in items:
        listbox.insert(tk.END, item)