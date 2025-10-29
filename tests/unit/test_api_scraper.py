"""
Unit tests for APIScraper class
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from src.scrapers.api_scraper import APIScraper


class TestAPIScraper:
    """Test cases for APIScraper class"""
    
    @patch('src.scrapers.api_scraper.requests.Session')
    @patch('src.scrapers.api_scraper.Settings')
    def test_establish_session_success(self, mock_settings, mock_session_class):
        """Test successful session establishment"""
        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response
        mock_session.cookies = {'JSESSIONID': 'test-session-id-123'}
        
        mock_settings_instance = Mock()
        mock_settings_instance.BASE_URL = "https://tender.telangana.gov.in"
        mock_settings_instance.REQUEST_TIMEOUT = 30
        mock_settings.return_value = mock_settings_instance
        
        # Create scraper (which calls _establish_session in __init__)
        scraper = APIScraper()
        
        # Verify session was created
        assert scraper.session is not None
        
        # Verify main page was visited
        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args
        assert '/TenderDetailsHome.html' in call_args[0][0]
        
        # Verify timeout was set
        assert call_args[1]['timeout'] == 30
        
        # Verify headers were set
        headers = call_args[1]['headers']
        assert 'User-Agent' in headers
        assert 'Accept' in headers
        assert 'Accept-Language' in headers
    
    @patch('src.scrapers.api_scraper.requests.Session')
    @patch('src.scrapers.api_scraper.Settings')
    def test_establish_session_failure(self, mock_settings, mock_session_class):
        """Test session establishment failure"""
        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Simulate request failure
        mock_session.get.side_effect = requests.exceptions.RequestException("Connection error")
        
        mock_settings_instance = Mock()
        mock_settings_instance.BASE_URL = "https://tender.telangana.gov.in"
        mock_settings_instance.REQUEST_TIMEOUT = 30
        mock_settings.return_value = mock_settings_instance
        
        # Creating scraper should raise exception
        with pytest.raises(requests.exceptions.RequestException):
            APIScraper()
    
    @patch('src.scrapers.api_scraper.requests.Session')
    @patch('src.scrapers.api_scraper.Settings')
    def test_establish_session_no_cookie(self, mock_settings, mock_session_class):
        """Test session establishment without JSESSIONID cookie"""
        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response
        mock_session.cookies = {}  # No JSESSIONID cookie
        
        mock_settings_instance = Mock()
        mock_settings_instance.BASE_URL = "https://tender.telangana.gov.in"
        mock_settings_instance.REQUEST_TIMEOUT = 30
        mock_settings.return_value = mock_settings_instance
        
        # Should not raise exception, just log warning
        scraper = APIScraper()
        
        # Verify session was still created
        assert scraper.session is not None
    
    @patch('src.scrapers.api_scraper.requests.Session')
    @patch('src.scrapers.api_scraper.Settings')
    def test_cleanup(self, mock_settings, mock_session_class):
        """Test session cleanup"""
        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response
        mock_session.cookies = {'JSESSIONID': 'test-session-id-123'}
        
        mock_settings_instance = Mock()
        mock_settings_instance.BASE_URL = "https://tender.telangana.gov.in"
        mock_settings_instance.REQUEST_TIMEOUT = 30
        mock_settings.return_value = mock_settings_instance
        
        # Create and cleanup scraper
        scraper = APIScraper()
        scraper.cleanup()
        
        # Verify session.close() was called
        mock_session.close.assert_called_once()
