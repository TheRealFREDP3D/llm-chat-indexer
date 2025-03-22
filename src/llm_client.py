"""
LLM client module for interacting with language models.
Uses litellm to support various LLM providers.
"""

import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from litellm import completion, RateLimitError, ServiceUnavailableError

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
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((RateLimitError, ServiceUnavailableError)),
        reraise=True
    )
    def _make_llm_request(self, messages):
        """
        Make a request to the LLM with retry logic.
        
        Args:
            messages (list): List of message objects
            
        Returns:
            ModelResponse: Response from the LLM
        """
        self._handle_rate_limit()
        try:
            return completion(
                model=self.provider,
                messages=messages
            )
        except (RateLimitError, ServiceUnavailableError) as e:
            logger.warning(f"LLM API temporary error ({type(e).__name__}): {str(e)}. Retrying...")
            raise  # Will be caught by retry decorator
        except Exception as e:
            logger.error(f"LLM API error: {str(e)}")
            raise
    
    def extract_topics(self, messages, max_keywords):
        """
        Extract key topics from chat messages.
        
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
            message_text = message_text[:15000] + "..."
            logger.info("Message text truncated to 15,000 characters for topic extraction")
        
        prompt = f"Extract exactly {max_keywords} key topics from this chat conversation. Return them as a comma-separated list with no additional text:\n\n{message_text}"
        
        try:
            response = self._make_llm_request([
                {"role": "system", "content": "You are a topic extraction assistant. Extract exactly the requested number of key topics and return only those topics as a comma-separated list with no explanations or other text."},
                {"role": "user", "content": prompt}
            ])
            
            topics = response.choices[0].message.content.strip().split(",")
            topics = [topic.strip() for topic in topics if topic.strip()]
            
            return topics[:max_keywords]
            
        except Exception as e:
            logger.error(f"Failed to extract topics: {str(e)}")
            return []
    
    def summarize(self, messages):
        """
        Generate a concise summary of chat messages.
        
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
            response = self._make_llm_request([
                {"role": "system", "content": "You are a summarization assistant. Create a concise, accurate summary of the provided conversation."},
                {"role": "user", "content": prompt}
            ])
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            return "Unable to generate summary due to an error."
