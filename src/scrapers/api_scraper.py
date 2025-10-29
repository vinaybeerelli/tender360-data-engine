"""
API-based scraper - Primary scraping method
This module will be implemented in Issue #1
"""

from typing import List, Dict, Optional
import requests

from .base_scraper import BaseScraper
from config.constants import API_HEADERS, API_PAYLOAD, TENDER_LIST_API, TENDER_LIST_PAGE
from config.settings import Settings
from src.utils.logger import log
from src.utils.helpers import retry, random_delay


class APIScraper(BaseScraper):
    """
    API-based scraper using AJAX endpoints.
    
    This is the primary scraping method (faster and more reliable).
    """
    
    def __init__(self, headless=True):
        super().__init__(headless)
        self.settings = Settings()
        self.session = None
        self._establish_session()
    
    def _establish_session(self):
        """
        Establish session by visiting main page to get cookies.
        
        IMPORTANT: Must visit main page before calling API endpoint.
        """
        log.info("Establishing session...")
        self.session = requests.Session()
        
        # Visit main page to get JSESSIONID cookie
        try:
            url = self.settings.BASE_URL + TENDER_LIST_PAGE
            log.info(f"Visiting main page: {url}")
            
            response = self.session.get(
                url,
                timeout=self.settings.REQUEST_TIMEOUT,
                headers={
                    "User-Agent": API_HEADERS["User-Agent"],
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": API_HEADERS["Accept-Language"],
                }
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            # Verify session cookie was set
            if 'JSESSIONID' in self.session.cookies:
                log.info(f"Session established successfully. Cookie: JSESSIONID={self.session.cookies['JSESSIONID']}")
            else:
                log.warning("Session established but JSESSIONID cookie not found in response")
                
        except requests.exceptions.RequestException as e:
            log.error(f"Failed to establish session: {e}")
            raise
    
    @retry(max_attempts=3)
    def scrape_tender_list(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Scrape list of tenders using API endpoint.
        
        Args:
            limit: Maximum number of tenders to scrape
            
        Returns:
            List of tender dictionaries
            
        Raises:
            ScraperException: If scraping fails
        """
        # TODO: Implement in Issue #1
        log.info(f"Scraping tender list (limit={limit})...")
        
        # This will be implemented to:
        # 1. POST to API endpoint with proper headers
        # 2. Parse JSON response
        # 3. Extract tender data
        # 4. Return list of tenders
        
        return []
    
    def scrape_tender_details(self, tender_id: str) -> Dict:
        """
        Scrape detailed information for a tender.
        
        Args:
            tender_id: Unique tender identifier
            
        Returns:
            Dictionary with tender details
        """
        # TODO: Implement in Issue #4
        log.info(f"Scraping details for tender: {tender_id}")
        return {}
    
    def extract_document_urls(self, tender_id: str) -> List[str]:
        """
        Extract document download URLs from tender page.
        
        Args:
            tender_id: Unique tender identifier
            
        Returns:
            List of document URLs
        """
        # TODO: Implement in Issue #5
        log.info(f"Extracting document URLs for tender: {tender_id}")
        return []
    
    def cleanup(self):
        """Clean up session."""
        if self.session:
            self.session.close()

