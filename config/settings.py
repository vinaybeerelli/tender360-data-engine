"""
Configuration management for Tender Scraper Engine
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    LOGS_DIR = DATA_DIR / "logs"
    DOWNLOADS_DIR = DATA_DIR / "downloads"
    BACKUPS_DIR = DATA_DIR / "backups"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/tender_scraper.db")
    
    # Scraper configuration
    BASE_URL: str = os.getenv("BASE_URL", "https://tender.telangana.gov.in")
    SCRAPER_MODE: str = os.getenv("SCRAPER_MODE", "api")
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Rate limiting
    MIN_DELAY: int = int(os.getenv("MIN_DELAY", "2"))
    MAX_DELAY: int = int(os.getenv("MAX_DELAY", "5"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "data/logs/scraper.log")
    
    # AWS configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-south-1")
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # Email notifications
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    ALERT_EMAIL: Optional[str] = os.getenv("ALERT_EMAIL")
    
    # Monitoring
    ENABLE_CLOUDWATCH: bool = os.getenv("ENABLE_CLOUDWATCH", "false").lower() == "true"
    HEALTH_CHECK_PORT: int = int(os.getenv("HEALTH_CHECK_PORT", "8000"))
    
    def __init__(self):
        """Initialize settings and create necessary directories."""
        self._create_directories()
    
    def _create_directories(self):
        """Create data directories if they don't exist."""
        for directory in [self.DATA_DIR, self.LOGS_DIR, self.DOWNLOADS_DIR, self.BACKUPS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def __repr__(self):
        return f"Settings(mode={self.SCRAPER_MODE}, base_url={self.BASE_URL})"

