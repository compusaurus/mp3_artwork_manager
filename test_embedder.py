import pytest
from core.embedder import embed_artwork_to_mp3

def test_embed_artwork_to_invalid_path():
    fake_bytes = b"This is not real image data"
    result = embed_artwork_to_mp3("nonexistent/path/to/file.mp3", fake_bytes)
    assert result is False
