import io
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageGrab # Make sure ImageGrab is imported from PIL
from PIL import Image # Redundant if specific classes imported, but fine.
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
# custom packages
from utils.ui_helpers import center_window
# from utils.ui_helpers import prompt_artist_title # Not used
# from utils.image_tools import has_embedded_artwork # Not used
#from utils.search_online import execute_musicbrainz_query # Not used
from utils.search_online import search_online
from gui.show_artist_list import show_artist_list
from gui.show_parse_dialog import show_parse_dialog # Not used
# from core.parser import parse_filename # Not used


class FindArtworkWindow(tk.Toplevel):
    def __init__(self, *, parent_window, file_path, config, main_window):
        super().__init__(parent_window)
        self.main_window = main_window
        self.file_path    = file_path
        self.config       = config
        center_window(self, parent_window)
        # ── derive default artist/title from the filename ────────────
        import re
        base = os.path.splitext(os.path.basename(file_path))[0]
        # strip out parentheticals, bitrate tags, noise words, etc.
        tmp = re.sub(r"\([^)]*\)", "", base)
        tmp = re.sub(r"(?i)\b\d{2,4}\s*[kK]\b", "", tmp)
        tmp = re.sub(r"(?i)\b(official video|official audio|visualizer|vinyl|rip)\b",
                     "", tmp, flags=re.IGNORECASE).strip()
        # split on the first dash into artist / title
        parts = re.split(r"\s*-\s*", tmp, maxsplit=1)
        self.parsed_artist = parts[0].strip()
        self.parsed_title  = parts[1].strip() if len(parts) > 1 else ""
        # ─────────────────────────────────────────────────────────────
        self.config = config
        self.new_artwork = None # This will store the PIL.Image object

        self.title("Find and Add Artwork")
        self.geometry("700x500")
        self.minsize(700, 500)
        self.resizable(False, False)
        self.new_art_data = {"img": None, "bytes": None} # Used by search_online
        self.preview_size = (300, 300)
        self.build_ui()
        center_window(self, parent_window)
        self.main_window.logger.info(f"Entered FindArtworkWindow. ")

    def build_ui(self):
        preview_frame = tk.LabelFrame(self, text="New Artwork")
        preview_frame.pack(padx=10, pady=(10, 5), fill="both", expand=True)
        
        # Removed width/height in text units. Label will size to the image.
        self.preview_label = tk.Label(preview_frame, bg="gray")
        #self.preview_label.pack(pady=10) # Centers the label (and thus image)
        self.preview_label.pack(padx=10, pady=10, fill="both", expand=True)
        self.current_preview = self.preview_label

        button_frame = tk.Frame(self)
        button_frame.pack(pady=(0, 10))

        tk.Button(button_frame, text="Paste Artwork", command=self.paste_artwork).pack(side="left", padx=5)
        tk.Button(button_frame, text="Select Image", command=self.select_image).pack(side="left", padx=5)
        tk.Button(button_frame, text="Quick Search", command=self.on_search_online).pack(side="left", padx=5)
        tk.Button(button_frame, text="Artist List", command=lambda: show_artist_list(self.file_path, self)).pack(side="left", padx=5)
        self.add_button = tk.Button(self, text="Add to MP3 File", command=self.save_artwork, state="disabled")
        self.add_button.pack(pady=(0, 5))
        self.confirm_button = self.add_button
        #tk.Button(button_frame,text="Edit Artist/Title",command=self.on_edit_artist_title).pack(side="left", padx=5)
        tk.Button(self, text="Cancel", command=self.destroy).pack()

    def display_image(self, pil_image):
        if pil_image is None:
            self.current_preview.config(image='')
            self.current_preview.image = None
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
            
            self.current_preview.config(image=img_tk)
            self.current_preview.image = img_tk # Keep a reference!
        except Exception as e:
            messagebox.showerror("Display Error", f"Could not display image: {e}", parent=self)
            self.current_preview.config(image='') # Clear preview on error
            self.current_preview.image = None

    def paste_artwork(self):
        # IMPORTANT: For reliable clipboard image pasting on Windows,
        # ensure 'pywin32' is installed in your Python environment: pip install pywin32
        # Pillow uses it for a more robust clipboard access method.
        try:
            img_from_clipboard = ImageGrab.grabclipboard()
            
            if img_from_clipboard:
                # For debugging, you can print info or save the raw pasted image:
                # print(f"Pasted image - Size: {img_from_clipboard.size}, Mode: {img_from_clipboard.mode}")
                # img_from_clipboard.save("debug_pasted_image.png")

                self.new_artwork = img_from_clipboard # Store the original PIL image for saving
                
                # Update new_art_data if other parts of your application rely on it
                self.new_art_data["img"] = self.new_artwork
                # Generating bytes can be deferred to save_artwork or done here
                # output = io.BytesIO()
                # self.new_artwork.convert("RGB").save(output, format="JPEG") # Ensure RGB for JPEG
                # self.new_art_data["bytes"] = output.getvalue()
                self.main_window.logger.info(f"Pasted image from FindArtworkWindow. ")
                self.display_image(self.new_artwork)
                self.add_button.config(state="normal")
            else:
                messagebox.showwarning("Paste Failed", "No image found in clipboard.", parent=self)
        except Exception as e:
            messagebox.showerror("Paste Failed", f"Could not paste image from clipboard.\n{e}", parent=self)
        finally:
            self.lift() # Ensure window stays on top after messagebox

    def select_image(self):
        file_path = filedialog.askopenfilename(
            parent=self,
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
        )
        if file_path:
            try:
                image = Image.open(file_path)
                self.new_artwork = image # Store the original PIL image
                # self.new_art_data["img"] = image # If needed for other logic
                self.main_window.logger.info(f"Selected image from FindArtworkWindow. ")
                self.display_image(self.new_artwork)
                self.add_button.config(state="normal")
            except Exception as e: # Catch more specific errors like FileNotFoundError, IOError if needed
                messagebox.showerror("Invalid File", f"Failed to load selected image.\n{e}", parent=self)
        self.lift()

    def on_search_online(self):
        #search_online(self, self.file_path, self.preview_label, self.add_button, self.new_art_data)
        # signature is (parent, path, preview_label, enable_button, art_data)
        self.main_window.logger.info(f"Selected Quick Search from FindArtworkWindow. ")
        search_online(
            self,
            self.file_path,
            self.preview_label,
            self.add_button,
            self.new_art_data
        )
        # ── pick up the downloaded image and enable Add ──────────
        img = self.new_art_data.get("img")
        if img:
            self.new_artwork = img
            # re-draw just in case
            self.display_image(self.new_artwork)
            self.add_button.config(state="normal")
        # ─────────────────────────────────────────────────────────
        self.lift()

    def show_artist_list(self):
        # pass the current file and this window into our new module
        self.main_window.logger.info(f"Selected Artist List from FindArtworkWindow. ")
        show_artist_list(self.file_path, self)

    def save_artwork(self):
        if not self.new_artwork:
            messagebox.showwarning("No Artwork", "Please select, paste, or find artwork first.", parent=self)
            return

        try:
            audio = MP3(self.file_path, ID3=ID3)
            if audio.tags is None: # Ensure ID3 tag container exists
                audio.tags = ID3()
            
            # Remove any existing cover art to avoid multiple APIC frames
            # This deletes all APIC frames. If you need more specific removal, adjust.
            audio.tags.delall("APIC")
            # For newer mutagen versions, this might be audio.tags.popall("APIC")

            artwork_bytes = self.image_to_bytes(self.new_artwork)
            audio.tags.add(
                APIC(
                    encoding=0,        # 0 for Latin-1, 3 for UTF-8 (for description/filename)
                    mime='image/jpeg', # Mime type for JPEG
                    type=3,            # 3 means 'Cover (front)'
                    desc=u'Cover',     # Description
                    data=artwork_bytes
                )
            )
            audio.save()
            self.main_window.logger.info(f"Artwork saved successfully from FindArtworkWindow. ")
            messagebox.showinfo("Success", "Artwork added successfully.", parent=self)
            # Tell the main window to refresh that row's icon:
            if hasattr(self.main_window, "refresh_item_artwork"):
                self.main_windo.refresh_item_artwork(self.file_path)
            else:
                # fallback: do a full re-scan
                if hasattr(self.main_window, "scan_folder"):
                    self.main_window.scan_folder()
            audio.save()
            messagebox.showinfo("Success", "Artwork added successfully.", parent=self)

            # tell the main window to update that row’s icon to “✔”
            try:
                # if you used iid=file_path on insert
                self.main_window.tree.set(self.file_path, "Artwork", "✔")
            except Exception:
                # fallback, in case you didn’t use iid=path:
                for iid in self.main_window.tree.get_children():
                    if self.main_window.tree.item(iid, "values")[0] == os.path.basename(self.file_path):
                        self.main_window.tree.set(iid, "Artwork", "✔")
                        break
                for idx,(path,has_art) in enumerate(self.main_window.file_data):
                    if path == self.file_path:
                        self.main_window.file_data[idx] = (path, True)
                        break
            self.destroy()

            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add artwork: {e}", parent=self)
            self.lift()

    def image_to_bytes(self, pil_image):
        with io.BytesIO() as img_bytes_io:
            image_to_save = pil_image
            # JPEG does not support alpha channels, convert to RGB if necessary
            if image_to_save.mode in ('RGBA', 'LA', 'P'): # P (paletted) might have transparency
                image_to_save = image_to_save.convert('RGB')
            
            # You can make quality configurable, e.g., self.config.get("jpeg_quality", 85)
            image_to_save.save(img_bytes_io, format="JPEG", quality=85) 
            return img_bytes_io.getvalue()

    def on_edit_artist_title(self):
        """
        Pops up the “Confirm or Edit Artist/Title” box,
        then updates self.parsed_artist/self.parsed_title
        """
        show_parse_dialog(
            parent_window         = self,
            base           = os.path.basename(self.file_path),
            path           = self.file_path,
            artist         = self.parsed_artist,
            title          = self.parsed_title,
            preview        = self.preview_label,
            attach_button  = self.add_button,
            new_art_data   = self.new_art_data,
            callback       = self._apply_parsed
        )

    def _apply_parsed(self, artist, title):
        """
        Called by show_parse_dialog when the user clicks “Search”.
        """
        self.parsed_artist = artist
        self.parsed_title  = title
