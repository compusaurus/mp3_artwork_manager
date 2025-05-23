# gui/artwork_picker.py
import io
import requests
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from PIL import Image, ImageTk
from utils.ui_helpers import center_window
from utils.logger import get_logger
from utils.config_manager import ConfigManager

config = ConfigManager().load()
log_dir = config.get("log_dir", "./logs")
logger = get_logger(log_dir)


def fetch_artwork_urls(artist: str, title: str, limit=50):
    """Return a list of cover-art URLs for this artist/title."""
    q = f"artist:{artist} AND recording:{title}"
    resp = requests.get(
        f"https://musicbrainz.org/ws/2/recording?query={q}&fmt=json&limit={limit}",
        headers={"User-Agent": "MP3ArtV1/1.0"}
    )
    recs = resp.json().get("recordings", [])
    urls = []
    for rec in recs:
        for rel in rec.get("releases", []):
            mbid = rel.get("id")
            # thumbnail endpoint
            urls.append(f"https://coverartarchive.org/release/{mbid}/front-250")
    return urls

def show_artwork_picker(artist: str,
                        title: str,
                        parent: tk.Toplevel,
                        callback):
    logger.info(f"Entered show artwork picker. ")
    # 1) get all candidate URLs
    urls = fetch_artwork_urls(artist, title, limit=100)
    total = len(urls)
    if total == 0:
        messagebox.showinfo("No Artwork",
                            f"No artwork found for {artist} – {title}",
                            parent=parent)
        return
    logger.info(f"User was offered {total} artwork candidate files for download.")
    # 2) ask user how many to download
    num = simpledialog.askinteger(
        "How many images?",
        f"Found {total} candidate images.\n"
        "How many do you want to download?",
        parent=parent,
        minvalue=1,
        maxvalue=total,
        initialvalue=min(10, total)
    )
    if not num:
        return
    urls = urls[:num]
    logger.info(f"User requested {num} artwork candidate files be downloaded.")

    # 3) show a modal progress window
    prog = tk.Toplevel(parent)
    prog.withdraw()
    prog.title("Downloading Artwork")
    prog.transient(parent)
    prog.grab_set()
    logger.info(f"Downloading begun for {num} artwork candidate files.")
    tk.Label(prog, text=f"Downloading 0 of {num}…").pack(padx=20, pady=(15,5))
    bar = ttk.Progressbar(prog, length=300, maximum=num, mode="determinate")
    bar.pack(padx=20, pady=(0,15))
    #prog.update()
    prog.update_idletasks()                          # force size calc
    center_window(prog, parent)                      # center it
    prog.deiconify()                                 # now pop it up    

    # 4) download each image, update the progress bar
    thumbs = []
    for i, url in enumerate(urls, start=1):
        # update label & bar
        logger.info(f"Downloading artwork candidate file #: {i} of {num} be downloaded.")
        prog.children['!label'].config(text=f"Downloading {i} of {num}…")
        bar['value'] = i
        prog.update_idletasks()
        prog.update()

        try:
            data = requests.get(url, timeout=5).content
            pil = Image.open(io.BytesIO(data))
            pil.thumbnail((150,150), Image.LANCZOS)
            tkimg = ImageTk.PhotoImage(pil)
            thumbs.append((url, tkimg))
        except Exception:
            # skip failures silently
            continue

    prog.destroy()

    # 5) now build the selection UI
    popup = tk.Toplevel(parent)
    popup.withdraw()
    popup.title(f"Artwork for {artist} – {title}")
    popup.geometry("500x500")
    popup.transient(parent)
    popup.update_idletasks()
    center_window(popup, parent)
    popup.deiconify()
    popup.lift()
    # how many actually made it into the list?
    count = len(thumbs)
    logger.info(f"Downloaded {count} artwork candidate images for “{artist} – {title}”")

    canvas = tk.Canvas(popup)
    vsb = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    frame = tk.Frame(canvas)
    canvas.create_window((0,0), window=frame, anchor="nw")

    selected = tk.StringVar()

    # wrap into N columns
    COLUMNS = 2
    for idx, (url, img) in enumerate(thumbs):
        row = idx // COLUMNS
        col = idx % COLUMNS
        rb = tk.Radiobutton(frame,
                            image=img,
                            variable=selected,
                            value=url,
                            indicatoron=False,
                            borderwidth=2,
                            relief="ridge")
        rb.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    # Optional: make columns expand evenly
    for c in range(COLUMNS):
        frame.grid_columnconfigure(c, weight=1)

    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    # bottom buttons
    btn_frame = tk.Frame(popup)
    btn_frame.pack(fill="x", pady=10)
    tk.Button(btn_frame, text="Cancel", command=popup.destroy).pack(side="right", padx=5)

    def on_continue():
        url = selected.get()
        if not url:
            messagebox.showwarning("No selection",
                                   "Please pick an artwork.",
                                   parent=popup)
            return
        # fetch full-size version:
        full_data = requests.get(url.replace("-250",""), timeout=5).content
        img = Image.open(io.BytesIO(full_data))
        popup.destroy()
        callback(img)

    tk.Button(btn_frame, text="Continue", command=on_continue).pack(side="right")

    popup.grab_set()
    popup.lift()
    popup.wait_window()