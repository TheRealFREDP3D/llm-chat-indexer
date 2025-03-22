"""
Configuration module for LLM Chat Indexer.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for LLM Chat Indexer."""
    
    BASE_DIR = os.getenv("BASE_DIR", os.getcwd())
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
    SUMMARY_FILENAME = os.getenv("SUMMARY_FILENAME", "chat_summaries.md")
    INDEX_FILENAME = os.getenv("INDEX_FILENAME", "chat_index.json")
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini/gemini-2.0-flash")
    SUPPORTED_FILE_EXTENSIONS = os.getenv(
        "SUPPORTED_FILE_EXTENSIONS",
        ".txt,.md,.json,.html,.csv"
    ).split(",")
    MAX_TOPIC_KEYWORDS = int(os.getenv("MAX_TOPIC_KEYWORDS", 5))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "chat_indexer.log")
