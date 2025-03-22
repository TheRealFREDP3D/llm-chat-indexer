"""
Tests for the logger module.
"""

import os
import tempfile
import logging
import pytest
from src.logger import setup_logger


def test_setup_logger():
    """Test logger setup."""
    # Use a temp file for testing
    with tempfile.NamedTemporaryFile(delete=False) as f:
        log_file = f.name

    try:
        # Set up logger
        logger = setup_logger("DEBUG", log_file)

        # Assertions
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 2  # Console and file handler

        # Test logging
        test_message = "Test log message"
        logger.info(test_message)

        # Check if message appears in log file
        with open(log_file, "r") as f:
            log_content = f.read()
            assert test_message in log_content
    finally:
        # Clean up
        os.unlink(log_file)


def test_setup_logger_invalid_level():
    """Test logger setup with invalid level."""
    # Should default to INFO if invalid level
    logger = setup_logger("INVALID", os.devnull)
    assert logger.level == logging.INFO


def test_setup_logger_creates_directory():
    """Test logger creates directory if it doesn't exist."""
    # Create a temp directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = os.path.join(tmpdir, "logs")
        log_file = os.path.join(log_dir, "test.log")

        # Set up logger
        setup_logger("INFO", log_file)

        # Assert directory was created
        assert os.path.exists(log_dir)
