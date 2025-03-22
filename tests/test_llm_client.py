"""
Tests for the llm_client module.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.llm_client import LLMClient


@pytest.fixture
def mock_completion_response():
    """Mock completion response fixture."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "topic1, topic2, topic3"
    return mock_response


@patch("src.llm_client.completion")
def test_extract_topics(mock_completion, mock_completion_response):
    """Test extracting topics."""
    # Configure the mock
    mock_completion.return_value = mock_completion_response

    # Create client and test
    client = LLMClient("test-provider")
    topics = client.extract_topics(["Hello", "How are you?"], 3)

    # Assertions
    assert mock_completion.called
    assert len(topics) == 3
    assert topics == ["topic1", "topic2", "topic3"]


@patch("src.llm_client.completion")
def test_extract_topics_empty_messages(mock_completion):
    """Test extracting topics with empty messages."""
    # Create client and test
    client = LLMClient("test-provider")
    topics = client.extract_topics([], 3)

    # Assertions
    assert not mock_completion.called
    assert topics == []


@patch("src.llm_client.completion")
def test_summarize(mock_completion, mock_completion_response):
    """Test summarizing messages."""
    # Configure the mock
    mock_completion_response.choices[0].message.content = "This is a summary."
    mock_completion.return_value = mock_completion_response

    # Create client and test
    client = LLMClient("test-provider")
    summary = client.summarize(["Hello", "How are you?"])

    # Assertions
    assert mock_completion.called
    assert summary == "This is a summary."


@patch("src.llm_client.completion")
def test_summarize_empty_messages(mock_completion):
    """Test summarizing empty messages."""
    # Create client and test
    client = LLMClient("test-provider")
    summary = client.summarize([])

    # Assertions
    assert not mock_completion.called
    assert summary == "No content to summarize."


@patch("src.llm_client.completion")
def test_rate_limiting(mock_completion, mock_completion_response):
    """Test rate limiting between requests."""
    # Configure the mock
    mock_completion.return_value = mock_completion_response

    # Create client with high rate limit for testing
    client = LLMClient("test-provider", rate_limit_delay=0.1)

    # Make two requests and measure time
    client.extract_topics(["Hello"], 3)
    client.extract_topics(["Hello again"], 3)

    # Assertions
    assert mock_completion.call_count == 2


@patch("src.llm_client.completion")
def test_completion_error_handling(mock_completion):
    """Test error handling in completion requests."""
    # Configure the mock to raise an exception
    mock_completion.side_effect = Exception("API Error")

    # Create client and test
    client = LLMClient("test-provider")

    # It should return empty topics when an error occurs
    topics = client.extract_topics(["Hello"], 3)

    # Assertions
    assert topics == []
