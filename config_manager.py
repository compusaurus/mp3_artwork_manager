# utils/config_manager.py

import json
import pathlib

DEFAULT_CONFIG = {
    "input_dir": str(pathlib.Path.cwd()),
    "log_dir": str(pathlib.Path.cwd() / "logs"),
    "splash_dir": str(pathlib.Path.cwd()),
    "splash_image": "compusaurusrex.jpg",
    "buttons_position": "bottom",
    "show_splash": True,
    "splash_duration": 2000,
    "show_confirmations": True,
    "first_launch": True
}

CONFIG_FILE = "config.json"

class ConfigManager:
    def __init__(self):
        self.config_path = pathlib.Path(CONFIG_FILE)
        self.config = DEFAULT_CONFIG.copy()

    def load(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    self.config.update(json.load(f))
            except Exception:
                pass
        return self.config

    def save(self, config):
        try:
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Failed to save config: {e}")
