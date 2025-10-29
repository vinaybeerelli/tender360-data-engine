# Error Handling and Retry Logic

## Overview

The Tender Scraper Engine implements comprehensive error handling and retry logic to ensure reliable operation and >90% success rate. This document describes the error handling mechanisms, retry strategies, and best practices.

## Table of Contents

- [Retry Decorator](#retry-decorator)
- [Exception Hierarchy](#exception-hierarchy)
- [API Scraper Error Handling](#api-scraper-error-handling)
- [Configuration](#configuration)
- [Best Practices](#best-practices)
- [Logging](#logging)

## Retry Decorator

### Overview

The `@retry` decorator provides automatic retry functionality with exponential backoff for any function that may fail due to transient errors.

### Features

- **Exponential Backoff**: Delay between retries increases exponentially (2^attempt)
- **Configurable Attempts**: Set maximum number of retry attempts
- **Exception Filtering**: Specify which exceptions should trigger retries
- **Comprehensive Logging**: Detailed logs for each attempt and failure
- **Exception Chaining**: Preserves original exception for debugging

### Usage

```python
from src.utils.helpers import retry
from requests.exceptions import RequestException

@retry(max_attempts=3, backoff_factor=2, exceptions=(RequestException,))
def fetch_data():
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_attempts` | int | 3 | Maximum number of retry attempts |
| `backoff_factor` | float | 2 | Multiplier for exponential backoff |
| `exceptions` | tuple | (Exception,) | Tuple of exception types to catch |

### Backoff Timing

The delay between retries follows this formula:

```
delay = backoff_factor ^ attempt
```

Example with `backoff_factor=2`:
- Attempt 1 fails → wait 2¹ = 2 seconds
- Attempt 2 fails → wait 2² = 4 seconds
- Attempt 3 fails → wait 2³ = 8 seconds

### Example Output

```
2025-10-29 19:12:30 | DEBUG    | Executing fetch_data (attempt 1/3)
2025-10-29 19:12:32 | WARNING  | ⚠ fetch_data attempt 1/3 failed: Timeout: Connection timeout. Retrying in 2s...
2025-10-29 19:12:35 | DEBUG    | Executing fetch_data (attempt 2/3)
2025-10-29 19:12:37 | INFO     | ✓ fetch_data succeeded after 2 attempt(s)
```

## Exception Hierarchy

### Custom Exceptions

The scraper uses a hierarchy of custom exceptions for precise error handling:

```python
TenderScraperException (Base)
├── ScraperException        # General scraping errors
├── NetworkException        # Network-related errors
├── RetryException          # Max retries exceeded
├── DatabaseException       # Database operations
├── ParserException         # Document parsing
├── ValidationException     # Data validation
└── ConfigurationException  # Configuration errors
```

### When to Use Each Exception

| Exception | Use Case | Example |
|-----------|----------|---------|
| `NetworkException` | Network failures | Connection timeout, DNS errors |
| `ScraperException` | Scraping logic errors | Invalid HTML structure, parsing errors |
| `RetryException` | Max retries exceeded | After all retry attempts fail |
| `ValidationException` | Invalid input data | Missing required fields, invalid format |

### Example

```python
from src.utils.exceptions import NetworkException, ScraperException

try:
    response = session.get(url, timeout=30)
    response.raise_for_status()
except Timeout as e:
    raise NetworkException(f"Request timed out: {e}") from e
except ConnectionError as e:
    raise NetworkException(f"Connection failed: {e}") from e
except Exception as e:
    raise ScraperException(f"Unexpected error: {e}") from e
```

## API Scraper Error Handling

### Session Management

The API scraper implements robust session management with error handling:

```python
@retry(max_attempts=3, backoff_factor=2, exceptions=(RequestException,))
def _establish_session(self):
    """Establish session with retry logic"""
    try:
        self.session = requests.Session()
        # Visit main page to get cookies
        response = self.session.get(base_url, timeout=30)
        response.raise_for_status()
    except Timeout as e:
        raise NetworkException(f"Session establishment timed out: {e}") from e
    except ConnectionError as e:
        raise NetworkException(f"Failed to connect: {e}") from e
```

### Method-Level Error Handling

Each scraper method includes comprehensive error handling:

#### 1. Input Validation

```python
def scrape_tender_details(self, tender_id: str) -> Dict:
    # Validate input
    if not tender_id or not isinstance(tender_id, str):
        raise ValueError(f"Invalid tender_id: {tender_id}")
```

#### 2. Session Check

```python
    # Ensure session is established
    if not self.session:
        log.warning("Session not established, creating new session")
        self._establish_session()
```

#### 3. Network Error Handling

```python
    try:
        # ... operation ...
    except Timeout as e:
        raise NetworkException(f"Operation timed out: {e}") from e
    except ConnectionError as e:
        raise NetworkException(f"Connection failed: {e}") from e
    except RequestException as e:
        raise NetworkException(f"Request failed: {e}") from e
```

#### 4. Catch-All Handler

```python
    except Exception as e:
        log.error(f"Unexpected error: {e}", exc_info=True)
        raise ScraperException(f"Unexpected error: {e}") from e
```

### Cleanup

The cleanup method never raises exceptions:

```python
def cleanup(self):
    """Clean up session with proper error handling."""
    try:
        if self.session:
            self.session.close()
            log.info("Session closed successfully")
    except Exception as e:
        log.error(f"Error while closing session: {e}")
        # Don't raise exception during cleanup
```

## Configuration

### Environment Variables

Configure retry behavior via environment variables in `.env`:

```bash
# Retry configuration
MAX_RETRIES=3
REQUEST_TIMEOUT=30

# Delays between requests
MIN_DELAY=2
MAX_DELAY=5
```

### Constants

Configure retry behavior in `config/constants.py`:

```python
RETRY_CONFIG = {
    "max_attempts": 3,
    "backoff_factor": 2,
    "timeout": 30,
}

# HTTP Status codes that trigger retries
RETRY_STATUS_CODES = [408, 429, 500, 502, 503, 504]
```

### Usage in Code

```python
from config.constants import RETRY_CONFIG

@retry(**RETRY_CONFIG, exceptions=(RequestException,))
def my_function():
    pass
```

## Best Practices

### 1. Use Specific Exceptions

✅ **Good:**
```python
@retry(max_attempts=3, exceptions=(RequestException,))
def fetch_data():
    pass
```

❌ **Bad:**
```python
@retry(max_attempts=3, exceptions=(Exception,))  # Too broad
def fetch_data():
    pass
```

### 2. Chain Exceptions

✅ **Good:**
```python
except Timeout as e:
    raise NetworkException(f"Timeout: {e}") from e
```

❌ **Bad:**
```python
except Timeout as e:
    raise NetworkException(f"Timeout: {e}")  # Loses stack trace
```

### 3. Log Before Raising

✅ **Good:**
```python
except Exception as e:
    log.error(f"Failed to process: {e}", exc_info=True)
    raise ScraperException(f"Processing failed: {e}") from e
```

### 4. Don't Catch in Cleanup

✅ **Good:**
```python
def cleanup(self):
    try:
        self.session.close()
    except Exception as e:
        log.error(f"Cleanup error: {e}")
        # Don't raise
```

❌ **Bad:**
```python
def cleanup(self):
    self.session.close()  # May raise during cleanup
```

### 5. Use Appropriate Backoff

For **fast operations** (API calls):
```python
@retry(max_attempts=3, backoff_factor=2)  # 2s, 4s, 8s
```

For **slow operations** (file downloads):
```python
@retry(max_attempts=5, backoff_factor=1.5)  # 1.5s, 2.25s, 3.37s, ...
```

## Logging

### Log Levels

| Level | When to Use | Example |
|-------|-------------|---------|
| `DEBUG` | Detailed operation info | "Executing function (attempt 1/3)" |
| `INFO` | Successful operations | "✓ Function succeeded after 2 attempts" |
| `WARNING` | Recoverable errors | "⚠ Attempt 1/3 failed, retrying..." |
| `ERROR` | Operation failures | "✗ Function failed after 3 attempts" |

### Log Format

All logs include:
- Timestamp
- Log level
- Function name and line number
- Descriptive message

Example:
```
2025-10-29 19:12:30 | WARNING | src.scrapers.api_scraper:scrape_tender_list:85 - 
  ⚠ scrape_tender_list attempt 1/3 failed: Timeout: Connection timeout. Retrying in 2s...
```

### Structured Logging

The retry decorator provides structured, consistent logging:

```python
# On retry attempt
log.debug(f"Executing {func_name} (attempt {attempt + 1}/{max_attempts})")

# On retry needed
log.warning(
    f"⚠ {func_name} attempt {attempt}/{max_attempts} failed: "
    f"{exception_type}: {error_message}. Retrying in {delay}s..."
)

# On success after retry
log.info(f"✓ {func_name} succeeded after {attempt + 1} attempt(s)")

# On final failure
log.error(
    f"✗ {func_name} failed after {max_attempts} attempts. "
    f"Last error: {exception_type}: {error_message}"
)
```

## Testing

### Unit Tests

We provide comprehensive unit tests for retry logic and error handling:

- **`tests/unit/test_retry_logic.py`**: 16 tests for retry decorator
- **`tests/unit/test_api_scraper_errors.py`**: 22 tests for API scraper error handling

### Running Tests

```bash
# Run all tests
pytest tests/unit/

# Run retry tests only
pytest tests/unit/test_retry_logic.py -v

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=html
```

### Test Coverage

- Retry decorator: 72% coverage
- API scraper: 72% coverage
- Total: 38 tests, all passing

## Monitoring

### Success Rate

Track retry success rate:

```python
from src.utils.logger import log

# Log includes retry count
log.info(f"✓ scrape_tender_list succeeded after 2 attempt(s)")
```

### Error Tracking

Monitor error patterns:

```bash
# Count errors by type
grep "ERROR" logs/scraper.log | awk '{print $5}' | sort | uniq -c

# Track retry patterns
grep "⚠" logs/scraper.log | wc -l
```

### Alerting

Set up alerts for:
- High retry rates (>50%)
- Frequent final failures
- Specific error patterns (e.g., 403, 429)

## Troubleshooting

### Common Issues

#### Issue: Too Many Retries

**Symptom:** Operations taking too long

**Solution:**
```python
# Reduce max attempts or increase backoff
@retry(max_attempts=2, backoff_factor=1.5)
```

#### Issue: Not Enough Retries

**Symptom:** Failures on transient errors

**Solution:**
```python
# Increase max attempts
@retry(max_attempts=5, backoff_factor=2)
```

#### Issue: Wrong Exception Type

**Symptom:** Retries not triggering

**Solution:**
```python
# Add more exception types
@retry(exceptions=(RequestException, Timeout, ConnectionError))
```

## Future Enhancements

Planned improvements:

1. **Adaptive Backoff**: Adjust based on server response
2. **Circuit Breaker**: Stop retrying after threshold
3. **Metrics Collection**: Track success/failure rates
4. **Custom Retry Strategies**: Per-endpoint configuration
5. **Retry Budget**: Limit total retry time

## References

- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Requests Library Exceptions](https://requests.readthedocs.io/en/latest/api/#exceptions)
- [Exponential Backoff Algorithm](https://en.wikipedia.org/wiki/Exponential_backoff)

---

**Last Updated:** October 29, 2025  
**Version:** 1.0  
**Author:** Agent ALPHA (API Scraping Specialist)
