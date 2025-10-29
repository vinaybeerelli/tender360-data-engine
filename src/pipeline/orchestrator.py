"""
Pipeline orchestrator - Coordinates complete workflow
This module will be implemented in Issue #8
"""

from typing import Optional
from sqlalchemy.orm import Session

from src.scrapers.api_scraper import APIScraper
from src.scrapers.selenium_scraper import SeleniumScraper
from src.scrapers.hybrid_scraper import HybridScraper
from src.services.downloader import DocumentDownloader
from src.services.parser import DocumentParser
from src.database import operations as db_ops
from src.utils.logger import log


class TenderPipeline:
    """
    Main pipeline orchestrator.
    
    Coordinates the complete workflow:
    1. Scrape tender list
    2. For each tender:
        a. Get details
        b. Extract document URLs
        c. Download documents
        d. Parse documents
        e. Save to database
    3. Generate summary
    """
    
    def __init__(self, db: Session, mode='api', headless=True):
        """
        Initialize pipeline.
        
        Args:
            db: Database session
            mode: Scraping mode (api, selenium, hybrid)
            headless: Run browser in headless mode
        """
        self.db = db
        self.mode = mode
        self.headless = headless
        
        # Initialize services
        self.scraper = self._get_scraper(mode, headless)
        self.downloader = DocumentDownloader()
        self.parser = DocumentParser()
        
        # Stats
        self.stats = {
            'found': 0,
            'scraped': 0,
            'failed': 0,
            'documents_downloaded': 0,
            'documents_parsed': 0
        }
    
    def _get_scraper(self, mode, headless):
        """Get appropriate scraper based on mode."""
        if mode == 'api':
            return APIScraper(headless)
        elif mode == 'selenium':
            return SeleniumScraper(headless)
        elif mode == 'hybrid':
            return HybridScraper(headless)
        else:
            raise ValueError(f"Invalid scraper mode: {mode}")
    
    def run_full_pipeline(self, limit: Optional[int] = None):
        """
        Run complete tender extraction pipeline.
        
        Args:
            limit: Maximum number of tenders to process
        """
        # TODO: Implement in Issue #8
        log.info("="*80)
        log.info("STARTING PIPELINE EXECUTION")
        log.info("="*80)
        
        try:
            # Step 1: Scrape tender list
            log.info(f"Step 1: Scraping tender list (mode={self.mode}, limit={limit})")
            tenders = self.scraper.scrape_tender_list(limit)
            self.stats['found'] = len(tenders)
            log.info(f"Found {len(tenders)} tenders")
            
            # Step 2: Process each tender
            # This will be implemented to:
            # - Get tender details
            # - Save to database
            # - Download documents
            # - Parse documents
            # - Handle errors gracefully
            
            # Step 3: Generate summary
            self._generate_summary()
            
        except Exception as e:
            log.error(f"Pipeline failed: {e}", exc_info=True)
            raise
        finally:
            self.cleanup()
    
    def _generate_summary(self):
        """Generate and log pipeline execution summary."""
        log.info("="*80)
        log.info("PIPELINE SUMMARY")
        log.info("="*80)
        log.info(f"Tenders found: {self.stats['found']}")
        log.info(f"Tenders scraped: {self.stats['scraped']}")
        log.info(f"Tenders failed: {self.stats['failed']}")
        log.info(f"Documents downloaded: {self.stats['documents_downloaded']}")
        log.info(f"Documents parsed: {self.stats['documents_parsed']}")
        
        success_rate = (self.stats['scraped'] / self.stats['found'] * 100) if self.stats['found'] > 0 else 0
        log.info(f"Success rate: {success_rate:.1f}%")
        log.info("="*80)
    
    def cleanup(self):
        """Clean up resources."""
        if self.scraper:
            self.scraper.cleanup()

