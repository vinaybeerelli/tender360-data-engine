"""
API-based scraper - Primary scraping method
This module will be implemented in Issue #1
"""

from typing import List, Dict, Optional
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from .base_scraper import BaseScraper
from config.settings import Settings
from src.utils.logger import log
from src.utils.helpers import retry
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
