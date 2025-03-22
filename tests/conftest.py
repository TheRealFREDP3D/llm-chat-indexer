"""
Test configuration and fixtures for LLM Chat Indexer tests.
"""

import os
import tempfile
import pytest
from unittest.mock import MagicMock

from src.config import Config
from src.llm_client import LLMClient
from src.logger import setup_logger


@pytest.fixture
def sample_chat_content():
    """Sample chat content for testing."""
    return """
    User: Hello, how are you?
    Assistant: I'm doing well, thank you! How can I help you today?
    User: I'm looking for information about machine learning.
    Assistant: Of course! Machine learning is a branch of artificial intelligence...
    User: Thanks! That's helpful.
    """


@pytest.fixture
def sample_json_content():
    """Sample JSON chat content for testing."""
    return """
    {
        "messages": [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you! How can I help you today?"},
            {"role": "user", "content": "I'm looking for information about machine learning."},
            {"role": "assistant", "content": "Of course! Machine learning is a branch of artificial intelligence..."},
            {"role": "user", "content": "Thanks! That's helpful."}
        ]
    }
    """


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        old_base_dir = Config.BASE_DIR
        old_output_dir = Config.OUTPUT_DIR

        # Override config temporarily
        Config.BASE_DIR = tmpdirname
        Config.OUTPUT_DIR = os.path.join(tmpdirname, "output")

        yield tmpdirname

        # Restore original config
        Config.BASE_DIR = old_base_dir
        Config.OUTPUT_DIR = old_output_dir


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client for testing."""
    mock_client = MagicMock(spec=LLMClient)

    # Configure the mock to return predictable values
    mock_client.extract_topics.return_value = ["machine learning", "artificial intelligence", "chatbot"]
    mock_client.summarize.return_value = "A conversation about machine learning and artificial intelligence."

    return mock_client


@pytest.fixture
def test_logger():
    """Set up a test logger."""
    return setup_logger("DEBUG", os.devnull)  # Log to nowhere
