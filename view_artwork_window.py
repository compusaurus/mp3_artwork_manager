import io
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from utils.ui_helpers import center_window
from utils.image_tools import has_embedded_artwork

class ViewArtworkWindow(tk.Toplevel):
    def __init__(self, parent, file_path, config):
        super().__init__(parent)
        self.file_path = file_path
        self.config = config
        self.title("Embedded Artwork")

        self.image_label = tk.Label(self)
        self.image_label.pack(padx=10, pady=10)

        self.copy_btn = tk.Button(self, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_btn.pack(side=tk.LEFT, padx=10, pady=5)

        self.close_btn = tk.Button(self, text="Close", command=self.destroy)
        self.close_btn.pack(side=tk.RIGHT, padx=10, pady=5)

        self.show_artwork()
        center_window(self)

    def show_artwork(self):
        try:
            audio = MP3(self.file_path, ID3=ID3)
            for tag in audio.tags.values():
                if isinstance(tag, APIC):
                    image_data = tag.data
                    image = Image.open(io.BytesIO(image_data))
                    image.thumbnail((400, 400))
                    self.tk_image = ImageTk.PhotoImage(image)
                    self.image_label.config(image=self.tk_image)
                    return
            messagebox.showinfo("No Artwork", "No embedded artwork found in this file.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load artwork: {e}")

    def copy_to_clipboard(self):
        try:
            audio = MP3(self.file_path, ID3=ID3)
            for tag in audio.tags.values():
                if isinstance(tag, APIC):
                    image_data = tag.data
                    image = Image.open(io.BytesIO(image_data))
                    output = io.BytesIO()
                    image.convert("RGB").save(output, "BMP")
                    data = output.getvalue()[14:]
                    output.close()

                    import win32clipboard
                    import win32con

                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(win32con.CF_DIB, data)
                    win32clipboard.CloseClipboard()
                    messagebox.showinfo("Success", "Artwork copied to clipboard.")
                    return
            messagebox.showwarning("No Artwork", "No artwork to copy.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy artwork: {e}")
