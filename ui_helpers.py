# utils/ui_helpers.py
import tkinter as tk

def center_window(window: tk.Toplevel, parent: tk.Tk = None):
    """
    Center a window over its parent. If no parent is provided,
    center it on the screen.
    """
    window.update_idletasks()
    if parent is not None:
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (window.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (window.winfo_height() // 2)
    else:
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (window.winfo_width() // 2)
        y = (screen_height // 2) - (window.winfo_height() // 2)
    window.geometry(f"+{x}+{y}")

def update_listbox(listbox: tk.Listbox, items: list):
    """
    Clear and update a Tkinter listbox with new items.
    """
    listbox.delete(0, tk.END)
    for item in items:
        listbox.insert(tk.END, item)

def prompt_artist_title(parent, default_artist, default_title, filename):
    dialog = tk.Toplevel(parent)
    dialog.title("Confirm or Edit Artist and Title")
    dialog.grab_set()

    tk.Label(dialog, text="Original filename:", fg="gray").grid(row=0, column=0, columnspan=2, sticky="w", padx=10)
    tk.Label(dialog, text=filename, font=("Segoe UI", 9, "bold")).grid(row=1, column=0, columnspan=2, sticky="w", padx=10)

    tk.Label(dialog, text="Parsed Artist:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
    artist_entry = tk.Entry(dialog, width=30)
    artist_entry.insert(0, default_artist)
    artist_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(dialog, text="Parsed Title:").grid(row=3, column=0, sticky="e", padx=10)
    title_entry = tk.Entry(dialog, width=30)
    title_entry.insert(0, default_title)
    title_entry.grid(row=3, column=1, padx=10)

    def on_search():
        dialog.result = (artist_entry.get(), title_entry.get())
        dialog.destroy()

    tk.Button(dialog, text="Search", command=on_search).grid(row=4, column=0, columnspan=2, pady=10)

    dialog.wait_window()
    return getattr(dialog, "result", (None, None))

