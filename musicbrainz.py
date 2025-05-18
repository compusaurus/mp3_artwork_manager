import requests
from typing import List, Dict
from constants import USER_AGENT

def search_release(artist: str, title: str) -> List[Dict]:
    """
    Search MusicBrainz for releases by artist and title.
    Returns a list of release dictionaries.
    """
    query = f"https://musicbrainz.org/ws/2/release/?query=artist:{artist} AND release:{title}&fmt=json"
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(query, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("releases", [])
    except Exception:
        return []