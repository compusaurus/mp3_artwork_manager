# gui/setup_window.py
import tkinter as tk
from tkinter import Toplevel, Label, Button
from config import load_config, save_config

class SetupWindow:
    def __init__(self, master):
        self.top = Toplevel(master)
        self.top.title("Setup")
        self.config = load_config()

        Label(self.top, text="Configuration screen coming soon.").pack(padx=10, pady=10)
        Button(self.top, text="Save", command=self.save).pack(side=tk.LEFT, padx=5, pady=5)
        Button(self.top, text="Cancel", command=self.top.destroy).pack(side=tk.LEFT, padx=5, pady=5)

    def save(self):
        save_config(self.config)
        self.top.destroy()