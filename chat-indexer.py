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
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config import Config
from src.logger import setup_logger
from src.file_parser import parse_file
from src.llm_client import LLMClient
from src.index_builder import build_index, get_timestamp

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="LLM Chat Indexer")
    parser.add_argument(
        "--input-dir",
        type=str,
        help="Directory containing chat files to process",
        default=Config.BASE_DIR
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Directory to store output files",
        default=Config.OUTPUT_DIR
    )
    parser.add_argument(
        "--supported-extensions",
        type=str,
        help="Comma-separated list of supported file extensions",
        default=",".join(Config.SUPPORTED_FILE_EXTENSIONS)
    )
    parser.add_argument(
        "--llm-provider",
        type=str,
        help="LLM provider to use",
        default=Config.LLM_PROVIDER
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level",
        default=Config.LOG_LEVEL
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
    files = []
    for ext in supported_extensions:
        if not ext.startswith('.'):
            ext = f".{ext}"
        pattern = os.path.join(directory, f"**/*{ext}")
        files.extend(glob.glob(pattern, recursive=True))
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
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        messages = parse_file(file_path, content)
        
        if not messages:
            logger.warning(f"No messages extracted from {file_path}")
            return {
                "filename": os.path.basename(file_path),
                "path": file_path,
                "timestamp": get_timestamp(file_path),
                "topics": [],
                "summary": "No content could be extracted from this file.",
                "message_count": 0
            }
            
        # Extract topics
        topics = llm_client.extract_topics(messages, max_topic_keywords)
        
        # Generate summary
        summary = llm_client.summarize(messages)
        
        return {
            "filename": os.path.basename(file_path),
            "path": file_path,
            "timestamp": get_timestamp(file_path),
            "topics": topics,
            "summary": summary,
            "message_count": len(messages)
        }
        
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        return {
            "filename": os.path.basename(file_path),
            "path": file_path,
            "timestamp": get_timestamp(file_path),
            "topics": [],
            "summary": f"Error processing file: {str(e)}",
            "message_count": 0
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
    supported_extensions = [ext.strip() for ext in args.supported_extensions.split(",")]
    
    logger.info(f"Input directory: {input_dir}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Supported extensions: {supported_extensions}")
    logger.info(f"LLM provider: {args.llm_provider}")
    
    # Initialize LLM client
    llm_client = LLMClient(args.llm_provider)
    
    # Get chat files
    chat_files = get_chat_files(input_dir, supported_extensions)
    logger.info(f"Found {len(chat_files)} chat files to process")
    
    if not chat_files:
        logger.warning(f"No chat files found in {input_dir} with extensions {supported_extensions}")
        return
    
    # Process files
    processed_files = []
    for file_path in chat_files:
        file_data = process_file(file_path, llm_client, Config.MAX_TOPIC_KEYWORDS)
        processed_files.append(file_data)
    
    # Build index
    index_data = {
        "files": processed_files,
        "metadata": {
            "total_files": len(processed_files),
            "generated_at": datetime.now().isoformat(),
            "llm_provider": args.llm_provider
        }
    }
    
    success = build_index(
        index_data,
        output_dir,
        Config.INDEX_FILENAME,
        Config.SUMMARY_FILENAME
    )
    
    if success:
        logger.info("Chat indexing completed successfully!")
        logger.info(f"JSON index: {os.path.join(output_dir, Config.INDEX_FILENAME)}")
        logger.info(f"Markdown summary: {os.path.join(output_dir, Config.SUMMARY_FILENAME)}")
    else:
        logger.error("Failed to build index")
        sys.exit(1)

if __name__ == "__main__":
    # Import here to avoid circular import issues
    from datetime import datetime
    main()
