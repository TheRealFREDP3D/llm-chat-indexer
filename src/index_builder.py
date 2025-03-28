"""
Index builder module for creating searchable indexes and summaries.
"""

import os
import json
import logging
import traceback
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
        logger.info("Formatting timestamps for index entries")
        for file_entry in index_data["files"]:
            timestamp = file_entry.get("timestamp", "")
            if timestamp:
                # Parse ISO format and format as more readable
                try:
                    dt = datetime.fromisoformat(timestamp)
                    file_entry["formatted_date"] = dt.strftime("%Y-%m-%d %H:%M:%S")
                    logger.debug(f"Formatted timestamp for {file_entry.get('filename', 'unknown file')}")
                except (ValueError, TypeError):
                    logger.warning(
                        f"Invalid timestamp format: {timestamp} for file {file_entry.get('filename', 'unknown file')}"
                    )
                    file_entry["formatted_date"] = timestamp
            else:
                logger.debug(f"No timestamp found for {file_entry.get('filename', 'unknown file')}")

        # Write JSON index
        index_path = os.path.join(output_dir, index_filename)
        logger.info(f"Writing JSON index to {index_path}")
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2)
        logger.info(f"Successfully wrote JSON index with {len(index_data['files'])} file entries")

        # Write Markdown summary
        summary_path = os.path.join(output_dir, summary_filename)
        logger.info(f"Generating markdown summary to {summary_path}")
        with open(summary_path, "w", encoding="utf-8") as f:
            # Write header with generation timestamp
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"# Chat Summaries\n\n")
            f.write(f"*Generated on: {current_time}*\n\n")
            f.write(f"This document contains summaries of {len(index_data['files'])} chat files.\n\n")

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
                message_count = entry.get("message_count", 0)
                participants = entry.get("participants", [])

                f.write(f"## {filename}\n\n")

                # File metadata section
                f.write("### Metadata\n\n")
                if timestamp:
                    f.write(f"**Date:** {timestamp}\n\n")
                if message_count:
                    f.write(f"**Messages:** {message_count}\n\n")
                if participants:
                    f.write(f"**Participants:** {', '.join(participants)}\n\n")
                if topics:
                    f.write(f"**Topics:** {', '.join(topics)}\n\n")

                # Summary section
                f.write("### Summary\n\n")
                f.write(f"{summary}\n\n")

                # Key points section if available
                key_points = entry.get("key_points", [])
                if key_points:
                    f.write("### Key Points\n\n")
                    for point in key_points:
                        f.write(f"- {point}\n")
                    f.write("\n")

                f.write("---\n\n")

        logger.info(f"Successfully wrote markdown summary with {len(index_data['files'])} file entries")
        return True

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error building index: {str(e)}")
        logger.debug(f"Detailed error: {error_details}")

        # Create a minimal error report if possible
        try:
            error_report_path = os.path.join(output_dir, "index_error_report.txt")
            with open(error_report_path, "w", encoding="utf-8") as f:
                f.write(f"Error occurred at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Error message: {str(e)}\n\n")
                f.write("Detailed error information:\n")
                f.write(error_details)
            logger.info(f"Error report written to {error_report_path}")
        except Exception as report_error:
            logger.error(f"Failed to write error report: {str(report_error)}")

        return False


def get_timestamp(file_path):
    """
    Get ISO formatted timestamp from file's modification time.

    Args:
        file_path (str): Path to the file

    Returns:
        str: ISO formatted timestamp
    """
    if not file_path:
        logger.warning("Empty file path provided for timestamp retrieval")
        return ""

    if not os.path.exists(file_path):
        logger.warning(f"Cannot get timestamp for non-existent file: {file_path}")
        return ""

    try:
        timestamp = datetime.fromtimestamp(os.path.getmtime(file_path))
        iso_timestamp = timestamp.isoformat()
        logger.debug(f"Retrieved timestamp {iso_timestamp} for {file_path}")
        return iso_timestamp
    except OSError as e:
        logger.error(f"Error getting timestamp for {file_path}: {str(e)}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error getting timestamp for {file_path}: {str(e)}")
        return ""
