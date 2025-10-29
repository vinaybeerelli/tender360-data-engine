"""
API-based scraper - Primary scraping method
This module will be implemented in Issue #1
"""

from typing import List, Dict, Optional
import requests

from .base_scraper import BaseScraper
from config.constants import API_HEADERS, API_PAYLOAD, TENDER_LIST_API
from config.settings import Settings
from src.utils.logger import log
from src.utils.helpers import retry


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
        main_page_url = self.settings.BASE_URL + "/TenderDetailsHome.html"
        try:
            response = self.session.get(main_page_url, timeout=self.settings.REQUEST_TIMEOUT)
            response.raise_for_status()
            log.info(f"Session established successfully. Cookies: {list(self.session.cookies.keys())}")
        except Exception as e:
            log.error(f"Failed to establish session: {e}")
            raise

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
        from src.utils.exceptions import ScraperException

        log.info(f"Scraping tender list (limit={limit})...")

        # Build API URL
        api_url = self.settings.BASE_URL + TENDER_LIST_API

        # Update payload with display length
        payload = API_PAYLOAD.copy()
        if limit:
            payload['iDisplayLength'] = str(limit)

        try:
            # Make API request
            response = self.session.post(
                api_url,
                data=payload,
                headers=API_HEADERS,
                timeout=self.settings.REQUEST_TIMEOUT
            )
            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            # Extract tender list from aaData
            if 'aaData' not in data:
                raise ScraperException("API response missing 'aaData' field")

            tenders_data = data['aaData']
            log.info(f"Received {len(tenders_data)} tenders from API")

            # Parse tender data
            tenders = []
            for tender_row in tenders_data:
                try:
                    tender = self._parse_tender_row(tender_row)
                    tenders.append(tender)
                except Exception as e:
                    log.warning(f"Failed to parse tender row: {e}")
                    continue

            log.info(f"Successfully parsed {len(tenders)} tenders")

            # Apply limit if specified
            if limit and len(tenders) > limit:
                tenders = tenders[:limit]

            return tenders

        except Exception as e:
            log.error(f"Failed to scrape tender list: {e}")
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

    def cleanup(self):
        """Clean up session."""
        if self.session:
            self.session.close()

    def _parse_tender_row(self, row: List) -> Dict:
        """
        Parse a tender row from API response.

        Args:
            row: List of tender data fields

        Returns:
            Dictionary with parsed tender data
        """
        import re
        from bs4 import BeautifulSoup

        # Extract fields based on TENDER_FIELDS mapping
        tender = {
            'department': row[0] if len(row) > 0 else '',
            'notice_number': row[1] if len(row) > 1 else '',
            'category': row[2] if len(row) > 2 else '',
            'work_name': row[3] if len(row) > 3 else '',
            'tender_value': row[4] if len(row) > 4 else '',
            'published_date': row[5] if len(row) > 5 else '',
            'bid_start_date': row[6] if len(row) > 6 else '',
            'bid_close_date': row[7] if len(row) > 7 else '',
            'tender_id': row[8] if len(row) > 8 else '',
        }

        # Extract tender ID and onclick parameters from actions column if available
        if len(row) > 9:
            actions_html = row[9]
            soup = BeautifulSoup(actions_html, 'html.parser')

            # Find onclick attribute
            onclick_elem = soup.find(attrs={'onclick': True})
            if onclick_elem:
                onclick = onclick_elem.get('onclick', '')
                # Extract parameters from onclick like: openWin('param1','param2')
                match = re.search(r"openWin\('([^']+)','([^']+)'\)", onclick)
                if match:
                    tender['tender_ref'] = match.group(1)
                    tender['tender_ref2'] = match.group(2)

        return tender
