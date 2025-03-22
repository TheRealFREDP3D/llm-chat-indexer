"""
Tests for the index_builder module.
"""

import os
import json
import tempfile
import pytest
from datetime import datetime
from src.index_builder import build_index, get_timestamp


def test_build_index(temp_directory):
    """Test building index and summary files."""
    # Test data
    index_data = {
        "files": [
            {
                "filename": "test1.txt",
                "path": "/path/to/test1.txt",
                "timestamp": "2023-06-15T12:00:00",
                "topics": ["topic1", "topic2"],
                "summary": "This is a summary of test1.",
                "message_count": 10,
            },
            {
                "filename": "test2.txt",
                "path": "/path/to/test2.txt",
                "timestamp": "2023-06-16T14:30:00",
                "topics": ["topic3", "topic4"],
                "summary": "This is a summary of test2.",
                "message_count": 15,
            },
        ]
    }

    output_dir = os.path.join(temp_directory, "output")
    index_filename = "test_index.json"
    summary_filename = "test_summary.md"

    # Call the function
    result = build_index(index_data, output_dir, index_filename, summary_filename)

    # Assertions
    assert result is True
    assert os.path.exists(os.path.join(output_dir, index_filename))
    assert os.path.exists(os.path.join(output_dir, summary_filename))

    # Check JSON content
    with open(os.path.join(output_dir, index_filename), "r") as f:
        saved_data = json.load(f)
        assert len(saved_data["files"]) == 2
        assert "formatted_date" in saved_data["files"][0]

    # Check markdown content
    with open(os.path.join(output_dir, summary_filename), "r") as f:
        content = f.read()
        assert "# Chat Summaries" in content
        assert "## Table of Contents" in content
        assert "## test1.txt" in content
        assert "## test2.txt" in content
        assert "**Topics:** topic1, topic2" in content


def test_build_index_invalid_data():
    """Test building index with invalid data."""
    # Test with invalid data
    result = build_index(None, "/tmp", "index.json", "summary.md")
    assert result is False

    # Test with empty output directory
    result = build_index({"files": []}, "", "index.json", "summary.md")
    assert result is False

    # Test with empty filenames
    result = build_index({"files": []}, "/tmp", "", "")
    assert result is False


def test_get_timestamp():
    """Test getting timestamp from file."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as f:
        filename = f.name

    try:
        # Get timestamp
        timestamp = get_timestamp(filename)

        # Assertions
        assert timestamp

        # Verify format (ISO format)
        try:
            dt = datetime.fromisoformat(timestamp)
            assert isinstance(dt, datetime)
        except ValueError:
            pytest.fail("Timestamp is not in ISO format")
    finally:
        # Clean up
        os.unlink(filename)


def test_get_timestamp_nonexistent_file():
    """Test getting timestamp from non-existent file."""
    timestamp = get_timestamp("/nonexistent/file.txt")
    assert timestamp == ""
