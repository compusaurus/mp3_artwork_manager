import pytest
from core.parser import parse_filename

@pytest.mark.parametrize("filename, expected", [
    ("Adele - Hello.mp3", ("Adele", "Hello")),
    ("Radiohead - Creep (Official Video).mp3", ("Radiohead", "Creep")),
    ("The Beatles - Hey Jude (Vinyl Rip).mp3", ("The Beatles", "Hey Jude")),
    ("NoArtistTitle.mp3", ("NoArtistTitle", "")),
])
def test_parse_filename(filename, expected):
    assert parse_filename(filename) == expected
