import requests
from typing import Optional
from constants import USER_AGENT

def fetch_cover_art(release_id: str) -> Optional[bytes]:
    """
    Fetch cover art image bytes from the Cover Art Archive for a given release ID.
    Returns image data as bytes if successful, None otherwise.
    """
    url = f"https://coverartarchive.org/release/{release_id}/front"
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.content
    except Exception:
        return None