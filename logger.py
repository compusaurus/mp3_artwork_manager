import logging

def setup_logger(name: str = "mp3art") -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("mp3art.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(name)