import os
import re
import io
import requests
from PIL import Image, ImageTk
from tkinter import messagebox

from gui.show_parse_dialog import show_parse_dialog
from utils.logger import get_logger
from utils.config_manager import ConfigManager

config = ConfigManager().load()
log_dir = config.get("log_dir", "./logs")
logger = get_logger(log_dir)


def clean_filename(name):
    # Strip file extension
    name = re.sub(r'(?i)\.mp3$', '', name)

    # Remove anything in parentheses
    name = re.sub(r"\([^)]*\)", '', name)

    # Remove bitrate indicators like 320k, 128K
    name = re.sub(r"(?i)\b\d{2,4}\s*[kK]\b", '', name)

    # Remove common tags
    tags_to_remove = [
        "official video", "official audio", "visualizer", "vinyl", "rip"
    ]
    for tag in tags_to_remove:
        pattern = rf"(?i)\b{re.escape(tag)}\b"
        name = re.sub(pattern, '', name)

    return name.strip()


def execute_musicbrainz_query(artist, title, path, preview_window, attach_button, prompted=False, new_art_data=None):
    try:
        logger.info(f"Entered execute_musicbrainz_query with {artist} AND release:{title}. ")
        query = f"https://musicbrainz.org/ws/2/release/?query=artist:{artist} AND release:{title}&fmt=json"
        headers = {'User-Agent': 'MP3ArtworkManager/1.0'}
        response = requests.get(query, headers=headers)

        if response.status_code != 200:
            raise Exception(f"MusicBrainz query failed with status code {response.status_code}")

        data = response.json()
        releases = data.get("releases", [])

        if not releases:
            raise Exception("No matching release found")

        release_id = releases[0]["id"]
        cover_url = f"https://coverartarchive.org/release/{release_id}/front"
        cover_resp = requests.get(cover_url, headers=headers)

        if cover_resp.status_code != 200:
            raise Exception("No cover art found for release")

        img_data = cover_resp.content
        image = Image.open(io.BytesIO(img_data))
        image.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(image)
        preview_window.config(image=photo)
        preview_window.image = photo

        if new_art_data is not None:
            new_art_data["img"] = image
            new_art_data["bytes"] = img_data
            logger.info(f"Received execute_musicbrainz_query with {artist} AND release:{title}. ")

        #if attach_button is not None:
        #    attach_button.config(state="normal")
        # As soon as we have valid art, turn on the Add button:
        if attach_button is not None:
            attach_button.config(state="normal")

    except Exception as e:
        messagebox.showerror("Search Error", f"Search failed: {e}")

#   search_online takes 5 arguments
def search_online(parent, path, preview_window, attach_button, new_art_data=None):
    base = os.path.basename(path).rsplit(".mp3", 1)[0]
    cleaned = clean_filename(base)

    match = re.match(r"(.+?)\s+-\s+(.+)", cleaned)
    if match:
        artist, title = match.groups()
    else:
        parts = cleaned.strip().split()
        artist = " ".join(parts[:len(parts)//2]) if parts else ""
        title = " ".join(parts[len(parts)//2:]) if len(parts) > 1 else ""
    logger.info(f"Entered search_online. ")

    def callback(parsed_artist, parsed_title):
        execute_musicbrainz_query(parsed_artist, parsed_title, path, preview_window, attach_button, prompted=True, new_art_data=new_art_data)

    show_parse_dialog(parent, base, path, artist, title, preview_window, attach_button, new_art_data, callback)


# Dummy stub for now; replace with actual save logic if needed
#def save_image_data_to_mp3(path, image_bytes):
#    messagebox.showinfo("Save Image", f"Artwork would be saved to:\n{path}")
