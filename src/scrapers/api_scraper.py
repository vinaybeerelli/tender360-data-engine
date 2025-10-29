"""
API-based scraper - Primary scraping method
Implements Issue #1: Fix API Scraper Session Management
"""

from typing import List, Dict, Optional
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from .base_scraper import BaseScraper
from config.settings import Settings
from src.utils.logger import log
from src.utils.helpers import retry
from src.utils.exceptions import ScraperException, NetworkException
import re
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

import sys
from pathlib import Path
# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.constants import (
    API_HEADERS, 
    API_PAYLOAD, 
    TENDER_LIST_API, 
    TENDER_LIST_PAGE,
    TENDER_DETAIL_PAGE
)
from config.settings import Settings
from src.utils.logger import log
from src.utils.helpers import retry
from src.utils.helpers import retry, random_delay
from src.utils.exceptions import ScraperException


class APIScraper(BaseScraper):
    """
    API-based scraper using AJAX endpoints.

    This is the primary scraping method (faster and more reliable).
    Implements proper session management for AWS Mumbai deployment.
    """

    def __init__(self, headless=True):
        super().__init__(headless)
        self.settings = Settings()
        self.session = None
        self._establish_session()

    @retry(max_attempts=3, backoff_factor=2, exceptions=(RequestException,))
    def _establish_session(self):
        """
        Establish session by visiting main page to get cookies.

        IMPORTANT: Must visit main page before calling API endpoint.

        Raises:
            NetworkException: If session establishment fails after retries
        """
        log.info("Establishing session...")

        try:
            self.session = requests.Session()
            log.debug("Session object created successfully")

            # TODO: Visit main page to get JSESSIONID cookie
            # base_url = self.settings.BASE_URL
            # response = self.session.get(
            #     f"{base_url}/TenderDetailsHome.html",
            #     timeout=self.settings.REQUEST_TIMEOUT
            # )
            # response.raise_for_status()
            # log.info(f"Session established. Cookies: {list(self.session.cookies.keys())}")

        except Timeout as e:
            log.error(f"Timeout while establishing session: {e}")
            raise NetworkException(f"Session establishment timed out: {e}") from e
        except ConnectionError as e:
            log.error(f"Connection error while establishing session: {e}")
            raise NetworkException(
                f"Failed to connect during session establishment: {e}"
            ) from e
        except RequestException as e:
            log.error(f"Request failed during session establishment: {e}")
            raise NetworkException(f"Session establishment failed: {e}") from e
        except Exception as e:
            log.error(f"Unexpected error during session establishment: {e}")
            raise ScraperException(f"Unexpected error establishing session: {e}") from e

    @retry(max_attempts=3, backoff_factor=2, exceptions=(RequestException,))
    def scrape_tender_list(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Scrape list of tenders using API endpoint with comprehensive error handling.
        This prevents 403 errors on AWS Mumbai.
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

        # NOTE: When implementing, use API_HEADERS which includes X-Requested-With: XMLHttpRequest
        # response = self.session.get(BASE_URL + "/TenderDetailsHome.html", headers=API_HEADERS)
        pass
    
    @retry(max_attempts=3)
    def scrape_tender_list(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Scrape list of tenders using API endpoint.

        Args:
            limit: Maximum number of tenders to scrape

        Returns:
            List of tender dictionaries

        Raises:
            ScraperException: If scraping fails after retries
            NetworkException: If network operation fails
        """
        log.info(f"Scraping tender list (limit={limit})...")

        try:
            # Ensure session is established
            if not self.session:
                log.warning("Session not established, creating new session")
                self._establish_session()

            # TODO: Implement in Issue #1
            # This will be implemented to:
            # 1. POST to API endpoint with proper headers
            # 2. Parse JSON response
            # 3. Extract tender data
            # 4. Return list of tenders

            log.debug("API scraping implementation pending (Issue #1)")
            return []

        except Timeout as e:
            log.error(f"Timeout while scraping tender list: {e}")
            raise NetworkException(f"Tender list scraping timed out: {e}") from e
        except ConnectionError as e:
            log.error(f"Connection error while scraping tender list: {e}")
            raise NetworkException(f"Failed to connect while scraping: {e}") from e
        except RequestException as e:
            log.error(f"Request failed while scraping tender list: {e}")
            raise NetworkException(f"Tender list scraping failed: {e}") from e
        except ValueError as e:
            log.error(f"Invalid response data while scraping tender list: {e}")
            raise ScraperException(f"Failed to parse tender list response: {e}") from e
        except Exception as e:
            log.error(
                f"Unexpected error while scraping tender list: {e}", exc_info=True
            )
            raise ScraperException(f"Unexpected error scraping tender list: {e}") from e

    @retry(max_attempts=3, backoff_factor=2, exceptions=(RequestException,))
    def scrape_tender_details(self, tender_id: str) -> Dict:
        """
        Scrape detailed information for a tender with error handling.
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

        log.info(f"Scraping tender list (limit={limit})...")
        
        # This will be implemented to:
        # 1. POST to API endpoint with API_HEADERS (includes X-Requested-With: XMLHttpRequest)
        # 2. Parse JSON response
        # 3. Extract tender data
        # 4. Return list of tenders
        
        all_tenders = []
        
        try:
            # Determine how many to fetch
            display_length = min(limit or 100, 100)  # API max is 100 per request
            
            # Prepare payload
            payload = API_PAYLOAD.copy()
            payload['iDisplayLength'] = str(display_length)
            payload['iDisplayStart'] = '0'
            
            # Make API request
            api_url = self.settings.BASE_URL + TENDER_LIST_API
            log.debug(f"POST {api_url} with display_length={display_length}")
            
            response = self.session.post(
                api_url,
                headers=API_HEADERS,
                data=payload,
                timeout=self.settings.REQUEST_TIMEOUT
            )
            
            # Check response status
            if response.status_code == 403:
                log.error("Got 403 Forbidden - session may have expired")
                raise ScraperException("403 Forbidden - please check session establishment")
            
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Extract tender data from aaData array
            if 'aaData' not in data:
                log.error("No 'aaData' field in response")
                raise ScraperException("Invalid API response format")
            
            tender_data = data['aaData']
            
            if not tender_data:
                log.warning("No tenders found in response")
                return []
            
            log.info(f"Received {len(tender_data)} tenders from API")
            
            # Parse each tender row
            for idx, row in enumerate(tender_data):
                if limit and len(all_tenders) >= limit:
                    break
                
                try:
                    tender = self._parse_tender_row(row, idx)
                    if tender:
                        all_tenders.append(tender)
                except Exception as e:
                    log.warning(f"Failed to parse tender at index {idx}: {e}")
                    continue
            
            log.info(f"✓ Successfully parsed {len(all_tenders)} tenders")
            return all_tenders
            
        except requests.exceptions.RequestException as e:
            log.error(f"Network error during scraping: {e}")
            raise ScraperException(f"Network error: {e}")
        except Exception as e:
            log.error(f"Error scraping tender list: {e}")
            raise ScraperException(f"Scraping failed: {e}")
    
    def _parse_tender_row(self, row: List, index: int) -> Optional[Dict]:
        """
        Parse a single tender row from API response.
        
        Args:
            row: List containing tender data (corresponds to table columns)
            index: Row index for logging
            
        Returns:
            Dictionary with tender information or None if parsing fails
        """
        try:
            # Row structure based on TENDER_FIELDS mapping:
            # 0: department, 1: notice_number, 2: category, 3: work_name,
            # 4: tender_value, 5: published_date, 6: bid_start_date,
            # 7: bid_close_date, 8: tender_id, 9: actions
            
            if len(row) < 10:
                log.warning(f"Row {index} has insufficient columns: {len(row)}")
                return None
            
            # Extract basic fields
            tender = {
                'department': self._clean_html(row[0]),
                'notice_number': self._clean_html(row[1]),
                'category': self._clean_html(row[2]),
                'work_name': self._clean_html(row[3]),
                'tender_value': self._clean_html(row[4]),
                'published_date': self._clean_html(row[5]),
                'bid_start_date': self._clean_html(row[6]),
                'bid_close_date': self._clean_html(row[7]),
                'tender_id': self._clean_html(row[8]),
            }
            
            # Extract onclick parameters from actions column (if present)
            actions_html = row[9] if len(row) > 9 else ''
            onclick_params = self._extract_onclick_params(actions_html)
            if onclick_params:
                tender.update(onclick_params)
            
            log.debug(f"Parsed tender: {tender['notice_number']} - {tender['work_name'][:50]}")
            
            return tender
            
        except Exception as e:
            log.warning(f"Error parsing row {index}: {e}")
            return None
    
    def _clean_html(self, html_content: str) -> str:
        """
        Remove HTML tags and clean text content.
        
        Args:
            html_content: HTML string
            
        Returns:
            Cleaned text
        """
        if not html_content:
            return ''
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(str(html_content), 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _extract_onclick_params(self, actions_html: str) -> Dict[str, str]:
        """
        Extract parameters from onclick attribute in actions column.
        
        The onclick typically contains a function call like:
        onclick="GetTenderInfo('tenderNo','mode','refNo')"
        
        Args:
            actions_html: HTML content of actions column
            
        Returns:
            Dictionary with extracted parameters
        """
        params = {}
        
        try:
            # Look for onclick attribute with GetTenderInfo function call
            # Pattern matches: GetTenderInfo('param1','param2','param3')
            # Captures three quoted parameters separated by commas
            pattern = r"""
                onclick=[\"']           # onclick attribute start
                GetTenderInfo\(         # Function name
                ['\"]([^'\"]+)['\"],    # First parameter (tender number)
                \s*['\"]([^'\"]+)['\"], # Second parameter (mode)
                \s*['\"]([^'\"]+)['\"]  # Third parameter (reference number)
            """
            
            match = re.search(pattern, str(actions_html), re.VERBOSE)
            
            if match:
                params['onclick_param1'] = match.group(1)  # Tender number
                params['onclick_param2'] = match.group(2)  # Mode
                params['onclick_param3'] = match.group(3)  # Reference number
                log.debug(f"Extracted onclick params: {params}")
            
        except Exception as e:
            log.debug(f"Could not extract onclick params: {e}")
        
        return params
    
    def scrape_tender_details(self, tender_id: str) -> Dict:
        """
        Scrape detailed information for a tender.

        Args:
            tender_id: Unique tender identifier

        Returns:
            Dictionary with tender details

        Raises:
            ScraperException: If scraping fails after retries
            NetworkException: If network operation fails
        """
        log.info(f"Scraping details for tender: {tender_id}")

        try:
            # Validate input
            if not tender_id or not isinstance(tender_id, str):
                log.error(f"Invalid tender_id provided: {tender_id}")
                raise ValueError(f"Invalid tender_id: {tender_id}")

            # Ensure session is established
            if not self.session:
                log.warning("Session not established, creating new session")
                self._establish_session()

            # TODO: Implement in Issue #4
            log.debug(
                f"Tender details scraping implementation pending (Issue #4) for {tender_id}"
            )
            return {}

        except Timeout as e:
            log.error(f"Timeout while scraping tender details for {tender_id}: {e}")
            raise NetworkException(
                f"Tender details scraping timed out for {tender_id}: {e}"
            ) from e
        except ConnectionError as e:
            log.error(
                f"Connection error while scraping tender details for {tender_id}: {e}"
            )
            raise NetworkException(
                f"Failed to connect while scraping tender {tender_id}: {e}"
            ) from e
        except RequestException as e:
            log.error(
                f"Request failed while scraping tender details for {tender_id}: {e}"
            )
            raise NetworkException(
                f"Tender details scraping failed for {tender_id}: {e}"
            ) from e
        except ValueError as e:
            log.error(f"Validation error for tender {tender_id}: {e}")
            raise ScraperException(f"Invalid data for tender {tender_id}: {e}") from e
        except Exception as e:
            log.error(
                f"Unexpected error while scraping tender {tender_id}: {e}",
                exc_info=True,
            )
            raise ScraperException(
                f"Unexpected error scraping tender {tender_id}: {e}"
            ) from e

    @retry(max_attempts=3, backoff_factor=2, exceptions=(RequestException,))
    def extract_document_urls(self, tender_id: str) -> List[str]:
        """
        Extract document download URLs from tender page with error handling.
        return {}

    def extract_document_urls(self, tender_id: str) -> List[str]:
        """
        Extract document download URLs from tender page.

        Args:
            tender_id: Unique tender identifier

        Returns:
            List of document URLs

        Raises:
            ScraperException: If extraction fails after retries
            NetworkException: If network operation fails
        """
        log.info(f"Extracting document URLs for tender: {tender_id}")

        try:
            # Validate input
            if not tender_id or not isinstance(tender_id, str):
                log.error(f"Invalid tender_id provided: {tender_id}")
                raise ValueError(f"Invalid tender_id: {tender_id}")

            # Ensure session is established
            if not self.session:
                log.warning("Session not established, creating new session")
                self._establish_session()

            # TODO: Implement in Issue #5
            log.debug(
                f"Document URL extraction implementation pending (Issue #5) for {tender_id}"
            )
            return []

        except Timeout as e:
            log.error(f"Timeout while extracting document URLs for {tender_id}: {e}")
            raise NetworkException(
                f"Document URL extraction timed out for {tender_id}: {e}"
            ) from e
        except ConnectionError as e:
            log.error(
                f"Connection error while extracting document URLs for {tender_id}: {e}"
            )
            raise NetworkException(
                f"Failed to connect while extracting URLs for {tender_id}: {e}"
            ) from e
        except RequestException as e:
            log.error(
                f"Request failed while extracting document URLs for {tender_id}: {e}"
            )
            raise NetworkException(
                f"Document URL extraction failed for {tender_id}: {e}"
            ) from e
        except ValueError as e:
            log.error(f"Validation error for tender {tender_id}: {e}")
            raise ScraperException(f"Invalid data for tender {tender_id}: {e}") from e
        except Exception as e:
            log.error(
                f"Unexpected error while extracting URLs for {tender_id}: {e}",
                exc_info=True,
            )
            raise ScraperException(
                f"Unexpected error extracting URLs for {tender_id}: {e}"
            ) from e

    def cleanup(self):
        """Clean up session with proper error handling."""
        try:
            if self.session:
                log.debug("Closing session...")
                self.session.close()
                log.info("Session closed successfully")
        except Exception as e:
            log.error(f"Error while closing session: {e}")
            # Don't raise exception during cleanup
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
