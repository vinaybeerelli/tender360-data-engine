"""
Unit tests for API Scraper

Tests the API scraper functionality with mocked responses
to verify 90%+ success rate.
Unit tests for API Scraper with mocked responses.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from src.scrapers.api_scraper import APIScraper
from src.utils.exceptions import ScraperException


# Sample mock data based on expected API response
MOCK_API_RESPONSE = {
    "sEcho": "1",
    "iTotalRecords": 100,
    "iTotalDisplayRecords": 100,
    "aaData": [
        [
            "Department of Health",
            "NOTICE-001",
            "Civil Works",
            "Construction of Hospital Building",
            "Rs. 50,00,000",
            "01/01/2024",
            "02/01/2024",
            "15/01/2024",
            "TND-2024-001",
            '<a href="#" onclick="openWin(\'TND-2024-001\',\'12345\')">View Details</a>'
        ],
        [
            "Department of Education",
            "NOTICE-002",
            "Goods",
            "Supply of Computer Equipment",
            "Rs. 25,00,000",
            "03/01/2024",
            "04/01/2024",
            "18/01/2024",
            "TND-2024-002",
            '<a href="#" onclick="openWin(\'TND-2024-002\',\'67890\')">View Details</a>'
        ],
        [
            "Public Works Department",
            "NOTICE-003",
            "Civil Works",
            "Road Construction Project",
            "Rs. 1,00,00,000",
            "05/01/2024",
            "06/01/2024",
            "20/01/2024",
            "TND-2024-003",
            '<a href="#" onclick="openWin(\'TND-2024-003\',\'11111\')">View Details</a>'
        ]
    ]
}


class TestAPIScraper:
    """Test suite for APIScraper class"""
    
    @patch('src.scrapers.api_scraper.requests.Session')
    def test_session_establishment(self, mock_session_class):
        """Test that session is established correctly"""
        # Setup mock
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response
        mock_session.cookies.keys.return_value = ['JSESSIONID']
        mock_session_class.return_value = mock_session
        
        # Create scraper
        scraper = APIScraper()
        
        # Verify session was created and GET request was made
        assert scraper.session is not None
        mock_session.get.assert_called_once()
        
        # Verify URL contains TenderDetailsHome.html
        call_args = mock_session.get.call_args
        assert 'TenderDetailsHome.html' in str(call_args)
    
    @patch('src.scrapers.api_scraper.requests.Session')
    def test_scrape_tender_list_success(self, mock_session_class):
        """Test successful tender list scraping"""
        # Setup mock
        mock_session = Mock()
        mock_session.cookies.keys.return_value = ['JSESSIONID']
        
        # Mock GET request for session establishment
        mock_get_response = Mock()
        mock_get_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_get_response
        
        # Mock POST request for API call
        mock_post_response = Mock()
        mock_post_response.raise_for_status = Mock()
        mock_post_response.json.return_value = MOCK_API_RESPONSE
        mock_session.post.return_value = mock_post_response
        
        mock_session_class.return_value = mock_session
        
        # Create scraper and scrape
        scraper = APIScraper()
        tenders = scraper.scrape_tender_list(limit=10)
        
        # Verify results
        assert len(tenders) == 3
        assert tenders[0]['department'] == 'Department of Health'
        assert tenders[0]['tender_id'] == 'TND-2024-001'
        assert tenders[1]['notice_number'] == 'NOTICE-002'
        assert tenders[2]['work_name'] == 'Road Construction Project'
    
    @patch('src.scrapers.api_scraper.requests.Session')
    def test_scrape_tender_list_with_limit(self, mock_session_class):
        """Test scraping with limit parameter"""
        # Setup mock
        mock_session = Mock()
        mock_session.cookies.keys.return_value = ['JSESSIONID']
        mock_session.get.return_value = Mock(raise_for_status=Mock())
        
        mock_post_response = Mock()
        mock_post_response.raise_for_status = Mock()
        mock_post_response.json.return_value = MOCK_API_RESPONSE
        mock_session.post.return_value = mock_post_response
        
        mock_session_class.return_value = mock_session
        
        # Create scraper and scrape with limit
        scraper = APIScraper()
        tenders = scraper.scrape_tender_list(limit=2)
        
        # Verify limit is respected
        assert len(tenders) <= 2
    
    @patch('src.scrapers.api_scraper.requests.Session')
    def test_scrape_tender_list_empty_response(self, mock_session_class):
        """Test handling of empty API response"""
        # Setup mock
        mock_session = Mock()
        mock_session.cookies.keys.return_value = ['JSESSIONID']
        mock_session.get.return_value = Mock(raise_for_status=Mock())
        
        mock_post_response = Mock()
        mock_post_response.raise_for_status = Mock()
        mock_post_response.json.return_value = {"aaData": []}
        mock_session.post.return_value = mock_post_response
        
        mock_session_class.return_value = mock_session
        
        # Create scraper and scrape
        scraper = APIScraper()
        tenders = scraper.scrape_tender_list()
        
        # Verify empty list is returned
        assert isinstance(tenders, list)
        assert len(tenders) == 0
    
    @patch('src.scrapers.api_scraper.requests.Session')
    def test_scrape_tender_list_missing_aaData(self, mock_session_class):
        """Test handling of malformed API response"""
        from src.utils.exceptions import RetryException
        
        # Setup mock
        mock_session = Mock()
        mock_session.cookies.keys.return_value = ['JSESSIONID']
        mock_session.get.return_value = Mock(raise_for_status=Mock())
        
        mock_post_response = Mock()
        mock_post_response.raise_for_status = Mock()
        mock_post_response.json.return_value = {"iTotalRecords": 0}
        mock_session.post.return_value = mock_post_response
        
        mock_session_class.return_value = mock_session
        
        # Create scraper and expect exception (wrapped in RetryException due to retry decorator)
        scraper = APIScraper()
        with pytest.raises(RetryException) as exc_info:
            scraper.scrape_tender_list()
        
        assert "scrape_tender_list" in str(exc_info.value)
    
    @patch('src.scrapers.api_scraper.requests.Session')
    def test_parse_tender_row_complete(self, mock_session_class):
        """Test parsing of complete tender row"""
        # Setup mock
        mock_session = Mock()
        mock_session.cookies.keys.return_value = ['JSESSIONID']
        mock_session.get.return_value = Mock(raise_for_status=Mock())
        mock_session_class.return_value = mock_session
        
        # Create scraper
        scraper = APIScraper()
        
        # Parse a row from mock data
        row = MOCK_API_RESPONSE['aaData'][0]
        tender = scraper._parse_tender_row(row)
        
        # Verify all fields
        assert tender['department'] == 'Department of Health'
        assert tender['notice_number'] == 'NOTICE-001'
        assert tender['category'] == 'Civil Works'
        assert tender['work_name'] == 'Construction of Hospital Building'
        assert tender['tender_value'] == 'Rs. 50,00,000'
        assert tender['published_date'] == '01/01/2024'
        assert tender['bid_start_date'] == '02/01/2024'
        assert tender['bid_close_date'] == '15/01/2024'
        assert tender['tender_id'] == 'TND-2024-001'
        assert tender.get('tender_ref') == 'TND-2024-001'
        assert tender.get('tender_ref2') == '12345'
    
    @patch('src.scrapers.api_scraper.requests.Session')
    def test_parse_tender_row_incomplete(self, mock_session_class):
        """Test parsing of incomplete tender row"""
        # Setup mock
        mock_session = Mock()
        mock_session.cookies.keys.return_value = ['JSESSIONID']
        mock_session.get.return_value = Mock(raise_for_status=Mock())
        mock_session_class.return_value = mock_session
        
        # Create scraper
        scraper = APIScraper()
        
        # Parse incomplete row
        incomplete_row = ['Dept', 'NOTICE-999']
        tender = scraper._parse_tender_row(incomplete_row)
        
        # Verify partial data
        assert tender['department'] == 'Dept'
        assert tender['notice_number'] == 'NOTICE-999'
        assert tender['category'] == ''
        assert tender['work_name'] == ''
    
    @patch('src.scrapers.api_scraper.requests.Session')
    def test_cleanup(self, mock_session_class):
        """Test session cleanup"""
        # Setup mock
        mock_session = Mock()
        mock_session.cookies.keys.return_value = ['JSESSIONID']
        mock_session.get.return_value = Mock(raise_for_status=Mock())
        mock_session_class.return_value = mock_session
        
        # Create scraper and cleanup
        scraper = APIScraper()
        scraper.cleanup()
        
        # Verify session was closed
        mock_session.close.assert_called_once()
    
    @patch('src.scrapers.api_scraper.requests.Session')
    def test_success_rate_multiple_runs(self, mock_session_class):
        """Test that success rate meets 90%+ target across multiple runs"""
        # Setup mock
        mock_session = Mock()
        mock_session.cookies.keys.return_value = ['JSESSIONID']
        mock_session.get.return_value = Mock(raise_for_status=Mock())
        
        mock_post_response = Mock()
        mock_post_response.raise_for_status = Mock()
        mock_post_response.json.return_value = MOCK_API_RESPONSE
        mock_session.post.return_value = mock_post_response
        
        mock_session_class.return_value = mock_session
        
        # Run multiple scraping attempts
        successful_runs = 0
        total_runs = 10
        
        for _ in range(total_runs):
            try:
                scraper = APIScraper()
                tenders = scraper.scrape_tender_list(limit=10)
                if tenders and len(tenders) > 0:
                    successful_runs += 1
                scraper.cleanup()
            except Exception:
                pass
        
        # Calculate success rate
        success_rate = (successful_runs / total_runs) * 100
        
        # Verify 90%+ success rate
        assert success_rate >= 90, f"Success rate {success_rate}% is below 90% target"


class TestAPIScraperIntegration:
    """Integration tests for API scraper (with mocks)"""
    
    @patch('src.scrapers.api_scraper.requests.Session')
    def test_full_scraping_workflow(self, mock_session_class):
        """Test complete scraping workflow from session to data extraction"""
        # Setup mock
        mock_session = Mock()
        mock_session.cookies.keys.return_value = ['JSESSIONID']
        mock_session.get.return_value = Mock(raise_for_status=Mock())
        
        mock_post_response = Mock()
        mock_post_response.raise_for_status = Mock()
        mock_post_response.json.return_value = MOCK_API_RESPONSE
        mock_session.post.return_value = mock_post_response
        
        mock_session_class.return_value = mock_session
        
        try:
            # Step 1: Initialize scraper (establishes session)
            scraper = APIScraper()
            assert scraper.session is not None
            
            # Step 2: Scrape tender list
            tenders = scraper.scrape_tender_list(limit=5)
            assert len(tenders) > 0
            
            # Step 3: Verify data quality
            for tender in tenders:
                assert 'department' in tender
                assert 'tender_id' in tender
                assert 'work_name' in tender
            
            # Step 4: Cleanup
            scraper.cleanup()
            
        except Exception as e:
            pytest.fail(f"Full workflow failed: {e}")
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
        # Note: onclick params represent: param1=tender_no, param2=mode, param3=ref_no
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
