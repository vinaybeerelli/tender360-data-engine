"""
Selenium-based scraper - Fallback method
Browser automation using undetected-chromedriver
"""

import os
import shutil
import time
import random
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from .base_scraper import BaseScraper
from config.settings import Settings
from config.constants import TABLE_ID, TENDER_LIST_PAGE
from src.utils.logger import log
from src.utils.exceptions import ScraperException


class DataRowsPresent:
    """
    Custom expected condition to check if data rows are present in table.
    More efficient than lambda as it avoids repeated element lookups.
    """

    def __init__(self, table_id: str):
        self.table_id = table_id
        self.selector = f"#{table_id} tbody tr:not(.dataTables_empty)"

    def __call__(self, driver):
        """Check if data rows exist."""
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, self.selector)
            return len(rows) > 0
        except Exception:
            return False


class SeleniumScraper(BaseScraper):
    """
    Browser-based scraper using Selenium.

    This is the fallback method when API scraping fails.
    Uses undetected-chromedriver to avoid detection.
    """

    def __init__(self, headless=True):
        super().__init__(headless)
        self.settings = Settings()
        self.driver = None
        self.screenshot_dir = self.settings.DATA_DIR / "screenshots"
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.driver_dir = self.settings.DATA_DIR / "drivers"
        self.driver_dir.mkdir(parents=True, exist_ok=True)
        self._setup_chromedriver()
        self._init_driver()

    def _setup_chromedriver(self):
        """
        Setup local chromedriver for undetected-chromedriver to patch.
        
        undetected-chromedriver needs to patch the chromedriver binary to avoid detection.
        This method ensures we have a writable copy in the data/drivers directory.
        """
        local_driver_path = self.driver_dir / "chromedriver"
        
        # If local driver already exists, use it
        if local_driver_path.exists():
            log.debug(f"Using existing chromedriver at: {local_driver_path}")
            self.driver_executable_path = str(local_driver_path)
            return
        
        # Try to find system chromedriver
        system_driver = shutil.which("chromedriver")
        if system_driver:
            log.info(f"Found system chromedriver at: {system_driver}")
            log.info(f"Copying to local directory: {local_driver_path}")
            
            try:
                shutil.copy2(system_driver, local_driver_path)
                local_driver_path.chmod(0o755)  # Make executable
                log.info("Chromedriver setup successful")
                self.driver_executable_path = str(local_driver_path)
                return
            except Exception as e:
                log.warning(f"Failed to copy chromedriver: {e}")
        
        # If no system driver found, let undetected-chromedriver try to download it
        # This will fail in environments without internet access, but we document it
        log.warning(
            "No system chromedriver found. undetected-chromedriver will attempt to "
            "download it automatically. This requires internet access."
        )
        self.driver_executable_path = None

    def _init_driver(self):
        """Initialize Chrome driver with undetected-chromedriver."""
        try:
            log.info("Initializing Chrome driver...")

            options = uc.ChromeOptions()

            if self.headless:
                options.add_argument("--headless=new")

            # Additional options for stability
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

            # User agent - use a more generic recent Chrome version
            # This can be made configurable in future via Settings
            user_agent = (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/119.0.0.0 Safari/537.36"
            )
            options.add_argument(f"user-agent={user_agent}")

            # Create driver with explicit path if available
            # This avoids undetected-chromedriver trying to download from internet
            driver_kwargs = {
                "options": options,
                "use_subprocess": True,
            }
            
            # Use local chromedriver if available
            if self.driver_executable_path:
                driver_kwargs["driver_executable_path"] = self.driver_executable_path
                log.info(f"Using chromedriver at: {self.driver_executable_path}")
            else:
                # Let undetected-chromedriver auto-detect (requires internet)
                driver_kwargs["version_main"] = None
                log.info("Auto-detecting Chrome version (requires internet access)")
            
            self.driver = uc.Chrome(**driver_kwargs)
            self.driver.set_page_load_timeout(60)

            log.info("Chrome driver initialized successfully")

        except Exception as e:
            log.error(f"Failed to initialize Chrome driver: {e}")
            raise ScraperException(f"Chrome driver initialization failed: {e}")

    def _take_screenshot(self, name: str):
        """
        Take screenshot for debugging.

        Args:
            name: Screenshot filename (without extension)
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.screenshot_dir / f"{name}_{timestamp}.png"
            self.driver.save_screenshot(str(filepath))
            log.info(f"Screenshot saved: {filepath}")
        except Exception as e:
            log.warning(f"Failed to take screenshot: {e}")

    def _human_delay(self, min_sec: float = 2.0, max_sec: float = 5.0):
        """
        Add human-like delay.

        Args:
            min_sec: Minimum delay in seconds
            max_sec: Maximum delay in seconds
        """
        delay = random.uniform(min_sec, max_sec)
        log.debug(f"Human delay: {delay:.2f}s")
        time.sleep(delay)

    def _wait_for_data_rows(self, timeout: int = 30) -> bool:
        """
        Wait for DataTable to populate with actual data.

        CRITICAL: This waits for actual data rows, not just empty table.

        Args:
            timeout: Maximum wait time in seconds

        Returns:
            True if data rows found, False otherwise
        """
        try:
            log.info("Waiting for DataTable to populate with data...")

            # First wait for table element to exist
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.ID, TABLE_ID)))
            log.debug(f"Table element #{TABLE_ID} found")

            # Now wait for actual data rows using custom condition
            # This is more efficient than lambda and provides better debugging
            WebDriverWait(self.driver, timeout).until(DataRowsPresent(TABLE_ID))

            rows = self.driver.find_elements(By.CSS_SELECTOR, f"#{TABLE_ID} tbody tr:not(.dataTables_empty)")
            log.info(f"DataTable populated with {len(rows)} rows")

            return True

        except TimeoutException:
            log.error(f"Timeout waiting for DataTable data after {timeout}s")
            self._take_screenshot("timeout_waiting_for_data")
            return False
        except Exception as e:
            log.error(f"Error waiting for data rows: {e}")
            self._take_screenshot("error_waiting_for_data")
            return False

    def _extract_row_data(self, row) -> Optional[Dict]:
        """
        Extract data from a table row.

        Args:
            row: Selenium WebElement for table row

        Returns:
            Dictionary with tender data or None if error
        """
        try:
            cells = row.find_elements(By.TAG_NAME, "td")

            if len(cells) < 10:
                log.warning(f"Row has only {len(cells)} cells, expected 10")
                return None

            # Extract data according to TENDER_FIELDS mapping
            tender_data = {
                "department": cells[0].text.strip(),
                "notice_number": cells[1].text.strip(),
                "category": cells[2].text.strip(),
                "work_name": cells[3].text.strip(),
                "tender_value": cells[4].text.strip(),
                "published_date": cells[5].text.strip(),
                "bid_start_date": cells[6].text.strip(),
                "bid_close_date": cells[7].text.strip(),
                "tender_id": cells[8].text.strip(),
                "scraped_at": datetime.now().isoformat(),
            }

            # Extract detail URL from the "View Details" link in actions column
            try:
                detail_link = cells[9].find_element(By.TAG_NAME, "a")
                tender_data["detail_url"] = detail_link.get_attribute("href")
            except NoSuchElementException:
                tender_data["detail_url"] = ""
                log.debug(f"No detail link found for tender {tender_data['tender_id']}")

            return tender_data

        except Exception as e:
            log.error(f"Error extracting row data: {e}")
            return None

    def scrape_tender_list(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Scrape list of tenders using browser automation.

        Args:
            limit: Maximum number of tenders to scrape

        Returns:
            List of tender dictionaries

        Raises:
            ScraperException: If scraping fails
        """
        log.info(f"Scraping tender list with Selenium (limit={limit})...")

        try:
            # Navigate to tender listing page
            url = self.settings.BASE_URL + TENDER_LIST_PAGE
            log.info(f"Navigating to: {url}")
            self.driver.get(url)

            # Human-like delay after page load
            self._human_delay(2, 4)

            # Wait for data to populate
            if not self._wait_for_data_rows():
                raise ScraperException("Failed to load tender data")

            # Extract data from rows
            rows = self.driver.find_elements(By.CSS_SELECTOR, f"#{TABLE_ID} tbody tr:not(.dataTables_empty)")

            tenders = []
            rows_to_process = rows[:limit] if limit else rows

            log.info(f"Processing {len(rows_to_process)} rows...")

            for idx, row in enumerate(rows_to_process, 1):
                tender_data = self._extract_row_data(row)

                if tender_data:
                    tenders.append(tender_data)
                    log.debug(f"Extracted tender {idx}/{len(rows_to_process)}: {tender_data.get('tender_id', 'N/A')}")

                # Small delay between rows to be more human-like
                if idx % 5 == 0:
                    time.sleep(random.uniform(0.5, 1.5))

            log.info(f"Successfully scraped {len(tenders)} tenders")
            return tenders

        except WebDriverException as e:
            log.error(f"WebDriver error during scraping: {e}")
            self._take_screenshot("webdriver_error")
            raise ScraperException(f"WebDriver error: {e}")
        except Exception as e:
            log.error(f"Unexpected error during scraping: {e}")
            self._take_screenshot("unexpected_error")
            raise ScraperException(f"Scraping failed: {e}")

    def scrape_tender_details(self, tender_id: str) -> Dict:
        """
        Scrape detailed information for a tender.

        Opens detail page in new window and extracts information.

        Args:
            tender_id: Unique tender identifier

        Returns:
            Dictionary with tender details
        """
        log.info(f"Scraping details with Selenium for tender: {tender_id}")

        try:
            # Store original window handle
            original_window = self.driver.current_window_handle

            # Find and click the "View Details" link for this tender
            # This will open in a new window
            detail_link = self.driver.find_element(
                By.XPATH,
                f"//td[contains(text(), '{tender_id}')]/following-sibling::td//a[contains(text(), 'View Details')]",
            )

            detail_link.click()

            # Human-like delay
            self._human_delay(2, 3)

            # Wait for new window to open
            WebDriverWait(self.driver, 10).until(lambda d: len(d.window_handles) > 1)

            # Switch to new window
            for window_handle in self.driver.window_handles:
                if window_handle != original_window:
                    self.driver.switch_to.window(window_handle)
                    break

            # Wait for page to load
            time.sleep(2)

            # Extract details - this is a placeholder structure
            # Actual implementation depends on detail page structure
            details = {
                "tender_id": tender_id,
                "eligibility": "",
                "general_terms": "",
                "legal_terms": "",
                "technical_terms": "",
                "submission_procedure": "",
                "scraped_at": datetime.now().isoformat(),
            }

            # TODO: Extract actual detail fields based on page structure
            # This will be implemented in Issue #4

            log.info(f"Extracted details for tender: {tender_id}")

            # Close detail window and switch back to original
            self.driver.close()
            self.driver.switch_to.window(original_window)

            return details

        except NoSuchElementException:
            log.error(f"Could not find detail link for tender: {tender_id}")
            return {}
        except Exception as e:
            log.error(f"Error scraping tender details: {e}")
            self._take_screenshot(f"error_details_{tender_id}")

            # Ensure we return to original window
            try:
                self.driver.switch_to.window(original_window)
            except Exception:
                pass

            return {}

    def extract_document_urls(self, tender_id: str) -> List[str]:
        """
        Extract document download URLs from tender page.

        Args:
            tender_id: Unique tender identifier

        Returns:
            List of document URLs
        """
        log.info(f"Extracting document URLs with Selenium for tender: {tender_id}")

        try:
            # Navigate to detail page if needed
            # Extract all document links
            # This is a placeholder - actual implementation in Issue #5

            document_links = []

            # Find all links that look like document downloads
            links = self.driver.find_elements(
                By.XPATH, "//a[contains(@href, '.pdf') or contains(@href, '.doc') or contains(@href, '.xls')]"
            )

            for link in links:
                url = link.get_attribute("href")
                if url:
                    document_links.append(url)

            log.info(f"Found {len(document_links)} document URLs")
            return document_links

        except Exception as e:
            log.error(f"Error extracting document URLs: {e}")
            return []

    def cleanup(self):
        """Clean up browser driver."""
        if self.driver:
            try:
                log.info("Closing browser...")
                self.driver.quit()
                log.info("Browser closed successfully")
            except Exception as e:
                log.warning(f"Error closing browser: {e}")
