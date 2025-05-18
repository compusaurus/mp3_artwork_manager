import json
import os
from pathlib import Path
from constants import CONFIG_FILE, DEFAULT_SPLASH_IMAGE, DEFAULT_SPLASH_DURATION

DEFAULT_CONFIG = {
    "input_dir": str(Path.cwd()),
    "log_dir": str(Path.cwd()),
    "splash_dir": str(Path.cwd()),
    "splash_image": DEFAULT_SPLASH_IMAGE,
    "buttons_position": "bottom",
    "show_splash": True,
    "splash_duration": DEFAULT_SPLASH_DURATION,
    "show_confirmations": True,
    "first_launch": True
}

def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass  # fallback to default

    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG.copy()

def save_config(config: dict) -> None:
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
