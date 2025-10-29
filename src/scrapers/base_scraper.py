"""
Base scraper class - Abstract interface for all scrapers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""
    
    def __init__(self, headless=True):
        """
        Initialize base scraper.
        
        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self.session = None
    
    @abstractmethod
    def scrape_tender_list(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Scrape list of tenders.
        
        Args:
            limit: Maximum number of tenders to scrape
            
        Returns:
            List of tender dictionaries
        """
        pass
    
    @abstractmethod
    def scrape_tender_details(self, tender_id: str) -> Dict:
        """
        Scrape detailed information for a tender.
        
        Args:
            tender_id: Unique tender identifier
            
        Returns:
            Dictionary with tender details
        """
        pass
    
    @abstractmethod
    def extract_document_urls(self, tender_id: str) -> List[str]:
        """
        Extract document download URLs from tender page.
        
        Args:
            tender_id: Unique tender identifier
            
        Returns:
            List of document URLs
        """
        pass
    
    def cleanup(self):
        """Clean up resources (sessions, browser instances, etc.)."""
        pass

