"""
Unit tests for retry logic and error handling
"""

import pytest
import time
from unittest.mock import Mock, patch
from requests.exceptions import Timeout, ConnectionError, RequestException

from src.utils.helpers import retry
from src.utils.exceptions import RetryException


class TestRetryDecorator:
    """Test suite for retry decorator"""

    def test_retry_success_on_first_attempt(self):
        """Test that function succeeds on first attempt without retry"""
        mock_func = Mock(return_value="success")
        decorated = retry(max_attempts=3)(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 1

    def test_retry_success_on_second_attempt(self):
        """Test that function succeeds on second attempt after one failure"""
        mock_func = Mock(side_effect=[Exception("Error"), "success"])
        decorated = retry(max_attempts=3, backoff_factor=0.1)(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 2

    def test_retry_exceeds_max_attempts(self):
        """Test that RetryException is raised when max attempts exceeded"""
        mock_func = Mock(side_effect=Exception("Persistent error"))
        decorated = retry(max_attempts=3, backoff_factor=0.1)(mock_func)

        with pytest.raises(RetryException) as exc_info:
            decorated()

        assert "Max retries (3) exceeded" in str(exc_info.value)
        assert mock_func.call_count == 3

    def test_retry_with_specific_exception(self):
        """Test retry with specific exception type"""
        mock_func = Mock(side_effect=[Timeout("Timeout error"), "success"])
        decorated = retry(max_attempts=3, backoff_factor=0.1, exceptions=(Timeout,))(
            mock_func
        )

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 2

    def test_retry_does_not_catch_wrong_exception(self):
        """Test that retry doesn't catch exceptions not in the tuple"""
        mock_func = Mock(side_effect=ValueError("Wrong exception"))
        decorated = retry(max_attempts=3, exceptions=(Timeout,))(mock_func)

        with pytest.raises(ValueError):
            decorated()

        assert mock_func.call_count == 1

    def test_retry_exponential_backoff(self):
        """Test exponential backoff timing"""
        mock_func = Mock(
            side_effect=[Exception("Error 1"), Exception("Error 2"), "success"]
        )
        decorated = retry(max_attempts=3, backoff_factor=2)(mock_func)

        start_time = time.time()
        result = decorated()
        elapsed_time = time.time() - start_time

        assert result == "success"
        # Should wait 2^1 + 2^2 = 2 + 4 = 6 seconds total
        assert elapsed_time >= 6.0
        assert mock_func.call_count == 3

    def test_retry_preserves_function_name(self):
        """Test that decorator preserves original function name"""

        @retry(max_attempts=3)
        def test_function():
            """Test docstring"""
            return "result"

        assert test_function.__name__ == "test_function"
        assert "Test docstring" in test_function.__doc__

    def test_retry_with_args_and_kwargs(self):
        """Test retry with function arguments"""
        mock_func = Mock(return_value="success")
        decorated = retry(max_attempts=3)(mock_func)

        result = decorated("arg1", "arg2", kwarg1="value1")

        assert result == "success"
        mock_func.assert_called_once_with("arg1", "arg2", kwarg1="value1")

    def test_retry_multiple_exception_types(self):
        """Test retry with multiple exception types"""
        mock_func = Mock(
            side_effect=[Timeout("timeout"), ConnectionError("connection"), "success"]
        )
        decorated = retry(
            max_attempts=4, backoff_factor=0.1, exceptions=(Timeout, ConnectionError)
        )(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 3

    def test_retry_chains_exception(self):
        """Test that retry chains original exception"""
        mock_func = Mock(side_effect=RequestException("Original error"))
        decorated = retry(
            max_attempts=2, backoff_factor=0.1, exceptions=(RequestException,)
        )(mock_func)

        with pytest.raises(RetryException) as exc_info:
            decorated()

        # Check exception chaining
        assert exc_info.value.__cause__ is not None
        assert isinstance(exc_info.value.__cause__, RequestException)
        assert "Original error" in str(exc_info.value.__cause__)


class TestRetryLogging:
    """Test suite for retry logging behavior"""

    @patch("src.utils.helpers.log")
    def test_retry_logs_attempts(self, mock_log):
        """Test that retry logs each attempt"""
        mock_func = Mock(
            side_effect=[Exception("Error 1"), Exception("Error 2"), "success"]
        )
        decorated = retry(max_attempts=3, backoff_factor=0.1)(mock_func)

        result = decorated()

        assert result == "success"
        # Should log: debug (attempt 1), warning (attempt 1 failed),
        #             debug (attempt 2), warning (attempt 2 failed),
        #             debug (attempt 3), info (success after retries)
        assert mock_log.debug.call_count == 3
        assert mock_log.warning.call_count == 2
        assert mock_log.info.call_count == 1

    @patch("src.utils.helpers.log")
    def test_retry_logs_final_failure(self, mock_log):
        """Test that retry logs final failure"""
        mock_func = Mock(side_effect=Exception("Persistent error"))
        decorated = retry(max_attempts=2, backoff_factor=0.1)(mock_func)

        with pytest.raises(RetryException):
            decorated()

        # Should log error on final failure
        assert mock_log.error.call_count == 1
        error_call = mock_log.error.call_args[0][0]
        assert "failed after 2 attempts" in error_call

    @patch("src.utils.helpers.log")
    def test_retry_logs_success_after_retry(self, mock_log):
        """Test that successful retry recovery is logged"""
        mock_func = Mock(side_effect=[Exception("Error"), "success"])
        decorated = retry(max_attempts=3, backoff_factor=0.1)(mock_func)

        result = decorated()

        assert result == "success"
        # Should log info about successful recovery
        assert mock_log.info.call_count == 1
        info_call = mock_log.info.call_args[0][0]
        assert "succeeded after" in info_call


class TestRetryEdgeCases:
    """Test edge cases for retry logic"""

    def test_retry_with_zero_max_attempts(self):
        """Test retry with zero max attempts (returns None)"""
        mock_func = Mock(side_effect=Exception("Error"))
        decorated = retry(max_attempts=0, backoff_factor=0.1)(mock_func)

        # With zero max attempts, the while loop never executes
        result = decorated()

        # Should return None since the loop never runs
        assert result is None
        assert mock_func.call_count == 0

    def test_retry_with_one_max_attempt(self):
        """Test retry with one max attempt (no retry)"""
        mock_func = Mock(side_effect=Exception("Error"))
        decorated = retry(max_attempts=1, backoff_factor=0.1)(mock_func)

        with pytest.raises(RetryException):
            decorated()

        assert mock_func.call_count == 1

    def test_retry_with_very_small_backoff(self):
        """Test retry with very small backoff factor"""
        mock_func = Mock(side_effect=[Exception("Error"), "success"])
        decorated = retry(max_attempts=3, backoff_factor=0.01)(mock_func)

        start_time = time.time()
        result = decorated()
        elapsed_time = time.time() - start_time

        assert result == "success"
        # With backoff_factor=0.01, delay should be 0.01^1 = 0.01 seconds
        assert elapsed_time < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
