"""Logging
"""
import logging


def create_file_logger(
    logger_name: str,
    log_dir: str
) -> logging.Logger:
    """Create a file logger (log to a file)

    Args:

    Returns:
        Logger
    """
    logger = logging.getLogger(logger_name)
    log_handler = logging.FileHandler(log_dir)
    logger.addHandler(log_handler)

    return logger
