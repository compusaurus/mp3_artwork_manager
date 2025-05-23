import pytest
import tkinter as tk
from utils.image_tools import generate_preview_image
from PIL import Image
from io import BytesIO

def test_generate_preview_image_valid_jpeg():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    img = Image.new("RGB", (500, 500), color="red")
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    image_data = buffer.getvalue()

    preview = generate_preview_image(image_data)
    assert preview.width() <= 300
    assert preview.height() <= 300

    root.destroy()
