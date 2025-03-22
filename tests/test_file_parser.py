"""
Tests for the file_parser module.
"""

import os
import tempfile
import pytest
from src.file_parser import parse_file


def test_parse_txt_file(sample_chat_content):
    """Test parsing a text file."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write(sample_chat_content.encode("utf-8"))
        filename = f.name

    try:
        # Test the parser
        messages = parse_file(filename, sample_chat_content)

        # Assertions
        assert len(messages) > 0
        assert "User: Hello, how are you?" in messages
        assert "Assistant: I'm doing well" in [m.strip() for m in messages]
    finally:
        # Clean up
        os.unlink(filename)


def test_parse_json_file(sample_json_content):
    """Test parsing a JSON file."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        f.write(sample_json_content.encode("utf-8"))
        filename = f.name

    try:
        # Test the parser
        messages = parse_file(filename, sample_json_content)

        # Assertions
        assert len(messages) == 5
        assert "Hello, how are you?" in messages
        assert "I'm doing well, thank you!" in messages
    finally:
        # Clean up
        os.unlink(filename)


def test_parse_markdown_file():
    """Test parsing a markdown file."""
    content = """
    # Chat Conversation
    
    **User**: Hello, how are you?
    
    **Assistant**: I'm doing well, thank you! How can I help you today?
    
    **User**: I'm looking for information about machine learning.
    """

    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        f.write(content.encode("utf-8"))
        filename = f.name

    try:
        # Test the parser
        messages = parse_file(filename, content)

        # Assertions
        assert len(messages) > 0
        # Markdown parsing often strips formatting, so we check for content
        assert any("Hello" in msg for msg in messages)
    finally:
        # Clean up
        os.unlink(filename)


def test_parse_csv_file():
    """Test parsing a CSV file."""
    content = "message\nHello, how are you?\nI'm doing well, thank you!\n"

    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        f.write(content.encode("utf-8"))
        filename = f.name

    try:
        # Test the parser (note: we don't pass content, as the CSV parser reads directly)
        messages = parse_file(filename, content)

        # Assertions
        assert len(messages) == 2
        assert "Hello, how are you?" in messages
        assert "I'm doing well, thank you!" in messages
    finally:
        # Clean up
        os.unlink(filename)


def test_parse_unsupported_file():
    """Test parsing an unsupported file type."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
        f.write(b"Some content")
        filename = f.name

    try:
        # Test the parser
        messages = parse_file(filename, "Some content")

        # Assertions
        assert messages == []
    finally:
        # Clean up
        os.unlink(filename)


def test_parse_invalid_json():
    """Test parsing invalid JSON."""
    invalid_json = '{"messages": [broken json]}'

    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        f.write(invalid_json.encode("utf-8"))
        filename = f.name

    try:
        # Test the parser
        messages = parse_file(filename, invalid_json)

        # Assertions
        assert messages == []
    finally:
        # Clean up
        os.unlink(filename)


def test_parse_empty_file():
    """Test parsing an empty file."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        filename = f.name

    try:
        # Test the parser
        messages = parse_file(filename, "")

        # Assertions
        assert messages == []
    finally:
        # Clean up
        os.unlink(filename)
