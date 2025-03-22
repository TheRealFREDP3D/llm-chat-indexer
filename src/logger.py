"""
Logging configuration for LLM Chat Indexer.
"""

import logging
import os

def setup_logger(log_level, log_file):
    """
    Set up and configure the application logger.
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str): Path to the log file
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
        
    # Configure logger
    logger = logging.getLogger("LLMChatIndexer")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    )
    logger.addHandler(console_handler)
    
    # Configure file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    )
    logger.addHandler(file_handler)
    
    return logger
