"""
Tests for the main chat-indexer script.
"""

import os
import sys
import tempfile
import pytest
from unittest.mock import patch, MagicMock

# Add project root to path to import main script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import chat_indexer


@pytest.fixture
def sample_files():
    """Create sample files for testing."""
    files = []

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a few sample files
        txt_file = os.path.join(tmpdir, "sample1.txt")
        with open(txt_file, "w") as f:
            f.write("User: Hello\nAssistant: Hi there")
        files.append(txt_file)

        json_file = os.path.join(tmpdir, "sample2.json")
        with open(json_file, "w") as f:
            f.write('{"messages":[{"role":"user","content":"Hello"},{"role":"assistant","content":"Hi there"}]}')
        files.append(json_file)

        # Create nested directory
        nested_dir = os.path.join(tmpdir, "nested")
        os.makedirs(nested_dir)

        md_file = os.path.join(nested_dir, "sample3.md")
        with open(md_file, "w") as f:
            f.write("# Chat\n\nUser: Hello\n\nAssistant: Hi there")
        files.append(md_file)

        yield tmpdir, files


def test_parse_arguments():
    """Test argument parsing."""
    # Mock command line arguments
    test_args = [
        "chat-indexer.py",
        "--input-dir",
        "/test/input",
        "--output-dir",
        "/test/output",
        "--llm-provider",
        "test-provider",
        "--log-level",
        "DEBUG",
    ]

    with patch("sys.argv", test_args):
        args = chat_indexer.parse_arguments()

        # Assertions
        assert args.input_dir == "/test/input"
        assert args.output_dir == "/test/output"
        assert args.llm_provider == "test-provider"
        assert args.log_level == "DEBUG"


def test_get_chat_files(sample_files):
    """Test getting chat files from directory."""
    tmpdir, expected_files = sample_files

    # Test getting files
    found_files = chat_indexer.get_chat_files(tmpdir, [".txt", ".json", ".md"])

    # Should have found all files (might be in different order)
    assert len(found_files) == len(expected_files)

    # Each expected file should be in the results
    for expected_file in expected_files:
        normalized_path = os.path.normpath(expected_file)
        assert any(os.path.normpath(f) == normalized_path for f in found_files)


def test_process_file(mock_llm_client):
    """Test processing a single file."""
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write(b"User: Hello\nAssistant: Hi there")
        filename = f.name

    try:
        # Process the file
        result = chat_indexer.process_file(filename, mock_llm_client, 3)

        # Assertions
        assert result["filename"] == os.path.basename(filename)
        assert result["path"] == filename
        assert "timestamp" in result
        assert result["topics"] == ["machine learning", "artificial intelligence", "chatbot"]
        assert result["summary"] == "A conversation about machine learning and artificial intelligence."
        assert result["message_count"] == 2
    finally:
        # Clean up
        os.unlink(filename)


@patch("chat_indexer.build_index")
@patch("chat_indexer.process_file")
@patch("chat_indexer.get_chat_files")
@patch("chat_indexer.setup_logger")
def test_main(mock_setup_logger, mock_get_files, mock_process, mock_build_index, sample_files):
    """Test the main function."""
    tmpdir, files = sample_files

    # Configure mocks
    mock_logger = MagicMock()
    mock_setup_logger.return_value = mock_logger
    mock_get_files.return_value = files

    # Mock process_file to return predictable results
    mock_process.side_effect = lambda file, client, max_keywords: {
        "filename": os.path.basename(file),
        "path": file,
        "timestamp": "2023-01-01T00:00:00",
        "topics": ["topic1", "topic2"],
        "summary": "Test summary",
        "message_count": 2,
    }

    # Mock build_index to return success
    mock_build_index.return_value = True

    # Mock command line arguments
    test_args = [
        "chat-indexer.py",
        "--input-dir",
        tmpdir,
        "--output-dir",
        os.path.join(tmpdir, "output"),
        "--llm-provider",
        "test-provider",
    ]

    with patch("sys.argv", test_args):
        # Run main function
        chat_indexer.main()

        # Assertions
        assert mock_setup_logger.called
        assert mock_get_files.called
        assert mock_process.call_count == len(files)
        assert mock_build_index.called

        # Check that build_index was called with correct data
        build_index_args = mock_build_index.call_args[0]
        assert isinstance(build_index_args[0], dict)
        assert "files" in build_index_args[0]
        assert len(build_index_args[0]["files"]) == len(files)
