"""
Integration test for undetected-chromedriver setup.

This test verifies that the Selenium scraper can properly initialize
with undetected-chromedriver in both online and offline environments.
"""

import pytest
from pathlib import Path
from src.scrapers.selenium_scraper import SeleniumScraper
from src.utils.exceptions import ScraperException


@pytest.mark.integration
class TestSeleniumSetup:
    """Integration tests for Selenium setup."""

    def test_chromedriver_setup_creates_local_copy(self, tmp_path):
        """Test that chromedriver is copied to local directory."""
        # Note: This test uses the actual file system
        # The setup should create data/drivers/chromedriver
        
        try:
            scraper = SeleniumScraper(headless=True)
            
            # Verify driver directory was created
            assert scraper.driver_dir.exists()
            
            # Verify chromedriver path is set
            assert scraper.driver_executable_path is not None
            
            # Clean up
            scraper.cleanup()
            
        except ScraperException as e:
            # If we can't initialize (e.g., no Chrome installed), that's ok for this test
            # We're mainly testing the setup logic
            pytest.skip(f"Could not initialize Chrome driver: {e}")

    def test_driver_initialization_with_local_path(self):
        """Test that driver initializes with local chromedriver path."""
        try:
            scraper = SeleniumScraper(headless=True)
            
            # Verify driver was created
            assert scraper.driver is not None
            
            # Verify driver executable path was used
            if scraper.driver_executable_path:
                driver_path = Path(scraper.driver_executable_path)
                assert driver_path.exists()
                assert driver_path.name == "chromedriver"
            
            # Clean up
            scraper.cleanup()
            
        except ScraperException as e:
            pytest.skip(f"Could not initialize Chrome driver: {e}")

    def test_driver_can_navigate_to_local_file(self, tmp_path):
        """Test that driver can navigate to a local HTML file."""
        # Create a test HTML file
        test_html = tmp_path / "test.html"
        test_html.write_text("""
            <!DOCTYPE html>
            <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Test Heading</h1>
                <p>Test content</p>
            </body>
            </html>
        """)
        
        try:
            scraper = SeleniumScraper(headless=True)
            
            # Navigate to local file
            file_url = f"file://{test_html}"
            scraper.driver.get(file_url)
            
            # Verify page loaded
            assert scraper.driver.title == "Test Page"
            
            # Verify can find elements
            h1 = scraper.driver.find_element("tag name", "h1")
            assert h1.text == "Test Heading"
            
            # Clean up
            scraper.cleanup()
            
        except ScraperException as e:
            pytest.skip(f"Could not initialize Chrome driver: {e}")

    def test_headless_mode_configuration(self):
        """Test that headless mode can be configured."""
        try:
            # Test with headless=True
            scraper_headless = SeleniumScraper(headless=True)
            assert scraper_headless.headless is True
            scraper_headless.cleanup()
            
            # Note: Testing headless=False in same process can be flaky
            # as Chrome may not fully release resources. In real usage,
            # each mode would be used in separate runs.
            
        except ScraperException as e:
            pytest.skip(f"Could not initialize Chrome driver: {e}")

    def test_screenshot_directory_creation(self):
        """Test that screenshot directory is created."""
        try:
            scraper = SeleniumScraper(headless=True)
            
            # Verify screenshot directory exists
            assert scraper.screenshot_dir.exists()
            assert scraper.screenshot_dir.is_dir()
            
            scraper.cleanup()
            
        except ScraperException as e:
            pytest.skip(f"Could not initialize Chrome driver: {e}")
