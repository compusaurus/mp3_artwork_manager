from logger import setup_logger

def test_logger_creates_instance():
    logger = setup_logger("test_logger")
    assert logger.name == "test_logger"
    assert logger.hasHandlers()
