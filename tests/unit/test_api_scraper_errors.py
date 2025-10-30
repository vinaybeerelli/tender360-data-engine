"""
Unit tests for API scraper error handling
"""

import pytest
from unittest.mock import Mock, patch
from requests.exceptions import Timeout, ConnectionError, RequestException

from src.scrapers.api_scraper import APIScraper
from src.utils.exceptions import ScraperException, NetworkException


class TestAPIScraperSessionManagement:
    """Test suite for session management and error handling"""

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_session_establishment_success(self, mock_session_class):
        """Test successful session establishment"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        scraper = APIScraper()

        assert scraper.session is not None
        assert scraper.session == mock_session

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_session_establishment_with_timeout(self, mock_session_class):
        """Test session establishment with timeout error"""
        mock_session_class.side_effect = Timeout("Connection timeout")

        with pytest.raises(NetworkException) as exc_info:
            APIScraper()

        assert "Session establishment timed out" in str(exc_info.value)

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_session_establishment_with_connection_error(self, mock_session_class):
        """Test session establishment with connection error"""
        mock_session_class.side_effect = ConnectionError("Connection failed")

        with pytest.raises(NetworkException) as exc_info:
            APIScraper()

        assert "Failed to connect during session establishment" in str(exc_info.value)

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_session_establishment_with_request_exception(self, mock_session_class):
        """Test session establishment with generic request exception"""
        mock_session_class.side_effect = RequestException("Request failed")

        with pytest.raises(NetworkException) as exc_info:
            APIScraper()

        assert "Session establishment failed" in str(exc_info.value)

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_session_establishment_with_unexpected_error(self, mock_session_class):
        """Test session establishment with unexpected error"""
        mock_session_class.side_effect = ValueError("Unexpected error")

        with pytest.raises(ScraperException) as exc_info:
            APIScraper()

        assert "Unexpected error establishing session" in str(exc_info.value)

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_session_cleanup_success(self, mock_session_class):
        """Test successful session cleanup"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        scraper = APIScraper()
        scraper.cleanup()

        mock_session.close.assert_called_once()

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_session_cleanup_with_error(self, mock_session_class):
        """Test session cleanup with error (should not raise)"""
        mock_session = Mock()
        mock_session.close.side_effect = Exception("Close error")
        mock_session_class.return_value = mock_session

        scraper = APIScraper()
        # Should not raise exception
        scraper.cleanup()

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_session_cleanup_when_none(self, mock_session_class):
        """Test cleanup when session is None"""
        mock_session_class.return_value = Mock()
        scraper = APIScraper()
        scraper.session = None

        # Should not raise exception
        scraper.cleanup()


class TestAPIScraperTenderList:
    """Test suite for tender list scraping error handling"""

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_scrape_tender_list_basic(self, mock_session_class):
        """Test basic tender list scraping"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        scraper = APIScraper()
        result = scraper.scrape_tender_list(limit=10)

        assert isinstance(result, list)
        assert len(result) == 0  # Empty since not implemented yet

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_scrape_tender_list_with_no_session(self, mock_session_class):
        """Test tender list scraping when session is None"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        scraper = APIScraper()
        scraper.session = None

        result = scraper.scrape_tender_list(limit=10)

        # Should re-establish session
        assert scraper.session is not None
        assert isinstance(result, list)

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_scrape_tender_list_with_timeout(self, mock_session_class):
        """Test tender list scraping with timeout error"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        scraper = APIScraper()

        # Mock the method to raise Timeout
        with patch.object(scraper, "scrape_tender_list") as mock_method:
            mock_method.side_effect = NetworkException("Tender list scraping timed out")

            with pytest.raises(NetworkException) as exc_info:
                scraper.scrape_tender_list(limit=10)

            assert "timed out" in str(exc_info.value)


class TestAPIScraperTenderDetails:
    """Test suite for tender details scraping error handling"""

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_scrape_tender_details_basic(self, mock_session_class):
        """Test basic tender details scraping"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        scraper = APIScraper()
        result = scraper.scrape_tender_details("T12345")

        assert isinstance(result, dict)
        assert len(result) == 0  # Empty since not implemented yet

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_scrape_tender_details_with_invalid_id_none(self, mock_session_class):
        """Test tender details scraping with None tender_id"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        scraper = APIScraper()

        with pytest.raises(ScraperException) as exc_info:
            scraper.scrape_tender_details(None)

        assert "Invalid data for tender" in str(exc_info.value)

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_scrape_tender_details_with_invalid_id_empty(self, mock_session_class):
        """Test tender details scraping with empty tender_id"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        scraper = APIScraper()

        with pytest.raises(ScraperException) as exc_info:
            scraper.scrape_tender_details("")

        assert "Invalid data for tender" in str(exc_info.value)

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_scrape_tender_details_with_invalid_id_type(self, mock_session_class):
        """Test tender details scraping with invalid tender_id type"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        scraper = APIScraper()

        with pytest.raises(ScraperException) as exc_info:
            scraper.scrape_tender_details(12345)  # Number instead of string

        assert "Invalid data for tender" in str(exc_info.value)

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_scrape_tender_details_recreates_session_if_needed(
        self, mock_session_class
    ):
        """Test that tender details scraping recreates session if needed"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        scraper = APIScraper()
        scraper.session = None

        result = scraper.scrape_tender_details("T12345")

        # Should re-establish session
        assert scraper.session is not None
        assert isinstance(result, dict)


class TestAPIScraperDocumentURLs:
    """Test suite for document URL extraction error handling"""

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_extract_document_urls_basic(self, mock_session_class):
        """Test basic document URL extraction"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        scraper = APIScraper()
        result = scraper.extract_document_urls("T12345")

        assert isinstance(result, list)
        assert len(result) == 0  # Empty since not implemented yet

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_extract_document_urls_with_invalid_id_none(self, mock_session_class):
        """Test document URL extraction with None tender_id"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        scraper = APIScraper()

        with pytest.raises(ScraperException) as exc_info:
            scraper.extract_document_urls(None)

        assert "Invalid data for tender" in str(exc_info.value)

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_extract_document_urls_with_invalid_id_empty(self, mock_session_class):
        """Test document URL extraction with empty tender_id"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        scraper = APIScraper()

        with pytest.raises(ScraperException) as exc_info:
            scraper.extract_document_urls("")

        assert "Invalid data for tender" in str(exc_info.value)

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_extract_document_urls_with_invalid_id_type(self, mock_session_class):
        """Test document URL extraction with invalid tender_id type"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        scraper = APIScraper()

        with pytest.raises(ScraperException) as exc_info:
            scraper.extract_document_urls(12345)  # Number instead of string

        assert "Invalid data for tender" in str(exc_info.value)

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_extract_document_urls_recreates_session_if_needed(
        self, mock_session_class
    ):
        """Test that document URL extraction recreates session if needed"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        scraper = APIScraper()
        scraper.session = None

        result = scraper.extract_document_urls("T12345")

        # Should re-establish session
        assert scraper.session is not None
        assert isinstance(result, list)


class TestAPIScraperRetryBehavior:
    """Test suite for retry behavior in API scraper"""

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_retry_decorator_is_applied_to_methods(self, mock_session_class):
        """Test that retry decorator is properly applied"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        scraper = APIScraper()

        # Check that methods have the retry decorator wrapper
        assert hasattr(scraper.scrape_tender_list, "__wrapped__")
        assert hasattr(scraper.scrape_tender_details, "__wrapped__")
        assert hasattr(scraper.extract_document_urls, "__wrapped__")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
