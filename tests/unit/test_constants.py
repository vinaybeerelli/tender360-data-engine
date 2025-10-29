"""
Unit tests for configuration constants.
"""

import pytest
from config.constants import API_HEADERS, API_PAYLOAD


class TestAPIHeaders:
    """Test API headers configuration."""
    
    def test_api_headers_exist(self):
        """Test that API_HEADERS dictionary exists and is not empty."""
        assert API_HEADERS is not None
        assert len(API_HEADERS) > 0
    
    def test_required_ajax_headers(self):
        """Test that all required AJAX headers are present."""
        required_headers = [
            "Accept",
            "Content-Type",
            "X-Requested-With",
            "User-Agent",
            "Referer",
            "Origin",
        ]
        
        for header in required_headers:
            assert header in API_HEADERS, f"Required header '{header}' is missing"
    
    def test_ajax_header_value(self):
        """Test that X-Requested-With is set to XMLHttpRequest."""
        assert API_HEADERS["X-Requested-With"] == "XMLHttpRequest"
    
    def test_security_headers_present(self):
        """Test that security-related headers are present."""
        security_headers = [
            "Sec-Fetch-Dest",
            "Sec-Fetch-Mode",
            "Sec-Fetch-Site",
        ]
        
        for header in security_headers:
            assert header in API_HEADERS, f"Security header '{header}' is missing"
    
    def test_browser_identification_headers(self):
        """Test that browser identification headers are present."""
        browser_headers = [
            "sec-ch-ua",
            "sec-ch-ua-mobile",
            "sec-ch-ua-platform",
        ]
        
        for header in browser_headers:
            assert header in API_HEADERS, f"Browser header '{header}' is missing"
    
    def test_connection_header(self):
        """Test that Connection header is present."""
        assert "Connection" in API_HEADERS
        assert API_HEADERS["Connection"] == "keep-alive"
    
    def test_host_header(self):
        """Test that Host header is present and correct."""
        assert "Host" in API_HEADERS
        assert API_HEADERS["Host"] == "tender.telangana.gov.in"
    
    def test_content_type_header(self):
        """Test that Content-Type is properly set for form data."""
        assert "Content-Type" in API_HEADERS
        assert "application/x-www-form-urlencoded" in API_HEADERS["Content-Type"]
    
    def test_accept_header(self):
        """Test that Accept header includes JSON."""
        assert "Accept" in API_HEADERS
        assert "application/json" in API_HEADERS["Accept"]


class TestAPIPayload:
    """Test API payload configuration."""
    
    def test_api_payload_exists(self):
        """Test that API_PAYLOAD dictionary exists and is not empty."""
        assert API_PAYLOAD is not None
        assert len(API_PAYLOAD) > 0
    
    def test_datatable_parameters(self):
        """Test that DataTables required parameters are present."""
        required_params = [
            "sEcho",
            "iColumns",
            "iDisplayStart",
            "iDisplayLength",
        ]
        
        for param in required_params:
            assert param in API_PAYLOAD, f"Required parameter '{param}' is missing"
