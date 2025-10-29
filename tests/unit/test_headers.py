"""
Tests for HTTP headers configuration.

Ensures that all HTTP headers include the X-Requested-With: XMLHttpRequest header.
"""

from config.constants import API_HEADERS, DOWNLOAD_HEADERS


class TestAPIHeaders:
    """Test API headers configuration."""

    def test_api_headers_contains_x_requested_with(self):
        """Verify API_HEADERS contains X-Requested-With header."""
        assert "X-Requested-With" in API_HEADERS
        assert API_HEADERS["X-Requested-With"] == "XMLHttpRequest"

    def test_api_headers_contains_required_fields(self):
        """Verify API_HEADERS contains all required fields."""
        required_headers = [
            "Accept",
            "Accept-Encoding",
            "Accept-Language",
            "Content-Type",
            "Origin",
            "Referer",
            "X-Requested-With",
            "User-Agent",
        ]
        for header in required_headers:
            assert header in API_HEADERS, f"Missing required header: {header}"

    def test_api_headers_content_type(self):
        """Verify Content-Type is set correctly for API requests."""
        assert API_HEADERS["Content-Type"] == "application/x-www-form-urlencoded; charset=UTF-8"


class TestDownloadHeaders:
    """Test download headers configuration."""

    def test_download_headers_contains_x_requested_with(self):
        """Verify DOWNLOAD_HEADERS contains X-Requested-With header."""
        assert "X-Requested-With" in DOWNLOAD_HEADERS
        assert DOWNLOAD_HEADERS["X-Requested-With"] == "XMLHttpRequest"

    def test_download_headers_contains_required_fields(self):
        """Verify DOWNLOAD_HEADERS contains all required fields."""
        required_headers = [
            "Accept",
            "Accept-Encoding",
            "Accept-Language",
            "Referer",
            "X-Requested-With",
            "User-Agent",
        ]
        for header in required_headers:
            assert header in DOWNLOAD_HEADERS, f"Missing required header: {header}"

    def test_download_headers_accept(self):
        """Verify Accept header is set correctly for downloads."""
        assert DOWNLOAD_HEADERS["Accept"] == "*/*"


class TestHeaderConsistency:
    """Test consistency between different header configurations."""

    def test_both_headers_have_x_requested_with(self):
        """Verify both API and DOWNLOAD headers have X-Requested-With."""
        assert API_HEADERS.get("X-Requested-With") == "XMLHttpRequest"
        assert DOWNLOAD_HEADERS.get("X-Requested-With") == "XMLHttpRequest"

    def test_user_agent_consistency(self):
        """Verify User-Agent is consistent across headers."""
        assert API_HEADERS.get("User-Agent") == DOWNLOAD_HEADERS.get("User-Agent")

    def test_accept_encoding_consistency(self):
        """Verify Accept-Encoding is consistent across headers."""
        assert API_HEADERS.get("Accept-Encoding") == DOWNLOAD_HEADERS.get("Accept-Encoding")
