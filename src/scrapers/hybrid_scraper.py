"""
Hybrid scraper - Automatically switches between API and Selenium
"""

from typing import List, Dict, Optional

from .api_scraper import APIScraper
from .selenium_scraper import SeleniumScraper
from src.utils.logger import log
from src.utils.exceptions import ScraperException


class HybridScraper:
    """
    Hybrid scraper that tries API first, falls back to Selenium.
    """
    
    def __init__(self, headless=True):
        self.headless = headless
        self.api_scraper = APIScraper(headless)
        self.selenium_scraper = None  # Lazy initialization
    
    def scrape_tender_list(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Scrape list of tenders, trying API first.
        
        Args:
            limit: Maximum number of tenders to scrape
            
        Returns:
            List of tender dictionaries
        """
        log.info("Attempting API scraping...")
        
        try:
            tenders = self.api_scraper.scrape_tender_list(limit)
            if tenders:
                log.info(f"API scraping successful: {len(tenders)} tenders")
                return tenders
        except Exception as e:
            log.warning(f"API scraping failed: {e}")
        
        log.info("Falling back to Selenium...")
        
        if not self.selenium_scraper:
            self.selenium_scraper = SeleniumScraper(self.headless)
        
        try:
            tenders = self.selenium_scraper.scrape_tender_list(limit)
            log.info(f"Selenium scraping successful: {len(tenders)} tenders")
            return tenders
        except Exception as e:
            log.error(f"Selenium scraping also failed: {e}")
            raise ScraperException("Both API and Selenium scraping failed")
    
    def cleanup(self):
        """Clean up both scrapers."""
        if self.api_scraper:
            self.api_scraper.cleanup()
        if self.selenium_scraper:
            self.selenium_scraper.cleanup()

