"""
File parsing module for LLM Chat Indexer.
Handles various file formats to extract chat messages.
"""

import os
import json
import logging
import pandas as pd
from bs4 import BeautifulSoup
from markdown import markdown

logger = logging.getLogger("LLMChatIndexer")


def parse_file(file_path, content):
    """
    Parse file content based on its extension to extract chat messages.

    Args:
        file_path (str): Path to the file
        content (str): File content as string

    Returns:
        list: Extracted messages from the file
    """
    def parse_txt(content):
        return content.splitlines()

    def parse_md(content):
        try:
            html = markdown(content, extensions=["extra"])
            soup = BeautifulSoup(html, "html.parser")
            messages = []

            for p in soup.find_all("p"):
                if p.get_text().strip():
                    messages.append(p.get_text().strip())

            for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
                level = int(heading.name[1])
                messages.append(f"{'#' * level} {heading.get_text().strip()}")

            for list_elem in soup.find_all(["ul", "ol"]):
                for item in list_elem.find_all("li"):
                    messages.append(f"- {item.get_text().strip()}")

            for quote in soup.find_all("blockquote"):
                messages.append(f"> {quote.get_text().strip()}")

            if not messages:
                logger.warning(f"No content extracted from markdown file {file_path}")

            return messages
        except ImportError as e:
            logger.error(f"Missing dependencies for markdown parsing: {str(e)}")
            return []

    def parse_json(content):
        try:
            data = json.loads(content)
            if isinstance(data, list):
                return [entry.get("message", "") for entry in data if "message" in entry]
            elif isinstance(data, dict) and "messages" in data:
                return [entry.get("content", "") for entry in data["messages"] if "content" in entry]
            logger.warning(f"Unsupported JSON structure in {file_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {str(e)}")
        return []

    def parse_html(content):
        try:
            soup = BeautifulSoup(content, "html.parser")
            return [p.get_text() for p in soup.find_all("p")]
        except Exception as e:
            logger.error(f"Error parsing HTML file {file_path}: {str(e)}")
            return []

    def parse_csv(file_path):
        try:
            df = pd.read_csv(file_path)
            if "message" in df.columns:
                return df["message"].dropna().tolist()
            elif "content" in df.columns:
                return df["content"].dropna().tolist()
            logger.warning(f"No message or content column found in CSV file {file_path}")
        except Exception as e:
            logger.error(f"Error parsing CSV file {file_path}: {str(e)}")
        return []

    handlers = {
        ".txt": parse_txt,
        ".md": parse_md,
        ".json": parse_json,
        ".html": parse_html,
        ".csv": lambda _: parse_csv(file_path),
    }

    try:
        ext = os.path.splitext(file_path)[1].lower()
        handler = handlers.get(ext)
        if handler:
            return handler(content)
        else:
            logger.warning(f"Unsupported file extension: {ext} for file {file_path}")
            logger.info(f"Supported extensions are: {', '.join(handlers.keys())}")
            return []
    except Exception as e:
        logger.error(f"Unexpected error processing file {file_path}: {str(e)}")
        return []
