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
    Retry decorator with exponential backoff and comprehensive error logging.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        backoff_factor: Multiplier for delay between retries (default: 2)
        exceptions: Tuple of exceptions to catch (default: all exceptions)

    Returns:
        Decorated function with retry logic

    Example:
        @retry(max_attempts=5, backoff_factor=2, exceptions=(requests.RequestException,))
        def fetch_data():
            return requests.get(url)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            last_exception = None
            func_name = getattr(func, "__name__", "unknown_function")

            while attempt < max_attempts:
                try:
                    log.debug(
                        f"Executing {func_name} (attempt {attempt + 1}/{max_attempts})"
                    )
                    result = func(*args, **kwargs)

                    # Log successful retry recovery
                    if attempt > 0:
                        log.info(
                            f"✓ {func_name} succeeded after {attempt + 1} attempt(s)"
                        )

                    return result

                except exceptions as e:
                    attempt += 1
                    last_exception = e
                    exception_type = type(e).__name__

                    if attempt >= max_attempts:
                        # Final failure - log comprehensive error details
                        log.error(
                            f"✗ {func_name} failed after {max_attempts} attempts. "
                            f"Last error: {exception_type}: {str(e)}"
                        )
                        raise RetryException(
                            f"Max retries ({max_attempts}) exceeded for {func_name}. "
                            f"Last error: {exception_type}: {str(e)}"
                        ) from e

                    # Calculate delay with exponential backoff
                    delay = backoff_factor**attempt
                    log.warning(
                        f"⚠ {func_name} attempt {attempt}/{max_attempts} failed: "
                        f"{exception_type}: {str(e)}. Retrying in {delay}s..."
                    )
                    time.sleep(delay)

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

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

    filename = re.sub(r"[^\w\s-]", "", filename)
    # Replace spaces with underscores
    filename = re.sub(r"[-\s]+", "_", filename)
    return filename.strip("_")


def parse_indian_currency(amount_str: str) -> float:
    """
    Parse Indian currency format (e.g., "1,50,000.00") to float.

    Args:
        amount_str: Amount string in Indian format

    Returns:
        Float value
    """
    # Remove currency symbols and commas
    cleaned = amount_str.replace("Rs.", "").replace("INR", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        log.warning(f"Failed to parse amount: {amount_str}")
        return 0.0
