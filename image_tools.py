# utils/image_tools.py
from PIL import Image, ImageTk
from io import BytesIO
from constants import PREVIEW_SIZE
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

def has_embedded_artwork(file_path):
    """
    Returns True if the MP3 file has embedded artwork, otherwise False.
    """
    try:
        audio = MP3(file_path, ID3=ID3)
        return any(isinstance(tag, APIC) for tag in audio.tags.values())
    except Exception:
        return False

def generate_preview_image(image_data: bytes) -> ImageTk.PhotoImage:
    """
    Generate a resized Tkinter-compatible image preview from raw bytes.
    """
    img = Image.open(BytesIO(image_data))
    img.thumbnail(PREVIEW_SIZE)
    return ImageTk.PhotoImage(img)


def load_image_from_file(path: str) -> bytes:
    """
    Load image bytes from a local file path.
    """
    with open(path, "rb") as f:
        return f.read()