#!/usr/bin/env python3
"""
Test script for validating API scraper with 100 tenders on AWS Mumbai.

Usage:
    python scripts/test_100_tenders.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from scrapers.api_scraper import APIScraper
from utils.logger import setup_logger
from utils.exceptions import ScraperException


def test_100_tenders():
    """
    Test scraper with 100 tenders and validate success rate.
    
    Success criteria:
    - Session establishment succeeds
    - No 403 errors
    - Tenders are returned
    - Success rate >= 90%
    """
    # Setup logging
    logger = setup_logger(log_level='INFO')
    
    logger.info("="*80)
    logger.info("TESTING: 100 Tenders on AWS Mumbai")
    logger.info("="*80)
    
    try:
        # Initialize scraper
        logger.info("Step 1: Initializing API scraper...")
        scraper = APIScraper(headless=True)
        logger.info("✓ Scraper initialized successfully")
        
        # Test with 100 tenders
        logger.info("Step 2: Scraping 100 tenders...")
        tenders = scraper.scrape_tender_list(limit=100)
        
        if not tenders:
            logger.error("✗ No tenders returned")
            return False
        
        logger.info(f"✓ Scraped {len(tenders)} tenders")
        
        # Validate data quality
        logger.info("Step 3: Validating data quality...")
        valid_tenders = 0
        
        for tender in tenders:
            # Check required fields
            required_fields = ['notice_number', 'work_name', 'tender_id']
            has_required = all(tender.get(field) for field in required_fields)
            
            if has_required:
                valid_tenders += 1
        
        success_rate = (valid_tenders / len(tenders)) * 100
        logger.info(f"Valid tenders: {valid_tenders}/{len(tenders)}")
        logger.info(f"Success rate: {success_rate:.2f}%")
        
        # Check success criteria
        if success_rate >= 90:
            logger.info("✓ SUCCESS: Achieved 90%+ success rate")
            
            # Print sample tenders
            logger.info("\nSample tenders:")
            for i, tender in enumerate(tenders[:5]):
                logger.info(f"  {i+1}. {tender.get('notice_number')} - {tender.get('work_name', '')[:60]}")
            
            return True
        else:
            logger.error(f"✗ FAILED: Success rate {success_rate:.2f}% is below 90%")
            return False
            
    except ScraperException as e:
        logger.error(f"✗ Scraping error: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}", exc_info=True)
        return False
    finally:
        # Cleanup
        if 'scraper' in locals():
            scraper.cleanup()
    
    logger.info("="*80)


def main():
    """Main execution."""
    success = test_100_tenders()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
