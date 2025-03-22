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
    try:
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == ".txt":
            return content.splitlines()
            
        elif ext == ".md":
            try:
                html = markdown(content)
                return [p.get_text() for p in BeautifulSoup(html, "html.parser").find_all("p")]
            except Exception as e:
                logger.error(f"Error parsing markdown file {file_path}: {str(e)}")
                return []
            
        elif ext == ".json":
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    return [entry.get("message", "") for entry in data if "message" in entry]
                elif isinstance(data, dict) and "messages" in data:
                    return [entry.get("content", "") for entry in data["messages"] if "content" in entry]
                logger.warning(f"Unsupported JSON structure in {file_path}")
                return []
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in {file_path}: {str(e)}")
                return []
                
        elif ext == ".html":
            try:
                soup = BeautifulSoup(content, "html.parser")
                return [p.get_text() for p in soup.find_all("p")]
            except Exception as e:
                logger.error(f"Error parsing HTML file {file_path}: {str(e)}")
                return []
            
        elif ext == ".csv":
            try:
                df = pd.read_csv(file_path)
                if "message" in df.columns:
                    return df["message"].dropna().tolist()
                elif "content" in df.columns:
                    return df["content"].dropna().tolist()
                logger.warning(f"No message or content column found in CSV file {file_path}")
                return []
            except Exception as e:
                logger.error(f"Error parsing CSV file {file_path}: {str(e)}")
                return []
                
        else:
            logger.warning(f"Unsupported file extension: {ext} for file {file_path}")
            return []
            
    except Exception as e:
        logger.error(f"Unexpected error processing file {file_path}: {str(e)}")
        return []
