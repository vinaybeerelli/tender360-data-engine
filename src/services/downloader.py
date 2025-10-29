"""
Document downloader service
This module will be implemented in Issue #6
"""

from pathlib import Path
from typing import Optional

from src.utils.logger import log
from src.utils.helpers import retry, random_delay
from config.settings import Settings
from config.constants import DOWNLOAD_HEADERS


class DocumentDownloader:
    """Service for downloading tender documents."""
    
    def __init__(self):
        self.settings = Settings()
        self.download_dir = self.settings.DOWNLOADS_DIR
    
    @retry(max_attempts=3)
    def download_document(self, url: str, tender_id: str, filename: str) -> Optional[Path]:
        """
        Download a document from URL.
        
        Args:
            url: Document URL
            tender_id: Tender ID (for organizing files)
            filename: Filename to save as
            
        Returns:
            Path to downloaded file or None if failed
        """
        # TODO: Implement in Issue #6
        log.info(f"Downloading document: {filename}")
        
        # This will be implemented to:
        # 1. Create directory: data/downloads/{tender_id}/
        # 2. Download file with retry logic using DOWNLOAD_HEADERS (includes X-Requested-With)
        # 3. Verify file integrity
        # 4. Return file path
        
        return None
    
    def is_already_downloaded(self, tender_id: str, filename: str) -> bool:
        """
        Check if document already downloaded.
        
        Args:
            tender_id: Tender ID
            filename: Filename
            
        Returns:
            True if file exists
        """
        file_path = self.download_dir / tender_id / filename
        return file_path.exists() and file_path.stat().st_size > 0

