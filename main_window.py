import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from pathlib import Path
from config import load_config, save_config
from constants import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, PREVIEW_SIZE
from core.scanner import scan_directory_for_mp3s
from utils.config_manager import ConfigManager
from utils.logger import get_logger
from utils.ui_helpers import center_window
from utils.image_tools import has_embedded_artwork
from gui.replace_artwork_window import ReplaceArtworkWindow
from gui.find_artwork_window import FindArtworkWindow
from gui.setup_window import SetupWindow
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
import threading

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Artwork Manager")
        self.config = ConfigManager().load()
        self.config = self.resolve_paths(load_config())
        #self.logger = get_logger(self.config.get("log_dir"))
        self.logger  = logger
        self.logger.info(f"UI initialized, watching folder {config['input_dir']}")
        self.file_data = []  # (filepath, has_art)
        self.sort_ascending = True

        self.setup_ui()
        center_window(self.root)

    def resolve_paths(self, config):
        for key in ("input_dir", "log_dir", "splash_dir"):
            if key in config:
                config[key] = str(Path(config[key]).resolve())
        return config

    def setup_ui(self):
        # Toolbar Frame
        toolbar = tk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=10, pady=(5, 0))

        tk.Label(toolbar, text="Search:").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(toolbar, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=2)

        tk.Button(toolbar, text="X", command=self.clear_search).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Go", command=self.execute_search).pack(side=tk.LEFT, padx=(0, 10))

        self.filter_var = tk.StringVar(value="Show all")
        filter_options = ["Show all", "Show with Art Embedded", "Show without Art Embedded"]
        self.filter_menu = ttk.OptionMenu(toolbar, self.filter_var, self.filter_var.get(), *filter_options, command=self.apply_filter)
        self.filter_menu.pack(side=tk.RIGHT, padx=(0, 10))

        self.sort_button = tk.Button(toolbar, text="Sort Asc", command=self.toggle_sort)
        self.sort_button.pack(side=tk.RIGHT)

        # Title
        tk.Label(self.root, text="MP3 Artwork Manager", font=("Helvetica", 14, "bold")).pack(pady=5)
        
        self.create_menu()
        
        # Treeview for file list
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("Filename", "Artwork")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.tree.heading("Filename", text="Filename")
        self.tree.heading("Artwork", text="Artwork")
        self.tree.column("Filename", anchor="w", width=600)
        self.tree.column("Artwork", anchor="center", width=100)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Bottom Button Bar
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Scan Folder", command=self.scan_folder).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Remove Selected", command=self.remove_selected).pack(side="left", padx=2)
        self.view_button = tk.Button(btn_frame, text="View Artwork", command=self.view_artwork)
        self.view_button.pack(side="left", padx=2)
        self.replace_button = tk.Button(btn_frame, text="Replace Artwork", command=self.find_or_replace_artwork)
        self.replace_button.pack(side="left", padx=2)
        #tk.Button(btn_frame, text="Find Missing Artwork", command=self.find_missing_artwork).pack(side="left", padx=2)

        tk.Button(btn_frame, text="Close", command=self.root.destroy).pack(side="left", padx=2)

        # Selection binding for label update
        self.tree.bind("<<TreeviewSelect>>", self.update_replace_button_label)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Setup", command=self.open_setup)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

    def open_setup(self):
        SetupWindow(self.root, self.config)

    def scan_folder(self):
        def run_scan():
            from mutagen.mp3 import MP3
            from mutagen.id3 import ID3, APIC

            input_dir = str(Path(self.config.get("input_dir", ".")).resolve())
            mp3_files = scan_directory_for_mp3s(input_dir)

            #self.file_data = []
            #self.tree.delete(*self.tree.get_children())

            # clear old data
            self.file_data = []
            self.tree.delete(*self.tree.get_children())

            progress_window = tk.Toplevel(self.root)
            progress_window.title("Scanning...")
            progress_window.resizable(False, False)
            progress_window.transient(self.root)
            progress_window.grab_set()
            progress_window.geometry("600x140")
            progress_window.minsize(600, 100)

            label_status = ttk.Label(progress_window, text="Scanning files...", anchor="center")
            label_status.pack(padx=20, pady=(10, 5))

            label_file = ttk.Label(progress_window, text="", anchor="center")
            label_file.pack(padx=20, pady=(0, 5))

            progress = ttk.Progressbar(progress_window, mode="determinate", length=500)
            progress.pack(padx=20, pady=(0, 10))
            progress["maximum"] = len(mp3_files)

            #def update_ui(idx, display_name, has_art):
            def update_ui(idx, file_path, display_name, has_art):
                art_status = "✔"  if has_art else "✖"
                #self.tree.insert("", "end", values=(display_name, art_status)) #use the full path as the item ID
                #self.tree.insert("", "end", iid=file,   # full filesystem path
                #                 values=(display_name, art_status))                
                #self.file_data.append((os.path.join(input_dir, display_name), has_art))
                # now that file_path is a parameter, we insert it reliably
                self.tree.insert("", "end",
                                 iid=file_path,
                                 values=(display_name, art_status))
                # keep your parallel list in sync
                self.file_data.append((file_path, has_art))
                self.master_data = list(self.file_data)
                label_file.config(text=display_name)
                progress["value"] = idx + 1
                progress_window.update_idletasks()

            for idx, file in enumerate(mp3_files):
                has_art = False
                display_name = os.path.basename(file)

                try:
                    audio = MP3(file, ID3=ID3)
                    has_art = any(isinstance(tag, APIC) for tag in audio.tags.values())
                except Exception:
                    pass

                #self.root.after(0, update_ui, idx, display_name, has_art)
                # pass file into update_ui so it has the right IID
                self.root.after(0, update_ui, idx, file, display_name, has_art)
            self.root.after(0, progress_window.destroy)

        # Run scanning in a thread
        threading.Thread(target=run_scan, daemon=True).start()
    
    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        # reset the filter dropdown to its default
        self.filter_var.set("Show all")
        # repopulate the tree from master_data
        self.file_data = list(self.master_data)
        self.tree.delete(*self.tree.get_children())
        for path, has_art in self.file_data:
            status = "✔" if has_art else "✖"
            self.tree.insert("", "end",
                             iid=path,
                             values=(os.path.basename(path), status))

    def execute_search(self):
        import os

        q = self.search_entry.get().strip().lower()
        if not q:
            return

        # 1) filter the master list, not tree or old file_data
        filtered = [
            (path, has_art)
            for path, has_art in self.master_data
            if q in os.path.basename(path).lower()
            ]

        # 2) update both the tree _and_ self.file_data
        self.tree.delete(*self.tree.get_children())
        for path, has_art in filtered:
            name   = os.path.basename(path)
            status = "✔" if has_art else "✖"
            self.tree.insert("", "end", iid=path, values=(name, status))

        self.file_data = filtered
        # make sure the dropdown reads “Show all” now that we’ve done a text search
        self.filter_var.set("Show all")

    def toggle_sort(self):
        self.sort_ascending = not self.sort_ascending
        self.sort_button.config(text="Sort Asc" if self.sort_ascending else "Sort Desc")

        sorted_data = sorted(self.file_data, key=lambda x: os.path.basename(x[0]).lower(), reverse=not self.sort_ascending)
        self.tree.delete(*self.tree.get_children())
        for file, has_art in sorted_data:
            status = "✔" if has_art else "✖"
            self.tree.insert("", "end", values=(os.path.basename(file), status))

    def apply_filter(self, selection):
         # build a fresh filtered list off the full master_data
         filtered = [
             (path, flag)
             for path, flag in self.master_data
             if   selection == "Show all"
             or  (selection == "Show with Art Embedded"   and flag)
             or  (selection == "Show without Art Embedded" and not flag)
         ]
 
         # update our working list and redraw the tree
         self.file_data = filtered
         self.tree.delete(*self.tree.get_children())
         for path, flag in filtered:
             status = "✔" if flag else "✖"
             self.tree.insert("", "end",
                              iid=path,
                              values=(os.path.basename(path), status))

    def reset_filter(self):
        self.apply_filter("Show all")

    def remove_selected(self):
        for selected in self.tree.selection():
            self.tree.delete(selected)

    def view_artwork(self):
        selected = self.tree.selection()
        if not selected:
            return

        #index = self.tree.index(selected[0])
        #file_path, has_art = self.file_data[index]
        # the Treeview item's IID is the full path:
        file_path = selected[0]
        has_art   = self.tree.set(file_path, "Artwork") == "✔"

        if not has_art:
            messagebox.showwarning("No Artwork", "This file has no embedded artwork.")
            return

        from gui.view_artwork_window import ViewArtworkWindow
        ViewArtworkWindow(self.root, file_path, self.config)

    def find_or_replace_artwork(self):
        selected = self.tree.selection()
        if not selected:
            return

        # index = self.tree.index(selected[0])
        # file_path, has_art = self.file_data[index]
        # the Treeview item's IID is the full path:
        file_path = selected[0]
        has_art   = self.tree.set(file_path, "Artwork") == "✔"        

        if has_art:
            ReplaceArtworkWindow(
                parent_window=self.root,   # real Tk widget
                file_path   = file_path,
                config      = self.config,
                main_window = self        # so the dialog can callback
            )
        else:
            FindArtworkWindow(
                parent_window=self.root,
                file_path   = file_path,
                config      = self.config,
                main_window = self
            )

    def update_replace_button_label(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        #index = self.tree.index(selected[0])
        #file_path, has_art = self.file_data[index]
        # the Treeview item's IID is the full path:
        file_path = selected[0]
        has_art   = self.tree.set(file_path, "Artwork") == "✔"        
        new_label = "Replace Artwork" if has_art else "Find Artwork"
        self.replace_button.config(text=new_label)

    def find_missing_artwork(self):
        self.tree.delete(*self.tree.get_children())
        for file, has_art in self.file_data:
            if not has_art:
                filename = os.path.basename(file)
                self.tree.insert("", "end", values=(filename, "✖"))

def refresh_item_artwork(self, mp3_path):
    """
    Find the Treeview/Listbox row for mp3_path and update its artwork column.
    """
    for iid in self.tree.get_children():
        vals = self.tree.item(iid, "values")
        if vals and vals[0] == mp3_path:
            # assume you have a checkmark PhotoImage called self.icon_check
            self.tree.set(iid, "Artwork", "")  # clear the text
            self.tree.item(iid, image=self.icon_check)
            break