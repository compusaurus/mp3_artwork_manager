# main.py
import tkinter as tk
from gui.main_window import MainWindow
from logger import setup_logger

def main():
    logger = setup_logger()
    logger.info("Starting MP3 Artwork Manager")

    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()