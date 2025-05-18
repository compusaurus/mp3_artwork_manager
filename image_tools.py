from PIL import Image, ImageTk
from io import BytesIO
from constants import PREVIEW_SIZE

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