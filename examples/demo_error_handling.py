#!/usr/bin/env python
"""
Example demonstrating error handling and retry logic
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.api_scraper import APIScraper
from src.utils.logger import log


def main():
    """Demonstrate error handling and retry logic"""
    
    print("=" * 60)
    print("Error Handling and Retry Logic Demo")
    print("=" * 60)
    print()
    
    # Initialize scraper
    print("1. Initializing API scraper...")
    try:
        scraper = APIScraper()
        print("   ✓ Scraper initialized successfully")
        print(f"   Session: {scraper.session}")
        print()
    except Exception as e:
        print(f"   ✗ Failed to initialize: {e}")
        return 1
    
    # Test scraping tender list
    print("2. Testing scrape_tender_list...")
    try:
        tenders = scraper.scrape_tender_list(limit=5)
        print(f"   ✓ Scraped {len(tenders)} tenders")
        print()
    except Exception as e:
        print(f"   ✗ Failed to scrape: {e}")
        print()
    
    # Test scraping tender details with valid ID
    print("3. Testing scrape_tender_details (valid ID)...")
    try:
        details = scraper.scrape_tender_details("T12345")
        print(f"   ✓ Scraped details: {details}")
        print()
    except Exception as e:
        print(f"   ✗ Failed to scrape: {e}")
        print()
    
    # Test scraping tender details with invalid ID
    print("4. Testing scrape_tender_details (invalid ID)...")
    try:
        details = scraper.scrape_tender_details(None)
        print(f"   ✓ Scraped details: {details}")
        print()
    except Exception as e:
        print(f"   ✓ Correctly caught invalid ID: {type(e).__name__}")
        print()
    
    # Test document URL extraction
    print("5. Testing extract_document_urls...")
    try:
        urls = scraper.extract_document_urls("T12345")
        print(f"   ✓ Extracted {len(urls)} URLs")
        print()
    except Exception as e:
        print(f"   ✗ Failed to extract: {e}")
        print()
    
    # Test cleanup
    print("6. Testing cleanup...")
    try:
        scraper.cleanup()
        print("   ✓ Cleanup successful")
        print()
    except Exception as e:
        print(f"   ✗ Failed to cleanup: {e}")
        print()
    
    print("=" * 60)
    print("Demo completed!")
    print("=" * 60)
    print()
    print("Check logs at: data/logs/scraper.log")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
