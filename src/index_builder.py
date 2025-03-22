"""
Index builder module for creating searchable indexes and summaries.
"""

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger("LLMChatIndexer")


def build_index(index_data, output_dir, index_filename, summary_filename):
    """
    Build JSON index and markdown summary files.

    Args:
        index_data (dict): Processed data with files and topics
        output_dir (str): Directory to store output files
        index_filename (str): Filename for JSON index
        summary_filename (str): Filename for markdown summary

    Returns:
        bool: True if successful, False otherwise
    """
    # Validate inputs
    if not isinstance(index_data, dict) or "files" not in index_data:
        logger.error("Invalid index_data format: expected dict with 'files' key")
        return False

    if not output_dir:
        logger.error("No output directory specified")
        return False

    if not index_filename or not summary_filename:
        logger.error("Missing filename for index or summary")
        return False

    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Format timestamps for better readability in the index
        for file_entry in index_data["files"]:
            timestamp = file_entry.get("timestamp", "")
            if timestamp:
                # Parse ISO format and format as more readable
                try:
                    dt = datetime.fromisoformat(timestamp)
                    file_entry["formatted_date"] = dt.strftime("%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    logger.warning(f"Invalid timestamp format: {timestamp}")
                    file_entry["formatted_date"] = timestamp

        # Write JSON index
        index_path = os.path.join(output_dir, index_filename)
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2)
        logger.info(f"JSON index written to {index_path}")

        # Write Markdown summary
        summary_path = os.path.join(output_dir, summary_filename)
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("# Chat Summaries\n\n")

            # Add table of contents
            f.write("## Table of Contents\n\n")
            for i, entry in enumerate(index_data["files"]):
                filename = entry.get("filename", f"File {i + 1}")
                anchor = filename.lower().replace(".", "-").replace(" ", "-")
                f.write(f"- [{filename}](#{anchor})\n")
            f.write("\n")

            # Add summaries
            for entry in index_data["files"]:
                filename = entry.get("filename", "")
                summary = entry.get("summary", "No summary available")
                topics = entry.get("topics", [])
                timestamp = entry.get("formatted_date", entry.get("timestamp", ""))

                f.write(f"## {filename}\n\n")
                if timestamp:
                    f.write(f"**Date:** {timestamp}\n\n")
                if topics:
                    f.write(f"**Topics:** {', '.join(topics)}\n\n")
                f.write(f"{summary}\n\n")
                f.write("---\n\n")

        logger.info(f"Markdown summary written to {summary_path}")
        return True

    except Exception as e:
        logger.error(f"Error building index: {str(e)}")
        return False


def get_timestamp(file_path):
    """
    Get ISO formatted timestamp from file's modification time.

    Args:
        file_path (str): Path to the file

    Returns:
        str: ISO formatted timestamp
    """
    if not file_path or not os.path.exists(file_path):
        logger.warning(f"Cannot get timestamp for non-existent file: {file_path}")
        return ""

    try:
        return datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
    except OSError as e:
        logger.error(f"Error getting timestamp for {file_path}: {str(e)}")
        return ""
