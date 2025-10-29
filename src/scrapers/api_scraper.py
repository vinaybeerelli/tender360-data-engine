"""
API-based scraper - Primary scraping method
This module will be implemented in Issue #1
"""

from typing import List, Dict, Optional
import requests
import re

from .base_scraper import BaseScraper
from config.constants import API_HEADERS, API_PAYLOAD, TENDER_LIST_API, TENDER_LIST_PAGE
from config.settings import Settings
from src.utils.logger import log
from src.utils.helpers import retry, random_delay
from src.utils.exceptions import ScraperException, NetworkException


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
            main_page_url = self.settings.BASE_URL + TENDER_LIST_PAGE
            log.info(f"Visiting main page: {main_page_url}")

            response = self.session.get(
                main_page_url,
                headers={
                    "User-Agent": API_HEADERS["User-Agent"],
                    "Accept": (
                        "text/html,application/xhtml+xml,application/xml;"
                        "q=0.9,image/webp,*/*;q=0.8"
                    ),
                    "Accept-Language": API_HEADERS["Accept-Language"],
                },
                timeout=self.settings.REQUEST_TIMEOUT,
            )

            if response.status_code == 200:
                cookies_list = list(self.session.cookies.keys())
                log.info(f"Session established successfully. Cookies: {cookies_list}")

                # Verify we got JSESSIONID cookie
                if "JSESSIONID" in self.session.cookies:
                    log.info(
                        f"JSESSIONID cookie obtained: {self.session.cookies['JSESSIONID'][:20]}..."
                    )
                else:
                    log.warning("JSESSIONID cookie not found in response")
            else:
                raise NetworkException(
                    f"Failed to establish session. Status: {response.status_code}"
                )

        except requests.RequestException as e:
            log.error(f"Failed to establish session: {e}")
            raise NetworkException(f"Session establishment failed: {e}")

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
        log.info(f"Scraping tender list (limit={limit})...")

        if not self.session:
            raise ScraperException(
                "Session not established. Call _establish_session() first."
            )

        try:
            # Prepare API endpoint URL
            api_url = self.settings.BASE_URL + TENDER_LIST_API
            log.info(f"Making API request to: {api_url}")

            # Prepare payload
            payload = API_PAYLOAD.copy()
            if limit:
                payload["iDisplayLength"] = str(limit)

            # Add random delay to be polite
            random_delay(self.settings.MIN_DELAY, self.settings.MAX_DELAY)

            # Make POST request to API endpoint
            response = self.session.post(
                api_url,
                data=payload,
                headers=API_HEADERS,
                timeout=self.settings.REQUEST_TIMEOUT,
            )

            # Check response status
            if response.status_code == 403:
                raise ScraperException(
                    "API returned 403 Forbidden. Session may be invalid."
                )
            elif response.status_code != 200:
                raise ScraperException(
                    f"API returned status code: {response.status_code}"
                )

            # Parse JSON response
            try:
                data = response.json()
            except ValueError as e:
                log.error(f"Failed to parse JSON response: {e}")
                log.debug(f"Response content: {response.text[:500]}")
                raise ScraperException(f"Invalid JSON response from API: {e}")

            # Extract tender data from response
            if "aaData" not in data:
                log.error("Response does not contain 'aaData' field")
                log.debug(f"Response keys: {data.keys()}")
                raise ScraperException("API response missing 'aaData' field")

            tender_rows = data["aaData"]
            log.info(f"API returned {len(tender_rows)} tender rows")

            if not tender_rows:
                log.warning("API returned empty tender list")
                return []

            # Parse tender data
            tenders = []
            for row in tender_rows:
                try:
                    tender = self._parse_tender_row(row)
                    if tender:
                        tenders.append(tender)
                except Exception as e:
                    log.warning(f"Failed to parse tender row: {e}")
                    continue

            log.info(f"Successfully parsed {len(tenders)} tenders")
            return tenders[:limit] if limit else tenders

        except requests.RequestException as e:
            log.error(f"Network error during API request: {e}")
            raise NetworkException(f"API request failed: {e}")
        except Exception as e:
            log.error(f"Unexpected error during scraping: {e}")
            raise ScraperException(f"Scraping failed: {e}")

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

    def _parse_tender_row(self, row: List) -> Optional[Dict]:
        """
        Parse a tender row from API response.

        Args:
            row: List of tender field values from API response.
                Expected structure (10 elements):
                [0] department (str)
                [1] notice_number (str)
                [2] category (str)
                [3] work_name (str)
                [4] tender_value (str)
                [5] published_date (str)
                [6] bid_start_date (str)
                [7] bid_close_date (str)
                [8] tender_id (str) - may contain onclick attribute
                [9] actions (str) - HTML with onclick="viewDetailTender('T...')"

        Returns:
            Dictionary with parsed tender data, or None if parsing fails
        """
        try:
            # Row structure based on TENDER_FIELDS mapping:
            # 0: department, 1: notice_number, 2: category, 3: work_name,
            # 4: tender_value, 5: published_date, 6: bid_start_date,
            # 7: bid_close_date, 8: tender_id, 9: actions (onclick)

            if len(row) < 10:
                log.warning(f"Row has insufficient columns: {len(row)}")
                return None

            # Extract tender ID from the onclick parameter in actions column
            tender_id = self._extract_tender_id(row[9])

            if not tender_id:
                log.warning(
                    f"Could not extract tender ID from actions column: {row[9][:100]}"
                )
                return None

            tender = {
                "tender_id": tender_id,
                "department": self._clean_html(row[0]),
                "notice_number": self._clean_html(row[1]),
                "category": self._clean_html(row[2]),
                "work_name": self._clean_html(row[3]),
                "tender_value": self._clean_html(row[4]),
                "published_date": self._clean_html(row[5]),
                "bid_start_date": self._clean_html(row[6]),
                "bid_close_date": self._clean_html(row[7]),
            }

            return tender

        except Exception as e:
            log.error(f"Failed to parse tender row: {e}")
            return None

    def _extract_tender_id(self, actions_html: str) -> Optional[str]:
        """
        Extract tender ID from onclick parameter in actions column.

        Example: onclick="viewDetailTender('T001234567')"

        Args:
            actions_html: HTML string containing onclick attribute

        Returns:
            Tender ID string or None if not found
        """
        try:
            # Look for pattern like viewDetailTender('T001234567')
            match = re.search(r"viewDetailTender\(['\"]([T]\d+)['\"]\)", actions_html)
            if match:
                return match.group(1)

            # Alternative pattern: just look for a tender ID pattern (T followed by digits)
            match = re.search(r"['\"](T\d+)['\"]", actions_html)
            if match:
                return match.group(1)

            return None

        except Exception as e:
            log.warning(f"Error extracting tender ID: {e}")
            return None

    def _clean_html(self, text: str) -> str:
        """
        Clean HTML tags and extra whitespace from text.

        Args:
            text: Text that may contain HTML

        Returns:
            Cleaned text
        """
        if not text or not isinstance(text, str):
            return ""

        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)

        # Remove extra whitespace
        text = " ".join(text.split())

        # Decode HTML entities
        text = (
            text.replace("&nbsp;", " ")
            .replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
        )

        return text.strip()

    def cleanup(self):
        """Clean up session."""
        if self.session:
            self.session.close()
