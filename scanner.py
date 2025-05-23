# core/scanner.py
import os
from typing import List
from constants import SUPPORTED_AUDIO_TYPES

def scan_directory_for_mp3s(directory: str) -> List[str]:
    """
    Recursively scan the given directory and return a list of .mp3 file paths.
    """
    mp3_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in SUPPORTED_AUDIO_TYPES):
                mp3_files.append(os.path.join(root, file))
    return mp3_files