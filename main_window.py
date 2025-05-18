import tkinter as tk
from tkinter import ttk
from config import load_config
from constants import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.config = load_config()
        self.root.title(APP_NAME)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.setup_ui()

    def setup_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="MP3 Artwork Manager", font=("Arial", 16)).pack(pady=10)
        ttk.Button(frame, text="Scan Folder", command=self.dummy_action).pack(pady=5)

    def dummy_action(self):
        print("Scan Folder clicked")