"""
Tests for the config module.
"""

import os
import pytest
from unittest.mock import patch
from src.config import Config


def test_default_config():
    """Test default configuration values."""
    # Assert default values
    assert Config.BASE_DIR is not None
    assert Config.OUTPUT_DIR is not None
    assert Config.SUMMARY_FILENAME == "chat_summaries.md"
    assert Config.INDEX_FILENAME == "chat_index.json"
    assert Config.LLM_PROVIDER == "gemini/gemini-2.0-flash"
    assert isinstance(Config.SUPPORTED_FILE_EXTENSIONS, list)
    assert len(Config.SUPPORTED_FILE_EXTENSIONS) > 0
    assert Config.MAX_TOPIC_KEYWORDS == 5
    assert Config.LOG_LEVEL == "INFO"
    assert Config.LOG_FILE == "chat_indexer.log"


@patch.dict(
    os.environ,
    {
        "BASE_DIR": "/custom/base/dir",
        "OUTPUT_DIR": "/custom/output/dir",
        "SUMMARY_FILENAME": "custom_summary.md",
        "INDEX_FILENAME": "custom_index.json",
        "LLM_PROVIDER": "custom-provider",
        "SUPPORTED_FILE_EXTENSIONS": ".custom1,.custom2",
        "MAX_TOPIC_KEYWORDS": "10",
        "LOG_LEVEL": "DEBUG",
        "LOG_FILE": "custom.log",
    },
)
def test_config_from_env_vars():
    """Test loading configuration from environment variables."""
    # Import again to reload with patched environment
    import importlib
    from src import config

    importlib.reload(config)

    # Assert values from environment
    assert config.Config.BASE_DIR == "/custom/base/dir"
    assert config.Config.OUTPUT_DIR == "/custom/output/dir"
    assert config.Config.SUMMARY_FILENAME == "custom_summary.md"
    assert config.Config.INDEX_FILENAME == "custom_index.json"
    assert config.Config.LLM_PROVIDER == "custom-provider"
    assert config.Config.SUPPORTED_FILE_EXTENSIONS == [".custom1", ".custom2"]
    assert config.Config.MAX_TOPIC_KEYWORDS == 10
    assert config.Config.LOG_LEVEL == "DEBUG"
    assert config.Config.LOG_FILE == "custom.log"


def test_config_supported_extensions_parsing():
    """Test parsing of supported file extensions."""
    # Import directly from config
    from src.config import Config

    # Check that extensions start with dot
    for ext in Config.SUPPORTED_FILE_EXTENSIONS:
        assert ext.startswith(".")
