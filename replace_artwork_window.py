import io
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageGrab
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
# custom packages
from utils.search_online import search_online
from utils.ui_helpers import center_window
from utils.ui_helpers import prompt_artist_title
from gui.show_parse_dialog import show_parse_dialog
from gui.show_artist_list import show_artist_list
from core.parser import parse_filename


class ReplaceArtworkWindow(tk.Toplevel):
    def __init__(self, *, parent_window, file_path, config, main_window):
        super().__init__(parent_window)
        self.main_window = main_window
        self.file_path = file_path
        self.config = config
        self.title("Replace Artwork")
        self.geometry("700x500")
        self.minsize(700, 500)
        center_window(self, parent_window) 
        self.transient(parent_window)
        self.grab_set()
        self.main_window.logger.info(f"Entered ReplaceArtworkWindow. ")
        self.file_path = file_path
        self.config = config
        self.new_art_data = {"img": None, "bytes": None}
        self.preview_size = (300, 300)

        self.create_widgets()
        self.load_current_artwork()

    def create_widgets(self):
        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

        # Titles
        tk.Label(container, text="Current Artwork").grid(row=0, column=0, sticky="n")
        tk.Label(container, text="New Artwork").grid(row=0, column=1, sticky="n")

        # Image Previews
        self.current_preview = tk.Label(container, relief=tk.SUNKEN)
        self.current_preview.grid(row=1, column=0, padx=10, pady=10)

        self.new_preview = tk.Label(container, relief=tk.SUNKEN)
        self.new_preview.grid(row=1, column=1, padx=10, pady=10)

        # Placeholder image for new artwork
        blank_img = Image.new("RGB", self.preview_size, color="lightgray")
        placeholder = ImageTk.PhotoImage(blank_img)
        self.new_preview.config(image=placeholder)
        self.new_preview.image = placeholder

        # Button Bar
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Paste Artwork", command=self.paste_image, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Select Image", command=self.select_image, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Quick Search", command=self.on_search_online, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Artist List", command=lambda: show_artist_list(self.file_path, self), width=15).pack(side=tk.LEFT, padx=5)

        # Save and Cancel
        self.save_button = tk.Button(self, text="Save", command=self.save_replacement, width=20)
        self.save_button.pack(pady=5)
        self.confirm_button = self.save_button
        tk.Button(self, text="Cancel", command=self.destroy, width=20).pack(pady=5)
        self.main_window.logger.info(f"Entered ReplaceArtworkWindow. ")

    def load_current_artwork(self):
        try:
            audio = MP3(self.file_path, ID3=ID3)
            for tag in audio.tags.values():
                if isinstance(tag, APIC):
                    img = Image.open(io.BytesIO(tag.data)).resize(self.preview_size, Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.current_preview.config(image=photo)
                    self.current_preview.image = photo
                    break
        except Exception as e:
            print(f"Error loading current artwork: {e}")

    def paste_image(self):
        try:
            img = ImageGrab.grabclipboard()
            if img:
                img = img.resize(self.preview_size, Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.new_preview.config(image=photo)
                self.new_preview.image = photo

                output = io.BytesIO()
                img.convert("RGB").save(output, format="JPEG")
                self.new_art_data["img"] = img
                self.new_art_data["bytes"] = output.getvalue()
                self.main_window.logger.info(f"Pasted image from ReplaceArtworkWindow. ")
        except Exception as e:
            messagebox.showerror("Error", f"Paste failed: {e}")

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg;*.jpeg;*.png")])
        if file_path:
            try:
                img = Image.open(file_path).resize(self.preview_size, Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.new_preview.config(image=photo)
                self.new_preview.image = photo

                output = io.BytesIO()
                img.convert("RGB").save(output, format="JPEG")
                self.new_art_data["img"] = img
                self.new_art_data["bytes"] = output.getvalue()
                self.main_window.logger.info(f"Selected new image from ReplaceArtworkWindow. ")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def save_replacement(self):
        if not self.new_art_data["bytes"]:
            messagebox.showwarning("No Image", "Please select or paste an image before saving.")
            return
        try:
            audio = MP3(self.file_path, ID3=ID3)
            if not audio.tags:
                audio.add_tags()
            audio.tags.delall("APIC")
            audio.tags.add(APIC(
                encoding=3, mime="image/jpeg", type=3, desc="Cover", data=self.new_art_data["bytes"]
            ))
            audio.save()
            messagebox.showinfo("Success", "Artwork replaced successfully.")
            self.main_window.logger.info(f"Artwork replaced successfully from ReplaceArtworkWindow. ")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save artwork: {e}")

    def on_search_online(self):
        #search_online(self,self.file_path,self.new_preview,self.confirm_button,self.new_art_data)
        self.main_window.logger.info(f"Selected Search Online from ReplaceArtworkWindow. ")
        search_online(self, self.file_path, self.new_preview, self.save_button, self.new_art_data)
        self.lift()

    def show_artist_list(self):
        # pass the current file and this window into our new module
        self.main_window.logger.info(f"Selected Artist List from ReplaceArtworkWindow. ")
        show_artist_list(self.file_path, self)

    def display_image(self, pil_image):
        if pil_image is None:
            self.new_preview.config(image="")
            self.new_preview.image = None
            return
        try:
            # Work with a copy for display transformations
            image_display = pil_image.copy()

            # Crucial: Convert to RGB for reliable PhotoImage display, especially if source is RGBA or P.
            if image_display.mode not in ("RGB", "L"): # L (grayscale) is also generally fine
                image_display = image_display.convert("RGB")
            
            # Resize the image for preview
            # Use Image.Resampling.LANCZOS for Pillow >= 9.1.0
            # For older versions, use Image.LANCZOS
            try:
                resample_filter = Image.Resampling.LANCZOS
            except AttributeError: # Older Pillow
                resample_filter = Image.LANCZOS
            img_resized = image_display.resize(self.preview_size, resample_filter)
            
            img_tk = ImageTk.PhotoImage(img_resized)
            
            #self.current_preview.config(image=img_tk)
            #self.current_preview.image = img_tk # Keep a reference!
            
            self.new_preview.config(image=img_tk)
            self.new_preview.image = img_tk
            

        except Exception as e:
            messagebox.showerror("Display Error", f"Could not display image: {e}", parent=self)
            self.new_preview.config(image='') # Clear preview on error
            self.new_preview.image = None
