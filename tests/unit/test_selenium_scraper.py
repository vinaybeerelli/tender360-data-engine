"""
Unit tests for Selenium Scraper
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from src.scrapers.selenium_scraper import SeleniumScraper
from src.utils.exceptions import ScraperException


@pytest.fixture
def mock_driver():
    """Create a mock Chrome driver."""
    driver = MagicMock()
    driver.current_window_handle = "main_window"
    driver.window_handles = ["main_window"]
    return driver


@pytest.fixture
def selenium_scraper(mock_driver):
    """Create a Selenium scraper with mocked driver."""
    with patch("src.scrapers.selenium_scraper.uc.Chrome") as mock_chrome:
        mock_chrome.return_value = mock_driver
        scraper = SeleniumScraper(headless=True)
        scraper.driver = mock_driver
        return scraper


class TestSeleniumScraperInit:
    """Tests for SeleniumScraper initialization."""

    @patch("src.scrapers.selenium_scraper.uc.Chrome")
    def test_init_creates_driver(self, mock_chrome):
        """Test that initialization creates Chrome driver."""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        scraper = SeleniumScraper(headless=True)

        assert scraper.driver is not None
        assert scraper.headless is True
        mock_chrome.assert_called_once()

    @patch("src.scrapers.selenium_scraper.uc.Chrome")
    def test_init_with_headless_false(self, mock_chrome):
        """Test initialization with headless=False."""
        scraper = SeleniumScraper(headless=False)

        assert scraper.headless is False
        mock_chrome.assert_called_once()

    @patch("src.scrapers.selenium_scraper.uc.Chrome")
    def test_init_creates_screenshot_directory(self, mock_chrome):
        """Test that screenshot directory is created."""
        scraper = SeleniumScraper(headless=True)

        assert scraper.screenshot_dir.exists()

    @patch("src.scrapers.selenium_scraper.uc.Chrome")
    def test_init_driver_failure(self, mock_chrome):
        """Test handling of driver initialization failure."""
        mock_chrome.side_effect = Exception("Chrome not found")

        with pytest.raises(ScraperException, match="Chrome driver initialization failed"):
            SeleniumScraper(headless=True)


class TestSeleniumScraperHelpers:
    """Tests for helper methods."""

    def test_human_delay(self, selenium_scraper):
        """Test that human delay works."""
        with patch("time.sleep") as mock_sleep:
            selenium_scraper._human_delay(1.0, 2.0)

            mock_sleep.assert_called_once()
            delay = mock_sleep.call_args[0][0]
            assert 1.0 <= delay <= 2.0

    def test_take_screenshot_success(self, selenium_scraper):
        """Test successful screenshot capture."""
        selenium_scraper.driver.save_screenshot = Mock()

        selenium_scraper._take_screenshot("test")

        selenium_scraper.driver.save_screenshot.assert_called_once()
        call_args = selenium_scraper.driver.save_screenshot.call_args[0][0]
        assert "test_" in call_args
        assert call_args.endswith(".png")

    def test_take_screenshot_failure(self, selenium_scraper):
        """Test screenshot failure is handled gracefully."""
        selenium_scraper.driver.save_screenshot = Mock(side_effect=Exception("Cannot save"))

        # Should not raise exception
        selenium_scraper._take_screenshot("test")


class TestExtractRowData:
    """Tests for row data extraction."""

    def test_extract_valid_row(self, selenium_scraper):
        """Test extracting data from a valid row."""
        # Create mock cells
        mock_cells = []
        test_data = [
            "Dept Name",
            "NOTICE-123",
            "Category A",
            "Road Work",
            "Rs. 1,00,000",
            "01/01/2024",
            "02/01/2024",
            "15/01/2024",
            "T-2024-001",
            "",  # Actions column
        ]

        for data in test_data:
            cell = MagicMock()
            cell.text = data
            mock_cells.append(cell)

        # Mock detail link in actions column
        mock_link = MagicMock()
        mock_link.get_attribute.return_value = "http://example.com/details"
        mock_cells[9].find_element.return_value = mock_link

        # Create mock row
        mock_row = MagicMock()
        mock_row.find_elements.return_value = mock_cells

        result = selenium_scraper._extract_row_data(mock_row)

        assert result is not None
        assert result["department"] == "Dept Name"
        assert result["notice_number"] == "NOTICE-123"
        assert result["tender_id"] == "T-2024-001"
        assert result["detail_url"] == "http://example.com/details"
        assert "scraped_at" in result

    def test_extract_row_insufficient_cells(self, selenium_scraper):
        """Test handling of row with insufficient cells."""
        mock_row = MagicMock()
        mock_row.find_elements.return_value = [MagicMock()] * 5  # Only 5 cells

        result = selenium_scraper._extract_row_data(mock_row)

        assert result is None

    def test_extract_row_no_detail_link(self, selenium_scraper):
        """Test row without detail link."""
        from selenium.common.exceptions import NoSuchElementException

        mock_cells = [MagicMock(text=f"Data {i}") for i in range(10)]
        mock_cells[9].find_element.side_effect = NoSuchElementException()

        mock_row = MagicMock()
        mock_row.find_elements.return_value = mock_cells

        result = selenium_scraper._extract_row_data(mock_row)

        assert result is not None
        assert result["detail_url"] == ""


class TestScrapeTenderList:
    """Tests for scraping tender list."""

    @patch("src.scrapers.selenium_scraper.WebDriverWait")
    def test_scrape_tender_list_success(self, mock_wait, selenium_scraper):
        """Test successful tender list scraping."""
        # Mock page load and data wait
        mock_wait.return_value.until.return_value = True

        # Create mock rows with data
        mock_cells = [MagicMock(text=f"Data {i}") for i in range(10)]
        mock_link = MagicMock()
        mock_link.get_attribute.return_value = "http://example.com/details"
        mock_cells[9].find_element.return_value = mock_link

        mock_row = MagicMock()
        mock_row.find_elements.return_value = mock_cells

        selenium_scraper.driver.find_elements.return_value = [mock_row, mock_row]
        selenium_scraper._wait_for_data_rows = Mock(return_value=True)

        with patch("time.sleep"):
            result = selenium_scraper.scrape_tender_list(limit=2)

        assert len(result) == 2
        assert all("scraped_at" in tender for tender in result)

    def test_scrape_tender_list_no_data(self, selenium_scraper):
        """Test handling of no data scenario."""
        selenium_scraper._wait_for_data_rows = Mock(return_value=False)

        with pytest.raises(ScraperException, match="Failed to load tender data"):
            selenium_scraper.scrape_tender_list()

    def test_scrape_tender_list_with_limit(self, selenium_scraper):
        """Test scraping with limit parameter."""
        selenium_scraper._wait_for_data_rows = Mock(return_value=True)

        # Create 10 mock rows
        mock_rows = []
        for i in range(10):
            mock_cells = [MagicMock(text=f"Data {i}-{j}") for j in range(10)]
            mock_link = MagicMock()
            mock_link.get_attribute.return_value = f"http://example.com/details/{i}"
            mock_cells[9].find_element.return_value = mock_link

            mock_row = MagicMock()
            mock_row.find_elements.return_value = mock_cells
            mock_rows.append(mock_row)

        selenium_scraper.driver.find_elements.return_value = mock_rows

        with patch("time.sleep"):
            result = selenium_scraper.scrape_tender_list(limit=5)

        assert len(result) == 5

    def test_scrape_tender_list_webdriver_error(self, selenium_scraper):
        """Test handling of WebDriver errors."""
        from selenium.common.exceptions import WebDriverException

        selenium_scraper.driver.get.side_effect = WebDriverException("Connection failed")

        with pytest.raises(ScraperException, match="WebDriver error"):
            selenium_scraper.scrape_tender_list()


class TestScrapeTenderDetails:
    """Tests for scraping tender details."""

    def test_scrape_details_window_switch(self, selenium_scraper):
        """Test window switching for detail page."""
        # Mock finding detail link
        mock_link = MagicMock()
        selenium_scraper.driver.find_element.return_value = mock_link

        # Mock window handles
        selenium_scraper.driver.window_handles = ["main", "detail"]

        with patch("src.scrapers.selenium_scraper.WebDriverWait"), patch("time.sleep"):
            result = selenium_scraper.scrape_tender_details("T-2024-001")

        assert result["tender_id"] == "T-2024-001"
        assert "scraped_at" in result
        mock_link.click.assert_called_once()
        selenium_scraper.driver.switch_to.window.assert_called()
        selenium_scraper.driver.close.assert_called_once()

    def test_scrape_details_no_link_found(self, selenium_scraper):
        """Test handling when detail link not found."""
        from selenium.common.exceptions import NoSuchElementException

        selenium_scraper.driver.find_element.side_effect = NoSuchElementException()

        result = selenium_scraper.scrape_tender_details("T-2024-001")

        assert result == {}


class TestExtractDocumentUrls:
    """Tests for extracting document URLs."""

    def test_extract_document_urls_success(self, selenium_scraper):
        """Test successful document URL extraction."""
        # Create mock links
        mock_links = []
        urls = ["http://example.com/doc1.pdf", "http://example.com/doc2.doc", "http://example.com/doc3.xls"]

        for url in urls:
            link = MagicMock()
            link.get_attribute.return_value = url
            mock_links.append(link)

        selenium_scraper.driver.find_elements.return_value = mock_links

        result = selenium_scraper.extract_document_urls("T-2024-001")

        assert len(result) == 3
        assert result == urls

    def test_extract_document_urls_no_docs(self, selenium_scraper):
        """Test when no documents are found."""
        selenium_scraper.driver.find_elements.return_value = []

        result = selenium_scraper.extract_document_urls("T-2024-001")

        assert result == []

    def test_extract_document_urls_error(self, selenium_scraper):
        """Test error handling during URL extraction."""
        selenium_scraper.driver.find_elements.side_effect = Exception("Page not loaded")

        result = selenium_scraper.extract_document_urls("T-2024-001")

        assert result == []


class TestCleanup:
    """Tests for cleanup operations."""

    def test_cleanup_success(self, selenium_scraper):
        """Test successful cleanup."""
        selenium_scraper.cleanup()

        selenium_scraper.driver.quit.assert_called_once()

    def test_cleanup_with_error(self, selenium_scraper):
        """Test cleanup handles errors gracefully."""
        selenium_scraper.driver.quit.side_effect = Exception("Cannot quit")

        # Should not raise exception
        selenium_scraper.cleanup()

    def test_cleanup_no_driver(self):
        """Test cleanup when driver is None."""
        with patch("src.scrapers.selenium_scraper.uc.Chrome"):
            scraper = SeleniumScraper(headless=True)
            scraper.driver = None

            # Should not raise exception
            scraper.cleanup()


class TestWaitForDataRows:
    """Tests for waiting for data to load."""

    @patch("src.scrapers.selenium_scraper.WebDriverWait")
    def test_wait_for_data_rows_success(self, mock_wait, selenium_scraper):
        """Test successful wait for data rows."""
        # Mock table found
        mock_wait.return_value.until.return_value = True

        # Mock data rows found
        mock_rows = [MagicMock() for _ in range(5)]
        selenium_scraper.driver.find_elements.return_value = mock_rows

        result = selenium_scraper._wait_for_data_rows(timeout=30)

        assert result is True

    @patch("src.scrapers.selenium_scraper.WebDriverWait")
    def test_wait_for_data_rows_timeout(self, mock_wait, selenium_scraper):
        """Test timeout waiting for data rows."""
        from selenium.common.exceptions import TimeoutException

        mock_wait.return_value.until.side_effect = TimeoutException()

        result = selenium_scraper._wait_for_data_rows(timeout=10)

        assert result is False
        # Should take screenshot on failure
        selenium_scraper.driver.save_screenshot.assert_called()
