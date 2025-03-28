"""
LLM client module for interacting with language models.
Uses litellm to support various LLM providers.
"""

import time
import logging
import asyncio
import traceback
from typing import List, Dict, Any, Optional, Union
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from litellm import (
    completion,
    acompletion,
    RateLimitError,
    ServiceUnavailableError,
    ModelResponse,
    InvalidRequestError,
    AuthenticationError,
    ContextWindowExceededError,
)

logger = logging.getLogger("LLMChatIndexer")


class LLMClient:
    """Client for interacting with LLMs via litellm."""

    def __init__(self, provider, max_retries=3, rate_limit_delay=1.0):
        """
        Initialize LLM client with specified provider.

        Args:
            provider (str): LLM provider identifier (e.g., 'gemini/gemini-2.0-flash')
            max_retries (int): Maximum number of retry attempts
            rate_limit_delay (float): Delay in seconds between API calls
        """
        self.provider = provider
        self.max_retries = max_retries
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0

    def _handle_rate_limit(self):
        """Implement basic rate limiting between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    @retry(
        stop=stop_after_attempt(lambda self: self.max_retries),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((RateLimitError, ServiceUnavailableError)),
        reraise=True,
    )
    def _make_llm_request(self, messages):
        """
        Make a request to the LLM with retry logic.

        Args:
            messages (list): List of message objects

        Returns:
            ModelResponse: Response from the LLM or None if failed
        """
        self._handle_rate_limit()
        try:
            return completion(model=self.provider, messages=messages)
        except (RateLimitError, ServiceUnavailableError) as e:
            logger.warning(f"LLM API temporary error ({type(e).__name__}): {str(e)}. Retrying...")
            raise  # Will be caught by retry decorator
        except ContextWindowExceededError as e:
            logger.error(f"Context length exceeded: {str(e)}")
            logger.debug(f"Message length: {sum(len(m.get('content', '')) for m in messages)}")
            return None
        except InvalidRequestError as e:
            logger.error(f"Bad request to LLM API: {str(e)}")
            logger.debug(f"Request messages: {messages}")
            return None
        except AuthenticationError as e:
            logger.error(f"Authentication error with LLM provider: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"LLM API error: {str(e)}")
            logger.error(f"Error details: {traceback.format_exc()}")
            return None

    async def _make_llm_request_async(self, messages):
        """
        Make an asynchronous request to the LLM.

        Args:
            messages (list): List of message objects

        Returns:
            ModelResponse: Response from the LLM or None if failed
        """
        self._handle_rate_limit()

        # Implement retry logic manually for async
        retries = 0
        while retries <= self.max_retries:
            try:
                return await acompletion(model=self.provider, messages=messages)
            except (RateLimitError, ServiceUnavailableError) as e:
                retries += 1
                if retries > self.max_retries:
                    logger.error(f"Max retries ({self.max_retries}) exceeded for LLM request")
                    return None

                wait_time = min(2**retries, 10)  # Exponential backoff
                logger.warning(
                    f"LLM API temporary error ({type(e).__name__}): {str(e)}. Retrying in {wait_time}s... (Attempt {retries}/{self.max_retries})"
                )
                await asyncio.sleep(wait_time)
            except ContextWindowExceededError as e:
                logger.error(f"Context length exceeded: {str(e)}")
                logger.debug(f"Message length: {sum(len(m.get('content', '')) for m in messages)}")
                return None
            except InvalidRequestError as e:
                logger.error(f"Bad request to LLM API: {str(e)}")
                logger.debug(f"Request messages: {messages}")
                return None
            except AuthenticationError as e:
                logger.error(f"Authentication error with LLM provider: {str(e)}")
                return None
            except Exception as e:
                logger.error(f"LLM API error: {str(e)}")
                logger.error(f"Error details: {traceback.format_exc()}")
                return None

    def extract_topics(self, messages, max_keywords):
        """
        Extract key topics from chat messages.

        Args:
            messages (list): List of chat messages
            max_keywords (int): Maximum number of topics to extract

        Returns:
            list: Extracted topics or fallback topics if extraction fails
        """
        if not messages:
            logger.warning("No messages provided for topic extraction")
            return []

        # Join messages with separator for context
        message_text = "\n".join(messages)

        # Truncate if too long (provider-dependent)
        if len(message_text) > 15000:
            message_text = message_text[:15000] + "..."
            logger.info("Message text truncated to 15,000 characters for topic extraction")

        prompt = f"Extract exactly {max_keywords} key topics from this chat conversation. Return them as a comma-separated list with no additional text:\n\n{message_text}"

        try:
            response = self._make_llm_request([
                {
                    "role": "system",
                    "content": "You are a topic extraction assistant. Extract exactly the requested number of key topics and return only those topics as a comma-separated list with no explanations or other text.",
                },
                {"role": "user", "content": prompt},
            ])

            if response is None:
                logger.warning("Topic extraction failed, using fallback extraction method")
                # Simple fallback: extract most frequent words as topics
                words = message_text.lower().split()
                # Filter out common words and short words
                common_words = {
                    "the",
                    "and",
                    "a",
                    "to",
                    "of",
                    "in",
                    "is",
                    "it",
                    "you",
                    "that",
                    "was",
                    "for",
                    "on",
                    "are",
                    "with",
                    "as",
                    "I",
                    "his",
                    "they",
                    "be",
                    "at",
                    "this",
                    "have",
                    "from",
                    "or",
                    "had",
                    "by",
                }
                filtered_words = [w for w in words if w not in common_words and len(w) > 3]

                # Count word frequency
                from collections import Counter

                word_counts = Counter(filtered_words)

                # Get most common words
                most_common = word_counts.most_common(max_keywords)
                return [word for word, _ in most_common]

            topics = response.choices[0].message.content.strip().split(",")
            topics = [topic.strip() for topic in topics if topic.strip()]

            if not topics:
                logger.warning("No topics extracted from LLM response, using fallback")
                return ["general discussion"]  # Fallback topic

            return topics[:max_keywords]

        except Exception as e:
            logger.error(f"Failed to extract topics: {str(e)}")
            logger.error(f"Error details: {traceback.format_exc()}")
            # Return generic topics as fallback
            return ["conversation", "discussion"] if max_keywords > 1 else ["conversation"]

    async def extract_topics_async(self, messages, max_keywords):
        """
        Extract key topics from chat messages asynchronously.

        Args:
            messages (list): List of chat messages
            max_keywords (int): Maximum number of topics to extract

        Returns:
            list: Extracted topics
        """
        if not messages:
            logger.warning("No messages provided for topic extraction")
            return []

        # Join messages with separator for context
        message_text = "\n".join(messages)

        # Truncate if too long (provider-dependent)
        if len(message_text) > 15000:
            message_text = f"{message_text[:15000]}..."
            logger.info("Message text truncated to 15,000 characters for topic extraction")

        prompt = f"Extract exactly {max_keywords} key topics from this chat conversation. Return them as a comma-separated list with no additional text:\n\n{message_text}"

        try:
            response = await self._make_llm_request_async([
                {
                    "role": "system",
                    "content": "You are a topic extraction assistant. Extract exactly the requested number of key topics and return only those topics as a comma-separated list with no explanations or other text.",
                },
                {"role": "user", "content": prompt},
            ])

            if response is None:
                logger.warning("Async topic extraction failed, using fallback extraction method")
                # Simple fallback: extract most frequent words as topics
                words = message_text.lower().split()
                # Filter out common words and short words
                common_words = {
                    "the",
                    "and",
                    "a",
                    "to",
                    "of",
                    "in",
                    "is",
                    "it",
                    "you",
                    "that",
                    "was",
                    "for",
                    "on",
                    "are",
                    "with",
                    "as",
                    "I",
                    "his",
                    "they",
                    "be",
                    "at",
                    "this",
                    "have",
                    "from",
                    "or",
                    "had",
                    "by",
                }
                filtered_words = [w for w in words if w not in common_words and len(w) > 3]

                # Count word frequency
                from collections import Counter

                word_counts = Counter(filtered_words)

                # Get most common words
                most_common = word_counts.most_common(max_keywords)
                return [word for word, _ in most_common]

            topics = response.choices[0].message.content.strip().split(",")
            topics = [topic.strip() for topic in topics if topic.strip()]

            if not topics:
                logger.warning("No topics extracted from LLM response, using fallback")
                return ["general discussion"]  # Fallback topic

            return topics[:max_keywords]

        except Exception as e:
            logger.error(f"Failed to extract topics asynchronously: {str(e)}")
            logger.error(f"Error details: {traceback.format_exc()}")
            # Return generic topics as fallback
            return ["conversation", "discussion"] if max_keywords > 1 else ["conversation"]

    def summarize(self, messages):
        """
        Generate a concise summary of chat messages.

        Args:
            messages (list): List of chat messages

        Returns:
            str: Summary of the conversation or fallback message if summarization fails
        """
        if not messages:
            logger.warning("No messages provided for summarization")
            return "No content to summarize."

        # Join messages with separator for context
        message_text = "\n".join(messages)

        # Truncate if too long (provider-dependent)
        if len(message_text) > 15000:
            message_text = message_text[:15000] + "..."
            logger.info("Message text truncated to 15,000 characters for summarization")

        prompt = f"Summarize this chat conversation in a concise paragraph:\n\n{message_text}"

        try:
            response = self._make_llm_request([
                {
                    "role": "system",
                    "content": "You are a summarization assistant. Create a concise, accurate summary of the provided conversation.",
                },
                {"role": "user", "content": prompt},
            ])

            if response is None:
                logger.warning("Summarization failed, generating basic fallback summary")
                # Generate a basic fallback summary
                word_count = len(message_text.split())
                msg_count = len(messages)
                return f"This conversation contains {msg_count} messages with approximately {word_count} words discussing various topics."

            summary = response.choices[0].message.content.strip()
            if not summary:
                return "The conversation was too brief or unclear to summarize effectively."

            return summary

        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            logger.error(f"Error details: {traceback.format_exc()}")

            # Create a more informative fallback message
            try:
                word_count = len(message_text.split())
                msg_count = len(messages)
                return f"Unable to generate detailed summary. Conversation contains {msg_count} messages with approximately {word_count} words."
            except:
                return "Unable to generate summary due to an error."

    async def summarize_async(self, messages):
        """
        Generate a concise summary of chat messages asynchronously.

        Args:
            messages (list): List of chat messages

        Returns:
            str: Summary of the conversation
        """
        if not messages:
            logger.warning("No messages provided for summarization")
            return "No content to summarize."

        # Join messages with separator for context
        message_text = "\n".join(messages)

        # Truncate if too long (provider-dependent)
        if len(message_text) > 15000:
            message_text = message_text[:15000] + "..."
            logger.info("Message text truncated to 15,000 characters for summarization")

        prompt = f"Summarize this chat conversation in a concise paragraph:\n\n{message_text}"

        try:
            response = await self._make_llm_request_async([
                {
                    "role": "system",
                    "content": "You are a summarization assistant. Create a concise, accurate summary of the provided conversation.",
                },
                {"role": "user", "content": prompt},
            ])

            if response is None:
                logger.warning("Async summarization failed, generating basic fallback summary")
                # Generate a basic fallback summary
                word_count = len(message_text.split())
                msg_count = len(messages)
                return f"This conversation contains {msg_count} messages with approximately {word_count} words discussing various topics."

            summary = response.choices[0].message.content.strip()
            if not summary:
                return "The conversation was too brief or unclear to summarize effectively."

            return summary

        except Exception as e:
            logger.error(f"Failed to generate summary asynchronously: {str(e)}")
            logger.error(f"Error details: {traceback.format_exc()}")

            # Create a more informative fallback message
            try:
                word_count = len(message_text.split())
                msg_count = len(messages)
                return f"Unable to generate detailed summary. Conversation contains {msg_count} messages with approximately {word_count} words."
            except:
                return "Unable to generate summary due to an error."
