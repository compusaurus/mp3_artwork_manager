# main.py
import sys
import os
print("Running from:", os.path.abspath(__file__))
import gui.main_window

print("Loaded main_window from:", gui.main_window.__file__)

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import tkinter as tk
from gui.main_window import MainWindow
from utils.logger import get_logger
from utils.config_manager import ConfigManager
def main():
    #config = load_config()
    config = ConfigManager().load()
    log_dir = config.get("log_dir", "./logs")
    logger = get_logger(log_dir)
    logger.info("Starting MP3 Artwork Manager")

    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()