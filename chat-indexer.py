#!/usr/bin/env python3
"""
LLM Chat Indexer - Main script

Processes chat files to create a searchable index and summary using LLM.
"""

import os
import sys
import glob
import argparse
import logging
from typing import List

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.config import Config
from src.logger import setup_logger
from src.file_parser import parse_file
from src.llm_client import LLMClient
from src.index_builder import build_index, get_timestamp


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="LLM Chat Indexer")
    parser.add_argument(
        "--input-dir", type=str, help="Directory containing chat files to process", default=Config.BASE_DIR
    )
    parser.add_argument("--output-dir", type=str, help="Directory to store output files", default=Config.OUTPUT_DIR)
    parser.add_argument(
        "--supported-extensions",
        type=str,
        help="Comma-separated list of supported file extensions",
        default=",".join(Config.SUPPORTED_FILE_EXTENSIONS),
    )
    parser.add_argument("--llm-provider", type=str, help="LLM provider to use", default=Config.LLM_PROVIDER)
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level",
        default=Config.LOG_LEVEL,
    )
    return parser.parse_args()


def get_chat_files(directory: str, supported_extensions: List[str]) -> List[str]:
    """
    Get all chat files with supported extensions from directory.

    Args:
        directory (str): Directory to search
        supported_extensions (List[str]): List of supported file extensions

    Returns:
        List[str]: List of file paths
    """
    # More efficient approach using os.walk to scan the directory tree once
    files = []
    # Normalize extensions to ensure they start with a dot
    normalized_extensions = []
    for ext in supported_extensions:
        normalized_extensions.append(ext if ext.startswith(".") else f".{ext}")

    # Walk through directory tree once
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            # Check if file has a supported extension
            if any(filename.endswith(ext) for ext in normalized_extensions):
                files.append(os.path.join(root, filename))
    return files


def process_file(file_path: str, llm_client: LLMClient, max_topic_keywords: int) -> dict:
    """
    Process a single chat file.

    Args:
        file_path (str): Path to the file
        llm_client (LLMClient): LLM client instance
        max_topic_keywords (int): Maximum number of topics to extract

    Returns:
        dict: Processed file data
    """
    logger = logging.getLogger("LLMChatIndexer")
    logger.info(f"Processing file: {file_path}")

    # Initialize timestamp before try block to avoid UnboundLocalError in exception handler
    timestamp = get_timestamp(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        messages = parse_file(file_path, content)
        timestamp = get_timestamp(file_path)

        if not messages:
            logger.warning(f"No messages extracted from {file_path}")
            return {
                "filename": os.path.basename(file_path),
                "path": file_path,
                "timestamp": timestamp,
                "topics": [],
                "summary": "No content could be extracted from this file.",
                "message_count": 0,
            }

        # Extract topics
        topics = llm_client.extract_topics(messages, max_topic_keywords)

        # Generate summary
        summary = llm_client.summarize(messages)

        return {
            "filename": os.path.basename(file_path),
            "path": file_path,
            "timestamp": timestamp,
            "topics": topics,
            "summary": summary,
            "message_count": len(messages),
        }

    except Exception as e:
        # Enhanced error logging with full traceback
        logger.exception(f"Error processing file {file_path}")
        return {
            "filename": os.path.basename(file_path),
            "path": file_path,
            "timestamp": timestamp,
            "topics": [],
            "summary": f"Error processing file: {str(e)}. Check logs for details.",
            "message_count": 0,
        }


def main():
    """Main function to run the chat indexer."""
    args = parse_arguments()

    # Set up logger
    logger = setup_logger(args.log_level, Config.LOG_FILE)
    logger.info("Starting LLM Chat Indexer")

    # Process arguments
    input_dir = os.path.abspath(args.input_dir)
    output_dir = os.path.abspath(args.output_dir)
    # Parse supported extensions (expected format: comma-separated list like "txt,md,json")
    supported_extensions = [ext.strip() for ext in args.supported_extensions.split(",") if ext.strip()]

    if not supported_extensions:
        logger.warning("No valid file extensions provided. Using default extensions.")
        supported_extensions = Config.SUPPORTED_FILE_EXTENSIONS

    logger.info(f"Input directory: {input_dir}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Supported extensions: {supported_extensions}")
    logger.info(f"LLM provider: {args.llm_provider}")

    # Ensure API key is set
    if not Config.LLM_API_KEY:
        logger.error("LLM API key not set. Please set LLM_API_KEY environment variable.")
        sys.exit(1)

    # Initialize LLM client
    llm_client = LLMClient(args.llm_provider)

    # Discover files to process
    processed_files = discover_and_process_files(input_dir, supported_extensions, llm_client, logger)
    if not processed_files:
        logger.error("No files were processed successfully. Exiting.")
        sys.exit(1)

    logger.info("Chat indexing completed successfully")


def discover_and_process_files(input_dir, supported_extensions, llm_client, logger):
    """
    Discover and process all chat files in the input directory.

    Args:
        input_dir (str): Directory containing chat files
        supported_extensions (List[str]): List of supported file extensions
        llm_client (LLMClient): LLM client instance
        logger (logging.Logger): Logger instance

    Returns:
        List[dict]: List of processed file data
    """
    # Create output directory if it doesn't exist
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

    # Get all chat files
    chat_files = get_chat_files(input_dir, supported_extensions)

    if not chat_files:
        logger.error(f"No chat files found in {input_dir} with extensions: {supported_extensions}")
        return []

    logger.info(f"Found {len(chat_files)} chat files to process")

    # Process each file
    processed_files = []
    for file_path in chat_files:
        try:
            file_data = process_file(file_path, llm_client, Config.MAX_TOPIC_KEYWORDS)
            processed_files.append(file_data)
        except Exception as e:
            logger.exception(f"Error processing file {file_path}: {str(e)}")

    if not processed_files:
        logger.error("No files were successfully processed")
        return []

    # Build index and save results
    logger.info("Building index and generating summaries")
    index_path = os.path.join(Config.OUTPUT_DIR, Config.INDEX_FILENAME)
    summary_path = os.path.join(Config.OUTPUT_DIR, Config.SUMMARY_FILENAME)

    build_index({"files": processed_files}, Config.OUTPUT_DIR, Config.INDEX_FILENAME, Config.SUMMARY_FILENAME)

    logger.info(f"Successfully processed {len(processed_files)} files")
    logger.info(f"Index saved to {index_path}")
    logger.info(f"Summaries saved to {summary_path}")

    return processed_files


def ensure_directories():
    """Ensure required directories exist."""
    directories = [
        Config.OUTPUT_DIR,
        os.path.dirname(Config.LOG_FILE),
        'logs',
        'output',
        'input'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")


def check_environment():
    """Verify environment setup before running"""
    required_dirs = ['input', 'output', 'logs', 'assets']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            logger.info(f"Created missing directory: {dir_name}")
    
    # Check for .env file
    if not os.path.exists('.env'):
        logger.warning("No .env file found. Copying from template...")
        shutil.copy('.env.template', '.env')
        logger.warning("Please edit .env file with your API key and settings")
        sys.exit(1)

    # Verify API key is set
    if os.getenv('LLM_API_KEY') == 'your_api_key_here':
        logger.error("Please set your LLM API key in .env file")
        sys.exit(1)


if __name__ == "__main__":
    # Import here to avoid circular import issues
    # This is necessary because datetime is used in main() which imports
    # other modules that might also import datetime, causing circular dependencies
    from datetime import datetime

    # Set up logger
    logger = setup_logger(Config.LOG_LEVEL, Config.LOG_FILE)
    logger.info("Starting LLM Chat Indexer")

    # Ensure required directories exist
    ensure_directories()

    check_environment()

    main()
