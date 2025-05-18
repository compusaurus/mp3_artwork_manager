from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from constants import APIC_ENCODING, APIC_MIME, APIC_TYPE, APIC_DESC

def embed_artwork_to_mp3(path: str, image_bytes: bytes) -> bool:
    """
    Embed image data into an MP3 file.
    Returns True if successful, False otherwise.
    """
    try:
        audio = MP3(path, ID3=ID3)
        if not audio.tags:
            audio.add_tags()
        audio.tags.delall("APIC")
        audio.tags.add(
            APIC(
                encoding=APIC_ENCODING,
                mime=APIC_MIME,
                type=APIC_TYPE,
                desc=APIC_DESC,
                data=image_bytes
            )
        )
        audio.save()
        return True
    except Exception as e:
        return False