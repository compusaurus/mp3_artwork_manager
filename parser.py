import re
from typing import Tuple

def parse_filename(filename: str) -> Tuple[str, str]:
    """
    Attempt to extract artist and title from a filename.
    """
    name = re.sub(r'(?i)\.mp3$', '', filename)
    name = re.sub(r"\([^)]*\)", '', name)  # Remove parentheses
    name = re.sub(r"(?i)\b\d{2,4}\s*[kK]\b", '', name)
    name = re.sub(r"(?i)\b(official video|official audio|visualizer|vinyl|rip)\b", '', name)
    name = re.sub(r"[-_]+", ' ', name).strip()

    match = re.match(r"(.+?)\s+-\s+(.+)", name)
    if match:
        return match.group(1).strip(), match.group(2).strip()

    parts = name.strip().split()
    mid = len(parts) // 2
    return " ".join(parts[:mid]), " ".join(parts[mid:])
