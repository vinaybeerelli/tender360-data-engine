"""
Unit tests for API Scraper with mocked responses.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from scrapers.api_scraper import APIScraper
from utils.exceptions import ScraperException


class TestAPIScraperSessionManagement:
    """Test session establishment and cookie management."""
    
    @patch('scrapers.api_scraper.requests.Session')
    @patch('scrapers.api_scraper.random_delay')
    def test_session_establishment_success(self, mock_delay, mock_session_class):
        """Test successful session establishment with JSESSIONID."""
        # Setup mock
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response
        
        # Mock cookies as a MagicMock to allow both dict-like and attribute access
        mock_cookies = MagicMock()
        mock_cookies.__contains__ = Mock(return_value=True)
        mock_cookies.get = Mock(return_value='ABC123XYZ')
        mock_session.cookies = mock_cookies
        
        mock_session_class.return_value = mock_session
        
        # Test
        scraper = APIScraper(headless=True)
        
        # Verify
        assert scraper.session is not None
        mock_session.get.assert_called_once()
        assert 'TenderDetailsHome.html' in mock_session.get.call_args[0][0]
    
    @patch('scrapers.api_scraper.requests.Session')
    @patch('scrapers.api_scraper.random_delay')
    def test_session_establishment_failure(self, mock_delay, mock_session_class):
        """Test session establishment handles errors gracefully."""
        # Setup mock to raise exception
        mock_session = Mock()
        mock_session.get.side_effect = Exception("Connection failed")
        mock_session_class.return_value = mock_session
        
        # Test - should raise ScraperException
        with pytest.raises(ScraperException, match="Connection failed"):
            APIScraper(headless=True)


class TestAPIScraperTenderList:
    """Test tender list scraping functionality."""
    
    @patch('scrapers.api_scraper.requests.Session')
    @patch('scrapers.api_scraper.random_delay')
    def test_scrape_tender_list_success(self, mock_delay, mock_session_class):
        """Test successful tender list scraping."""
        # Setup mock session
        mock_session = Mock()
        
        # Mock session establishment
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_get_response
        
        mock_cookies = MagicMock()
        mock_cookies.__contains__ = Mock(return_value=True)
        mock_cookies.get = Mock(return_value='test123')
        mock_session.cookies = mock_cookies
        
        # Mock API response with sample data
        mock_api_response = Mock()
        mock_api_response.status_code = 200
        mock_api_response.raise_for_status = Mock()
        mock_api_response.json.return_value = {
            'aaData': [
                [
                    'Department 1',
                    'Notice-001',
                    'Category A',
                    'Construction Work 1',
                    'Rs. 10,00,000',
                    '01-01-2024',
                    '05-01-2024',
                    '10-01-2024',
                    'TENDER-001',
                    '<a href="#" onclick="GetTenderInfo(\'param1\',\'param2\',\'param3\')">View</a>'
                ],
                [
                    'Department 2',
                    'Notice-002',
                    'Category B',
                    'Road Work 2',
                    'Rs. 20,00,000',
                    '02-01-2024',
                    '06-01-2024',
                    '11-01-2024',
                    'TENDER-002',
                    '<a href="#">View</a>'
                ]
            ],
            'iTotalRecords': 2
        }
        mock_session.post.return_value = mock_api_response
        
        mock_session_class.return_value = mock_session
        
        # Test
        scraper = APIScraper(headless=True)
        tenders = scraper.scrape_tender_list(limit=10)
        
        # Verify
        assert len(tenders) == 2
        assert tenders[0]['notice_number'] == 'Notice-001'
        assert tenders[0]['work_name'] == 'Construction Work 1'
        assert tenders[0]['tender_id'] == 'TENDER-001'
        assert 'onclick_param1' in tenders[0]  # onclick params extracted
        
        # Verify API was called with correct parameters
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        assert 'TenderDetailsHomeJson.html' in call_args[0][0]
    
    @patch('scrapers.api_scraper.requests.Session')
    @patch('scrapers.api_scraper.random_delay')
    def test_scrape_tender_list_403_error(self, mock_delay, mock_session_class):
        """Test handling of 403 Forbidden error."""
        # Setup mock
        mock_session = Mock()
        
        # Mock session establishment
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_get_response
        
        mock_cookies = MagicMock()
        mock_cookies.__contains__ = Mock(return_value=True)
        mock_cookies.get = Mock(return_value='test123')
        mock_session.cookies = mock_cookies
        
        # Mock API response with 403
        mock_api_response = Mock()
        mock_api_response.status_code = 403
        mock_session.post.return_value = mock_api_response
        
        mock_session_class.return_value = mock_session
        
        # Test - should raise RetryException after multiple attempts
        scraper = APIScraper(headless=True)
        with pytest.raises(Exception):  # Will raise RetryException or ScraperException
            scraper.scrape_tender_list(limit=10)
    
    @patch('scrapers.api_scraper.requests.Session')
    @patch('scrapers.api_scraper.random_delay')
    def test_scrape_tender_list_empty_response(self, mock_delay, mock_session_class):
        """Test handling of empty tender list."""
        # Setup mock
        mock_session = Mock()
        
        # Mock session establishment
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_get_response
        
        mock_cookies = MagicMock()
        mock_cookies.__contains__ = Mock(return_value=True)
        mock_cookies.get = Mock(return_value='test123')
        mock_session.cookies = mock_cookies
        
        # Mock empty API response
        mock_api_response = Mock()
        mock_api_response.status_code = 200
        mock_api_response.raise_for_status = Mock()
        mock_api_response.json.return_value = {'aaData': []}
        mock_session.post.return_value = mock_api_response
        
        mock_session_class.return_value = mock_session
        
        # Test
        scraper = APIScraper(headless=True)
        tenders = scraper.scrape_tender_list(limit=10)
        
        # Verify
        assert len(tenders) == 0


class TestAPIScraperDataParsing:
    """Test data parsing and extraction."""
    
    @patch('scrapers.api_scraper.requests.Session')
    @patch('scrapers.api_scraper.random_delay')
    def test_parse_tender_row_with_html(self, mock_delay, mock_session_class):
        """Test parsing of tender row with HTML content."""
        # Setup mock
        mock_session = Mock()
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_get_response
        
        mock_cookies = MagicMock()
        mock_cookies.__contains__ = Mock(return_value=True)
        mock_cookies.get = Mock(return_value='test123')
        mock_session.cookies = mock_cookies
        mock_session_class.return_value = mock_session
        
        scraper = APIScraper(headless=True)
        
        # Test row with HTML tags
        row = [
            '<div>Department Name</div>',
            '<b>Notice-001</b>',
            'Category A',
            '<span>Work Name with <i>HTML</i></span>',
            'Rs. 10,00,000',
            '01-01-2024',
            '05-01-2024',
            '10-01-2024',
            'TENDER-001',
            '<a href="#">View</a>'
        ]
        
        tender = scraper._parse_tender_row(row, 0)
        
        # Verify HTML is cleaned
        assert tender['department'] == 'Department Name'
        assert tender['notice_number'] == 'Notice-001'
        assert tender['work_name'] == 'Work Name with HTML'
    
    @patch('scrapers.api_scraper.requests.Session')
    @patch('scrapers.api_scraper.random_delay')
    def test_extract_onclick_params(self, mock_delay, mock_session_class):
        """Test extraction of onclick parameters."""
        # Setup mock
        mock_session = Mock()
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_get_response
        
        mock_cookies = MagicMock()
        mock_cookies.__contains__ = Mock(return_value=True)
        mock_cookies.get = Mock(return_value='test123')
        mock_session.cookies = mock_cookies
        mock_session_class.return_value = mock_session
        
        scraper = APIScraper(headless=True)
        
        # Test various onclick formats
        test_cases = [
            (
                "<a onclick=\"GetTenderInfo('param1','param2','param3')\">View</a>",
                {'onclick_param1': 'param1', 'onclick_param2': 'param2', 'onclick_param3': 'param3'}
            ),
            (
                '<a onclick="GetTenderInfo(\'abc\',\'def\',\'xyz\')">View</a>',
                {'onclick_param1': 'abc', 'onclick_param2': 'def', 'onclick_param3': 'xyz'}
            ),
            (
                '<a href="#">View</a>',  # No onclick
                {}
            ),
        ]
        
        for html, expected in test_cases:
            result = scraper._extract_onclick_params(html)
            assert result == expected


class TestAPIScraperLimitHandling:
    """Test limit parameter handling."""
    
    @patch('scrapers.api_scraper.requests.Session')
    @patch('scrapers.api_scraper.random_delay')
    def test_scrape_with_limit(self, mock_delay, mock_session_class):
        """Test that limit parameter is respected."""
        # Setup mock
        mock_session = Mock()
        
        # Mock session establishment
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_get_response
        
        mock_cookies = MagicMock()
        mock_cookies.__contains__ = Mock(return_value=True)
        mock_cookies.get = Mock(return_value='test123')
        mock_session.cookies = mock_cookies
        
        # Create 100 tenders
        tender_data = []
        for i in range(100):
            tender_data.append([
                f'Department {i}',
                f'Notice-{i:03d}',
                'Category A',
                f'Work {i}',
                'Rs. 10,00,000',
                '01-01-2024',
                '05-01-2024',
                '10-01-2024',
                f'TENDER-{i:03d}',
                '<a href="#">View</a>'
            ])
        
        mock_api_response = Mock()
        mock_api_response.status_code = 200
        mock_api_response.raise_for_status = Mock()
        mock_api_response.json.return_value = {
            'aaData': tender_data,
            'iTotalRecords': 100
        }
        mock_session.post.return_value = mock_api_response
        
        mock_session_class.return_value = mock_session
        
        # Test with limit=50
        scraper = APIScraper(headless=True)
        tenders = scraper.scrape_tender_list(limit=50)
        
        # Verify
        assert len(tenders) == 50


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
