# gui/setup_window.py
import tkinter as tk
from tkinter import filedialog, ttk
from config import load_config, save_config
from utils.ui_helpers import center_window
from pathlib import Path

class SetupWindow:
    def __init__(self, master, config):
        self.config = config
        self.top = tk.Toplevel(master)
        self.top.title("Preferences")
        self.top.geometry("600x300")
        center_window(self.top, master)
        self.top.lift()
        self.top.focus_force()

        self.config = load_config()

        # Directories frame
        frame = ttk.Frame(self.top, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        self.entries = {}

        row = 0
        for label, key in [
            ("MP3 Input Directory:", "input_dir"),
            ("Log Directory:", "log_dir"),
            ("Splash Directory:", "splash_dir")
        ]:
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w")
            entry = ttk.Entry(frame, width=60)
            entry.insert(0, self.config.get(key, ""))
            entry.grid(row=row, column=1, sticky="ew")
            self.entries[key] = entry
            ttk.Button(frame, text="Browse", command=lambda k=key: self.browse_dir(k)).grid(row=row, column=2)
            row += 1

        # Splash Image File Picker
        ttk.Label(frame, text="Splash Image File:").grid(row=row, column=0, sticky="w")
        self.splash_entry = ttk.Entry(frame, width=60)
        self.splash_entry.insert(0, self.config.get("splash_image", ""))
        self.splash_entry.grid(row=row, column=1, sticky="ew")
        ttk.Button(frame, text="Browse", command=self.browse_splash_file).grid(row=row, column=2)
        row += 1

        # Buttons Position Dropdown
        ttk.Label(frame, text="Buttons Position:").grid(row=row, column=0, sticky="w")
        self.position_var = tk.StringVar(value=self.config.get("buttons_position", "top"))
        ttk.Combobox(frame, textvariable=self.position_var, values=["top", "bottom", "left", "right"], width=20).grid(row=row, column=1, sticky="w")
        row += 1

        # Splash screen options
        self.splash_var = tk.BooleanVar(value=self.config.get("show_splash", True))
        ttk.Checkbutton(frame, text="Show splash screen on startup", variable=self.splash_var).grid(row=row, column=0, columnspan=2, sticky="w")
        row += 1

        ttk.Label(frame, text="Splash Duration (ms):").grid(row=row, column=0, sticky="w")
        self.duration_entry = ttk.Entry(frame, width=10)
        self.duration_entry.insert(0, str(self.config.get("splash_duration", 2000)))
        self.duration_entry.grid(row=row, column=1, sticky="w")
        row += 1

        self.confirm_var = tk.BooleanVar(value=self.config.get("show_confirmations", True))
        ttk.Checkbutton(frame, text="Show confirmation prompts", variable=self.confirm_var).grid(row=row, column=0, columnspan=2, sticky="w")
        row += 1

        # Save/Cancel
        ttk.Button(frame, text="Save", command=self.save).grid(row=row, column=0, pady=10)
        ttk.Button(frame, text="Cancel", command=self.top.destroy).grid(row=row, column=1, pady=10, sticky="w")

    def browse_dir(self, key):
        initial = self.entries[key].get()
        path = filedialog.askdirectory(initialdir=initial if Path(initial).exists() else ".")
        if path:
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, str(Path(path).resolve()))
        self.top.lift()
        self.top.focus_force()

    def browse_splash_file(self):
        splash_dir = Path(self.entries["splash_dir"].get()).resolve()
        filetypes = [("JPEG files", "*.jpg;*.jpeg"), ("PNG files", "*.png"), ("All files", "*.*")]
        filename = filedialog.askopenfilename(
            title="Select Splash Image",
            initialdir=str(splash_dir) if splash_dir.exists() else ".",
            filetypes=filetypes
        )
        if filename:
            selected_path = Path(filename).resolve()
            try:
                selected_path.relative_to(splash_dir)  # Enforce selection within splash_dir
                self.splash_entry.delete(0, tk.END)
                self.splash_entry.insert(0, selected_path.name)
            except ValueError:
                tk.messagebox.showwarning(
                    "Invalid Selection",
                    f"The selected file must be inside:{splash_dir}"
                )
        self.top.lift()
        self.top.focus_force()

    def save(self):
        self.config["input_dir"] = str(Path(self.entries["input_dir"].get()).resolve())
        self.config["log_dir"] = str(Path(self.entries["log_dir"].get()).resolve())
        self.config["splash_dir"] = str(Path(self.entries["splash_dir"].get()).resolve())
        self.config["splash_image"] = self.splash_entry.get()
        self.config["buttons_position"] = self.position_var.get()
        self.config["show_splash"] = self.splash_var.get()
        self.config["splash_duration"] = int(self.duration_entry.get())
        self.config["show_confirmations"] = self.confirm_var.get()
        save_config(self.config)
        self.top.destroy()
