# utils/logger.py
from datetime import datetime
import os
import logging
from logging.handlers import TimedRotatingFileHandler

def get_logger(log_dir: str, name: str = "mp3_art") -> logging.Logger:
    """
    Returns a logger that writes INFO+ messages into
    log_dir/mp3_art_YYYYMMDD.log, one file per day.
    """
    os.makedirs(log_dir, exist_ok=True)

    # build today's filename
    date_str = datetime.now().strftime("%Y%m%d")
    log_filename = f"{name}_{date_str}.log"
    log_path = os.path.join(log_dir, log_filename)

    # simple FileHandler: one file per day, no automatic rotation
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setLevel(logging.INFO)

    # timestamp with milliseconds
    fmt = "%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    handler.setFormatter(logging.Formatter(fmt, datefmt))

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # prevent double‐adding if called multiple times
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == log_path
               for h in logger.handlers):
        logger.addHandler(handler)

    return logger
