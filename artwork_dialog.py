# gui/artwork_dialog.py
import tkinter as tk
from tkinter import Toplevel, Label, Button

class ArtworkDialog:
    def __init__(self, master, image_data=None):
        self.top = Toplevel(master)
        self.top.title("Artwork Preview")
        self.image_data = image_data
        Label(self.top, text="Artwork preview goes here").pack(padx=10, pady=10)
        Button(self.top, text="Close", command=self.top.destroy).pack(pady=5)
