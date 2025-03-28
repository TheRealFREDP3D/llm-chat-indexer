"""
Logging configuration for LLM Chat Indexer.
"""

import logging
import os


def setup_logger(log_level, log_file, log_format=None):
    """
    Set up and configure the application logger.

    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str): Path to the log file
        log_format (str, optional): Custom log format. Defaults to
                                   "%(asctime)s %(levelname)s %(message)s"

    Returns:
        logging.Logger: Configured logger instance

    Creates log directory if it doesn't exist

    Examples:
        Custom format for production debugging:
        >>> logger = setup_logger(
        ...     "INFO",
        ...     "logs/app.log",
        ...     "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
        ... )

        Format with thread information for concurrent operations:
        >>> logger = setup_logger(
        ...     "DEBUG",
        ...     "logs/app.log",
        ...     "%(asctime)s [%(threadName)s] %(levelname)s - %(message)s"
        ... )
    """
    # Set default log format if not provided
    if log_format is None:
        log_format = "%(asctime)s %(levelname)s %(message)s"

    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # Configure logger
    logger = logging.getLogger("LLMChatIndexer")

    # Clear any existing handlers to prevent duplicate logs
    if logger.handlers:
        logger.handlers.clear()

    # Prevent propagation to root logger
    logger.propagate = False

    # Set log level
    log_level_value = getattr(logging, log_level.upper())
    logger.setLevel(log_level_value)

    # Configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level_value)
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)

    # Configure file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level_value)
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)

    return logger
