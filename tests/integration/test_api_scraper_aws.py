"""
Integration test for API Scraper on AWS Mumbai.

This test should be run on AWS Mumbai EC2 instance to verify:
- Session establishment works correctly
- No 403 errors occur
- Tender data is scraped successfully
- Success rate >= 90%

Usage:
    pytest tests/integration/test_api_scraper_aws.py -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from scrapers.api_scraper import APIScraper
from utils.exceptions import ScraperException


@pytest.mark.integration
@pytest.mark.requires_aws
class TestAPIScraperAWSMumbai:
    """Integration tests for AWS Mumbai deployment."""
    
    def test_session_establishment(self):
        """Test that session can be established from AWS Mumbai."""
        scraper = APIScraper(headless=True)
        
        assert scraper.session is not None, "Session should be established"
        assert 'JSESSIONID' in scraper.session.cookies or len(scraper.session.cookies) > 0, \
            "Session should have cookies"
        
        scraper.cleanup()
    
    def test_scrape_10_tenders(self):
        """Test scraping 10 tenders as a quick smoke test."""
        scraper = APIScraper(headless=True)
        
        try:
            tenders = scraper.scrape_tender_list(limit=10)
            
            assert len(tenders) > 0, "Should return at least some tenders"
            assert len(tenders) <= 10, "Should not exceed limit"
            
            # Verify tender structure
            for tender in tenders:
                assert 'notice_number' in tender, "Tender should have notice_number"
                assert 'work_name' in tender, "Tender should have work_name"
                assert 'tender_id' in tender, "Tender should have tender_id"
                
        finally:
            scraper.cleanup()
    
    def test_scrape_100_tenders_success_rate(self):
        """
        Test scraping 100 tenders and verify success rate >= 90%.
        
        This is the main acceptance test for Issue #1.
        """
        scraper = APIScraper(headless=True)
        
        try:
            # Scrape 100 tenders
            tenders = scraper.scrape_tender_list(limit=100)
            
            assert len(tenders) > 0, "Should return tenders"
            
            # Count valid tenders
            valid_tenders = 0
            for tender in tenders:
                # Check required fields
                has_notice = bool(tender.get('notice_number'))
                has_work_name = bool(tender.get('work_name'))
                has_tender_id = bool(tender.get('tender_id'))
                
                if has_notice and has_work_name and has_tender_id:
                    valid_tenders += 1
            
            # Calculate success rate
            success_rate = (valid_tenders / len(tenders)) * 100
            
            print(f"\nResults:")
            print(f"  Total tenders: {len(tenders)}")
            print(f"  Valid tenders: {valid_tenders}")
            print(f"  Success rate: {success_rate:.2f}%")
            
            # Verify success rate >= 90%
            assert success_rate >= 90, \
                f"Success rate {success_rate:.2f}% is below 90% threshold"
            
            # Print sample tenders
            print("\nSample tenders:")
            for i, tender in enumerate(tenders[:5]):
                print(f"  {i+1}. {tender.get('notice_number')} - {tender.get('work_name', '')[:60]}")
            
        finally:
            scraper.cleanup()
    
    def test_no_403_errors(self):
        """Test that no 403 Forbidden errors occur on AWS Mumbai."""
        scraper = APIScraper(headless=True)
        
        try:
            # This should not raise a 403 error
            tenders = scraper.scrape_tender_list(limit=10)
            
            # If we get here, no 403 error occurred
            assert True, "No 403 error occurred"
            
        except ScraperException as e:
            if '403' in str(e):
                pytest.fail(f"Got 403 Forbidden error: {e}")
            else:
                # Other scraper exceptions are okay for this test
                pass
        finally:
            scraper.cleanup()
    
    def test_data_quality(self):
        """Test that scraped data has good quality."""
        scraper = APIScraper(headless=True)
        
        try:
            tenders = scraper.scrape_tender_list(limit=10)
            
            assert len(tenders) > 0, "Should return tenders"
            
            for tender in tenders:
                # Check all expected fields are present
                expected_fields = [
                    'department', 'notice_number', 'category', 'work_name',
                    'tender_value', 'published_date', 'bid_start_date',
                    'bid_close_date', 'tender_id'
                ]
                
                for field in expected_fields:
                    assert field in tender, f"Tender missing field: {field}"
                
                # Check that fields are not just empty HTML
                assert len(tender['work_name']) > 0, "Work name should not be empty"
                assert len(tender['notice_number']) > 0, "Notice number should not be empty"
                
        finally:
            scraper.cleanup()


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '-s'])
