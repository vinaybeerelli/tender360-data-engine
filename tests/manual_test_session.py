"""
Manual test script to verify session establishment works with real website
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.scrapers.api_scraper import APIScraper
from src.utils.logger import setup_logger


def test_session_establishment():
    """Test that session establishment works with the real website"""
    logger = setup_logger(log_level='INFO')
    
    logger.info("=" * 80)
    logger.info("MANUAL TEST: Session Establishment")
    logger.info("=" * 80)
    
    try:
        # Create scraper instance (which establishes session)
        logger.info("Creating APIScraper instance...")
        scraper = APIScraper()
        
        # Check if session exists
        if scraper.session is None:
            logger.error("❌ FAILED: Session is None")
            return False
        
        logger.info("✓ Session object created")
        
        # Check if cookies exist
        if not scraper.session.cookies:
            logger.error("❌ FAILED: No cookies found in session")
            return False
        
        logger.info(f"✓ Cookies found: {list(scraper.session.cookies.keys())}")
        
        # Check for JSESSIONID specifically
        if 'JSESSIONID' in scraper.session.cookies:
            cookie_value = scraper.session.cookies['JSESSIONID']
            logger.info(f"✓ JSESSIONID cookie present: {cookie_value[:20]}...")
        else:
            logger.warning("⚠ JSESSIONID cookie not found (may not be required)")
        
        # Cleanup
        scraper.cleanup()
        logger.info("✓ Cleanup completed")
        
        logger.info("=" * 80)
        logger.info("✅ SESSION ESTABLISHMENT TEST PASSED")
        logger.info("=" * 80)
        return True
        
    except Exception as e:
        logger.error(f"❌ FAILED: {e}", exc_info=True)
        logger.info("=" * 80)
        logger.info("❌ SESSION ESTABLISHMENT TEST FAILED")
        logger.info("=" * 80)
        return False


if __name__ == '__main__':
    success = test_session_establishment()
    sys.exit(0 if success else 1)
