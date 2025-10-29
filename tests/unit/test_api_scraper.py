"""
Unit tests for API Scraper
"""

import pytest
from unittest.mock import Mock, patch

from src.scrapers.api_scraper import APIScraper
from src.utils.exceptions import NetworkException


class TestAPIScraper:
    """Test cases for APIScraper class."""

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_establish_session_success(self, mock_session_class):
        """Test successful session establishment."""
        # Mock session and response
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session.cookies = {"JSESSIONID": "test_session_id_123456"}

        # Create scraper (should establish session in __init__)
        scraper = APIScraper()

        # Verify session was established
        assert scraper.session is not None
        mock_session.get.assert_called_once()

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_establish_session_failure(self, mock_session_class):
        """Test session establishment failure."""
        # Mock session with error response
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 500
        mock_session.get.return_value = mock_response

        # Should raise NetworkException
        with pytest.raises(NetworkException):
            APIScraper()

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_parse_tender_row_valid(self, mock_session_class):
        """Test parsing a valid tender row."""
        # Mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session.cookies = {"JSESSIONID": "test_id"}

        scraper = APIScraper()

        # Mock tender row data
        row = [
            "Department of Roads",
            "NOT-2024-001",
            "Civil",
            "Road Construction Work",
            "10,00,000",
            "01/01/2024",
            "02/01/2024",
            "15/01/2024",
            "T001234567",
            "<a onclick=\"viewDetailTender('T001234567')\">View</a>",
        ]

        tender = scraper._parse_tender_row(row)

        assert tender is not None
        assert tender["tender_id"] == "T001234567"
        assert tender["department"] == "Department of Roads"
        assert tender["work_name"] == "Road Construction Work"
        assert tender["tender_value"] == "10,00,000"

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_parse_tender_row_insufficient_columns(self, mock_session_class):
        """Test parsing a row with insufficient columns."""
        # Mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session.cookies = {"JSESSIONID": "test_id"}

        scraper = APIScraper()

        # Row with only 5 columns (needs 10)
        row = ["Dept", "NOT-001", "Cat", "Work", "Value"]

        tender = scraper._parse_tender_row(row)

        assert tender is None

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_extract_tender_id_from_onclick(self, mock_session_class):
        """Test extracting tender ID from onclick parameter."""
        # Mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session.cookies = {"JSESSIONID": "test_id"}

        scraper = APIScraper()

        # Test various onclick patterns
        test_cases = [
            ("onclick=\"viewDetailTender('T001234567')\"", "T001234567"),
            ("onclick='viewDetailTender(\"T998877665\")'", "T998877665"),
            ("<a onclick=\"viewDetailTender('T111222333')\">View</a>", "T111222333"),
        ]

        for html, expected_id in test_cases:
            result = scraper._extract_tender_id(html)
            assert result == expected_id, f"Failed for: {html}"

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_extract_tender_id_no_match(self, mock_session_class):
        """Test extracting tender ID when no match found."""
        # Mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session.cookies = {"JSESSIONID": "test_id"}

        scraper = APIScraper()

        result = scraper._extract_tender_id("No tender ID here")
        assert result is None

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_clean_html(self, mock_session_class):
        """Test HTML cleaning function."""
        # Mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session.cookies = {"JSESSIONID": "test_id"}

        scraper = APIScraper()

        test_cases = [
            ("<div>Test</div>", "Test"),
            ("Test&nbsp;Value", "Test Value"),
            ("  Multiple   Spaces  ", "Multiple Spaces"),
            ('<a href="#">Link</a> Text', "Link Text"),
            ("&lt;tag&gt;", "<tag>"),
        ]

        for html, expected in test_cases:
            result = scraper._clean_html(html)
            assert result == expected, f"Failed for: {html}"

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_clean_html_empty(self, mock_session_class):
        """Test cleaning empty or None values."""
        # Mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session.cookies = {"JSESSIONID": "test_id"}

        scraper = APIScraper()

        assert scraper._clean_html(None) == ""
        assert scraper._clean_html("") == ""
        assert scraper._clean_html("   ") == ""

    @patch("src.scrapers.api_scraper.random_delay")
    @patch("src.scrapers.api_scraper.requests.Session")
    def test_scrape_tender_list_success(self, mock_session_class, mock_delay):
        """Test successful tender list scraping."""
        # Mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Mock GET response for session establishment
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_session.get.return_value = mock_get_response
        mock_session.cookies = {"JSESSIONID": "test_id"}

        # Mock POST response for API call
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "aaData": [
                [
                    "Dept1",
                    "NOT-001",
                    "Cat1",
                    "Work1",
                    "1000",
                    "01/01/2024",
                    "02/01/2024",
                    "15/01/2024",
                    "T001",
                    "onclick='viewDetailTender(\"T001\")'",
                ],
                [
                    "Dept2",
                    "NOT-002",
                    "Cat2",
                    "Work2",
                    "2000",
                    "01/02/2024",
                    "02/02/2024",
                    "15/02/2024",
                    "T002",
                    "onclick='viewDetailTender(\"T002\")'",
                ],
            ],
            "iTotalRecords": 2,
            "iTotalDisplayRecords": 2,
        }
        mock_session.post.return_value = mock_post_response

        # Create scraper and scrape
        scraper = APIScraper()
        tenders = scraper.scrape_tender_list(limit=10)

        # Verify results
        assert len(tenders) == 2
        assert tenders[0]["tender_id"] == "T001"
        assert tenders[1]["tender_id"] == "T002"

    @patch("src.scrapers.api_scraper.random_delay")
    @patch("src.scrapers.api_scraper.requests.Session")
    def test_scrape_tender_list_403_error(self, mock_session_class, mock_delay):
        """Test handling of 403 Forbidden error."""
        # Mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Mock GET for session
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_session.get.return_value = mock_get_response
        mock_session.cookies = {"JSESSIONID": "test_id"}

        # Mock POST with 403
        mock_post_response = Mock()
        mock_post_response.status_code = 403
        mock_session.post.return_value = mock_post_response

        # Should raise ScraperException after retries
        scraper = APIScraper()
        with pytest.raises(Exception) as exc_info:
            scraper.scrape_tender_list()

        # Either ScraperException or RetryException is acceptable
        assert "403 Forbidden" in str(exc_info.value) or "Max retries" in str(
            exc_info.value
        )

    @patch("src.scrapers.api_scraper.random_delay")
    @patch("src.scrapers.api_scraper.requests.Session")
    def test_scrape_tender_list_missing_aadata(self, mock_session_class, mock_delay):
        """Test handling of response without aaData field."""
        # Mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Mock GET for session
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_session.get.return_value = mock_get_response
        mock_session.cookies = {"JSESSIONID": "test_id"}

        # Mock POST with invalid response
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {"error": "No data"}
        mock_session.post.return_value = mock_post_response

        # Should raise exception after retries
        scraper = APIScraper()
        with pytest.raises(Exception) as exc_info:
            scraper.scrape_tender_list()

        # Either ScraperException or RetryException is acceptable
        assert "aaData" in str(exc_info.value) or "Max retries" in str(exc_info.value)

    @patch("src.scrapers.api_scraper.requests.Session")
    def test_cleanup(self, mock_session_class):
        """Test cleanup closes session."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session.cookies = {"JSESSIONID": "test_id"}

        scraper = APIScraper()
        scraper.cleanup()

        mock_session.close.assert_called_once()
