import logging
import sys

# Define logging format
LOG_FORMAT = "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured standard Python logger.
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    return logger
