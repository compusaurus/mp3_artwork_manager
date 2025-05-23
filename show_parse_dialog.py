import tkinter as tk
from tkinter import Toplevel, Label, Entry, Button, StringVar

from utils.ui_helpers import center_window

def show_parse_dialog(parent, base, path, artist, title, preview, attach_button, new_art_data, callback):
    dialog = Toplevel(parent)
    dialog.title("Confirm or Edit Artist and Title")
    dialog.transient(parent)
    dialog.grab_set()
    center_window(dialog, parent)

    Label(dialog, text="Original filename:").pack(anchor='w', padx=10, pady=(10, 0))
    Label(dialog, text=base, foreground="gray").pack(anchor='w', padx=10)

    Label(dialog, text="Parsed Artist:").pack(anchor='w', padx=10, pady=(10, 0))
    artist_var = StringVar(value=artist)
    Entry(dialog, textvariable=artist_var, width=50).pack(padx=10)

    Label(dialog, text="Parsed Title:").pack(anchor='w', padx=10, pady=(10, 0))
    title_var = StringVar(value=title)
    Entry(dialog, textvariable=title_var, width=50).pack(padx=10)

    def confirm():
        dialog.destroy()
        parsed_artist = artist_var.get().strip()
        parsed_title = title_var.get().strip()
        callback(parsed_artist, parsed_title)

    Button(dialog, text="Search", command=confirm).pack(pady=10)
    
    dialog.wait_window()       # <— pause here until the user clicks “Search” and the callback runs