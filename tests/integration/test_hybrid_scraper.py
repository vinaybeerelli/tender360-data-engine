"""
Integration tests for Hybrid Scraper
Tests the integration between API scraper and Selenium fallback
"""

import pytest
from unittest.mock import patch, MagicMock

from src.scrapers.hybrid_scraper import HybridScraper
from src.utils.exceptions import ScraperException


class TestHybridScraperIntegration:
    """Integration tests for HybridScraper."""

    @patch("src.scrapers.hybrid_scraper.APIScraper")
    @patch("src.scrapers.hybrid_scraper.SeleniumScraper")
    def test_api_success_no_fallback(self, mock_selenium_class, mock_api_class):
        """Test that Selenium is not used when API succeeds."""
        # Mock API scraper to return data
        mock_api = MagicMock()
        mock_api.scrape_tender_list.return_value = [{"tender_id": "T-001"}]
        mock_api_class.return_value = mock_api

        hybrid = HybridScraper(headless=True)
        result = hybrid.scrape_tender_list(limit=10)

        assert len(result) == 1
        assert result[0]["tender_id"] == "T-001"
        # Selenium should not be initialized
        mock_selenium_class.assert_not_called()

    @patch("src.scrapers.hybrid_scraper.APIScraper")
    @patch("src.scrapers.hybrid_scraper.SeleniumScraper")
    def test_api_failure_fallback_to_selenium(self, mock_selenium_class, mock_api_class):
        """Test fallback to Selenium when API fails."""
        # Mock API scraper to fail
        mock_api = MagicMock()
        mock_api.scrape_tender_list.side_effect = Exception("API failed")
        mock_api_class.return_value = mock_api

        # Mock Selenium scraper to succeed
        mock_selenium = MagicMock()
        mock_selenium.scrape_tender_list.return_value = [{"tender_id": "T-002"}]
        mock_selenium_class.return_value = mock_selenium

        hybrid = HybridScraper(headless=True)
        result = hybrid.scrape_tender_list(limit=10)

        assert len(result) == 1
        assert result[0]["tender_id"] == "T-002"
        # Both should be called
        mock_api.scrape_tender_list.assert_called_once()
        mock_selenium_class.assert_called_once_with(True)
        mock_selenium.scrape_tender_list.assert_called_once()

    @patch("src.scrapers.hybrid_scraper.APIScraper")
    @patch("src.scrapers.hybrid_scraper.SeleniumScraper")
    def test_api_returns_empty_fallback_to_selenium(self, mock_selenium_class, mock_api_class):
        """Test fallback when API returns empty list."""
        # Mock API scraper to return empty list
        mock_api = MagicMock()
        mock_api.scrape_tender_list.return_value = []
        mock_api_class.return_value = mock_api

        # Mock Selenium scraper to succeed
        mock_selenium = MagicMock()
        mock_selenium.scrape_tender_list.return_value = [{"tender_id": "T-003"}]
        mock_selenium_class.return_value = mock_selenium

        hybrid = HybridScraper(headless=True)
        result = hybrid.scrape_tender_list(limit=10)

        assert len(result) == 1
        assert result[0]["tender_id"] == "T-003"
        mock_selenium_class.assert_called_once()

    @patch("src.scrapers.hybrid_scraper.APIScraper")
    @patch("src.scrapers.hybrid_scraper.SeleniumScraper")
    def test_both_fail_raises_exception(self, mock_selenium_class, mock_api_class):
        """Test exception when both scrapers fail."""
        # Mock both to fail
        mock_api = MagicMock()
        mock_api.scrape_tender_list.side_effect = Exception("API failed")
        mock_api_class.return_value = mock_api

        mock_selenium = MagicMock()
        mock_selenium.scrape_tender_list.side_effect = Exception("Selenium failed")
        mock_selenium_class.return_value = mock_selenium

        hybrid = HybridScraper(headless=True)

        with pytest.raises(ScraperException, match="Both API and Selenium scraping failed"):
            hybrid.scrape_tender_list(limit=10)

    @patch("src.scrapers.hybrid_scraper.APIScraper")
    @patch("src.scrapers.hybrid_scraper.SeleniumScraper")
    def test_selenium_lazy_initialization(self, mock_selenium_class, mock_api_class):
        """Test that Selenium is only initialized when needed."""
        # Mock API to succeed first call
        mock_api = MagicMock()
        mock_api.scrape_tender_list.return_value = [{"tender_id": "T-004"}]
        mock_api_class.return_value = mock_api

        hybrid = HybridScraper(headless=True)

        # First call - API succeeds
        _ = hybrid.scrape_tender_list(limit=10)  # noqa: F841
        assert mock_selenium_class.call_count == 0

        # Mock API to fail second call
        mock_api.scrape_tender_list.side_effect = Exception("API failed")
        mock_selenium = MagicMock()
        mock_selenium.scrape_tender_list.return_value = [{"tender_id": "T-005"}]
        mock_selenium_class.return_value = mock_selenium

        # Second call - API fails, Selenium used
        result2 = hybrid.scrape_tender_list(limit=10)

        # Selenium should now be initialized
        assert mock_selenium_class.call_count == 1
        assert result2[0]["tender_id"] == "T-005"

    @patch("src.scrapers.hybrid_scraper.APIScraper")
    @patch("src.scrapers.hybrid_scraper.SeleniumScraper")
    def test_cleanup_both_scrapers(self, mock_selenium_class, mock_api_class):
        """Test that cleanup is called on both scrapers."""
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api

        mock_selenium = MagicMock()
        mock_selenium.scrape_tender_list.return_value = [{"tender_id": "T-006"}]
        mock_selenium_class.return_value = mock_selenium

        # Force selenium initialization
        mock_api.scrape_tender_list.side_effect = Exception("API failed")

        hybrid = HybridScraper(headless=True)
        hybrid.scrape_tender_list(limit=10)

        # Call cleanup
        hybrid.cleanup()

        # Both should be cleaned up
        mock_api.cleanup.assert_called_once()
        mock_selenium.cleanup.assert_called_once()

    @patch("src.scrapers.hybrid_scraper.APIScraper")
    def test_cleanup_only_api_when_selenium_not_used(self, mock_api_class):
        """Test cleanup when only API scraper was used."""
        mock_api = MagicMock()
        mock_api.scrape_tender_list.return_value = [{"tender_id": "T-007"}]
        mock_api_class.return_value = mock_api

        hybrid = HybridScraper(headless=True)
        hybrid.scrape_tender_list(limit=10)

        # Call cleanup
        hybrid.cleanup()

        # Only API cleanup should be called
        mock_api.cleanup.assert_called_once()
        assert hybrid.selenium_scraper is None
