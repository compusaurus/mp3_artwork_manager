# gui/show_artist_list.py
import io
import os
import re
import requests
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from utils.ui_helpers import center_window
from utils.logger import get_logger
from utils.config_manager import ConfigManager

# ← Make sure this import points at the file you put the picker in
from gui.artwork_picker import show_artwork_picker 

config = ConfigManager().load()
log_dir = config.get("log_dir", "./logs")
logger = get_logger(log_dir)

def show_artist_list(mp3_path: str, parent_window: tk.Toplevel):
    """
    Pops up an artist‐lookup dialog based on the MP3 filename.
    """
    logger.info(f"Entered show artist list with {mp3_path}. ")
    # 1) parse default artist from the raw filename
    base = os.path.splitext(os.path.basename(mp3_path))[0]
    # strip parentheses, bitrate tags, etc.
    tmp = re.sub(r"\([^)]*\)", "", base)
    tmp = re.sub(r"(?i)\b\d{2,4}\s*[kK]\b", "", tmp)
    tmp = re.sub(r"(?i)\b(official video|official audio|visualizer|vinyl|rip)\b",
                 "", tmp, flags=re.IGNORECASE).strip()
    # split on the dash (artist – title)
    parts = re.split(r"\s*-\s*", tmp, maxsplit=1)
    default_artist = parts[0].strip()

    # 2) build the popup
    popup = tk.Toplevel(parent_window)
    popup.withdraw()
    popup.title("Artist Lookup")
    popup.geometry("350x450")
    center_window(popup, parent_window)
    popup.update_idletasks()
    popup.deiconify()
    popup.lift()

    # — Search bar —
    search_frame = tk.Frame(popup)
    search_frame.pack(fill="x", padx=10, pady=(10,0))
    tk.Label(search_frame, text="Search Artist:", font=("Arial",10,"bold"))\
      .pack(side="left")
    entry = tk.Entry(search_frame)
    entry.insert(0, default_artist)
    entry.pack(side="left", fill="x", expand=True, padx=(5,0))
    btn_go = tk.Button(search_frame, text="Go")
    btn_go.pack(side="left", padx=5)

    # — Results list —
    lb = tk.Listbox(popup)
    lb.pack(fill="both", expand=True, padx=10, pady=10)

    # — Bottom buttons —
    btn_frame = tk.Frame(popup)
    btn_frame.pack(fill="x", pady=(0,10))
    btn_cancel = tk.Button(btn_frame, text="Cancel",
                           command=popup.destroy, width=10)
    btn_cancel.pack(side="right", padx=5)
    btn_continue = tk.Button(btn_frame, text="Continue",
                             state="disabled", width=10)
    btn_continue.pack(side="right", padx=5)

    popup.update_idletasks()
    popup.deiconify()
    popup.lift()

    # 3) define search action
    def do_search():
        popup.config(cursor="watch")
        popup.update()
        artist = entry.get().strip()
        if not artist:
            messagebox.showwarning("Enter a name",
                                   "Please type an artist to search.",
                                   parent=popup)
            return

        lb.delete(0, tk.END)
        try:
            url = (f"https://musicbrainz.org/ws/2/artist/"
                   f"?query=artist:{artist}&fmt=json")
            resp = requests.get(url, headers={"User-Agent":"MP3ArtV1/1.0"})
            hits = resp.json().get("artists", [])
            popup.config(cursor="")
            if not hits:
                lb.insert(tk.END, f"<no matches for “{artist}”>")
            else:
                for art in hits:
                    lb.insert(tk.END, art.get("name","<unknown>"))
        except Exception as e:
            messagebox.showerror("Error",
                                 f"Could not fetch artist list:\n{e}",
                                 parent=popup)

    btn_go.config(command=do_search)

    # 4) enable Continue only when an item is highlighted
    lb.bind("<<ListboxSelect>>",
            lambda e: btn_continue.config(
                state="normal" if lb.curselection() else "disabled"
            ))

    # 5) on Continue, invoke your track‐list dialog
    def on_continue():
        idx = lb.curselection()
        if not idx:
            return
        chosen_artist = lb.get(idx[0])
        popup.destroy()
        # now call your track picker
        logger.info(f"Calling show_track_list with {chosen_artist}. ")
        show_track_list(mp3_path, chosen_artist, parent_window)

    btn_continue.config(command=on_continue)

    # initial search
    do_search()

    # block until closed
    popup.grab_set()
    popup.wait_window()


def show_track_list(mp3_path: str, artist_name: str, parent_window: tk.Toplevel):
    """
    1) parses default title from mp3_path
    2) shows a Search Title / Go bar
    3) shows Cancel / Continue buttons
    4) on Continue, opens the artwork‐picker
    """
    # parse default title
    base = os.path.splitext(os.path.basename(mp3_path))[0]
    parts = base.split(" - ", 1)
    default_title = parts[1] if len(parts) == 2 else ""
    logger.info(f"Entered show_track_list with {artist_name} and release title {default_title}. ")

    popup = tk.Toplevel(parent_window)
    popup.withdraw()
    popup.title(f"Tracks by {artist_name}")
    popup.geometry("400x550")
    center_window(popup, parent_window)
    popup.update_idletasks()
    popup.deiconify()
    popup.lift()

    # ── Title Search Bar ───────────────────────────
    topfrm = tk.Frame(popup)
    topfrm.pack(fill="x", padx=10, pady=(10, 0))
    tk.Label(topfrm, text="Search Title:", font=("Arial", 10, "bold")).pack(side="left")
    entry_title = tk.Entry(topfrm)
    entry_title.insert(0, default_title)
    entry_title.pack(side="left", fill="x", expand=True, padx=(5,0))
    btn_go = tk.Button(topfrm, text="Go")
    btn_go.pack(side="left", padx=5)

    # ── Listbox ────────────────────────────────────
    lb = tk.Listbox(popup)
    lb.pack(fill="both", expand=True, padx=10, pady=10)

    # ── Cancel / Continue ───────────────────────────
    btn_frame = tk.Frame(popup)
    btn_frame.pack(fill="x", pady=10)
    btn_cancel   = tk.Button(btn_frame, text="Cancel",   width=10, command=popup.destroy)
    btn_cancel.pack(side="right", padx=5)
    btn_continue = tk.Button(btn_frame, text="Continue", width=10, state="disabled")
    btn_continue.pack(side="right", padx=5)

    popup.update_idletasks()
    popup.deiconify()
    popup.lift()

    # ── Helper to load tracks ──────────────────────
    def do_search_tracks():
        popup.config(cursor="watch")
        popup.update()
        q = entry_title.get().strip()
        lb.delete(0, tk.END)
        try:
            url = (
                "https://musicbrainz.org/ws/2/recording"
                f"?query=artist:{artist_name}%20AND%20recording:{q}&fmt=json&limit=50"
            )
            resp = requests.get(url, headers={"User-Agent": "MP3ArtV1/1.0"})
            recs = resp.json().get("recordings", [])
            popup.config(cursor="")
            if not recs:
                lb.insert(tk.END, f"<no matches for “{q}”>")
            else:
                for rec in recs:
                    lb.insert(tk.END, rec["title"])
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch tracks:\n{e}", parent=popup)
    
    popup.lift()
    btn_go.config(command=do_search_tracks)
    popup.lift()

    # ── Enable Continue on selection ───────────────
    lb.bind("<<ListboxSelect>>",
            lambda e: btn_continue.config(state="normal" if lb.curselection() else "disabled"))

    # ── The magic: on Continue, call artwork picker ─
    def on_continue():
        sel = lb.curselection()
        if not sel:
            return
        track = lb.get(sel[0])
        popup.destroy()

        def receive_art(pil_image):
            # 1) Keep the PIL.Image for display & later save
            parent_window.new_artwork = pil_image
            parent_window.new_art_data["img"] = pil_image

            # 2) Also serialize to JPEG bytes now, so save_artwork()
            buf = io.BytesIO()
            pil_image.convert("RGB").save(buf, format="JPEG")
            parent_window.new_art_data["bytes"] = buf.getvalue()

            # 3) Show it in the preview pane…
            parent_window.display_image(pil_image)
            # 4) …and enable the “Add to MP3 File” button
            parent_window.confirm_button.config(state="normal")

        show_artwork_picker(
            artist=artist_name,
            title=track,
            parent=parent_window,
            callback=receive_art
        )

    btn_continue.config(command=on_continue)

    # ── Kick off first search ──────────────────────
    do_search_tracks()
    popup.grab_set()
    popup.wait_window()
