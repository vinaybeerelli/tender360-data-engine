"""
Utility helper functions
"""

import time
import random
from functools import wraps
from typing import Callable, Any

from .logger import log
from .exceptions import RetryException


def retry(max_attempts=3, backoff_factor=2, exceptions=(Exception,)):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        backoff_factor: Multiplier for delay between retries
        exceptions: Tuple of exceptions to catch
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        log.error(f"Failed after {max_attempts} attempts: {e}")
                        raise RetryException(f"Max retries exceeded for {func.__name__}")
                    
                    delay = backoff_factor ** attempt
                    log.warning(f"Attempt {attempt} failed, retrying in {delay}s: {e}")
                    time.sleep(delay)
            
        return wrapper
    return decorator


def random_delay(min_seconds=2, max_seconds=5):
    """
    Random delay between requests to avoid rate limiting.
    
    Args:
        min_seconds: Minimum delay in seconds
        max_seconds: Maximum delay in seconds
    """
    delay = random.uniform(min_seconds, max_seconds)
    log.debug(f"Sleeping for {delay:.2f}s")
    time.sleep(delay)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing special characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove special characters
    import re
    filename = re.sub(r'[^\w\s-]', '', filename)
    # Replace spaces with underscores
    filename = re.sub(r'[-\s]+', '_', filename)
    return filename.strip('_')


def parse_indian_currency(amount_str: str) -> float:
    """
    Parse Indian currency format (e.g., "1,50,000.00") to float.
    
    Args:
        amount_str: Amount string in Indian format
        
    Returns:
        Float value
    """
    # Remove currency symbols and commas
    cleaned = amount_str.replace('Rs.', '').replace('INR', '').replace(',', '').strip()
    try:
        return float(cleaned)
    except ValueError:
        log.warning(f"Failed to parse amount: {amount_str}")
        return 0.0

