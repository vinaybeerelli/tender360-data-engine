"""
Custom exceptions for Tender Scraper Engine
"""


class TenderScraperException(Exception):
    """Base exception for Tender Scraper Engine."""
    pass


class ScraperException(TenderScraperException):
    """Exception raised during scraping operations."""
    pass


class DatabaseException(TenderScraperException):
    """Exception raised during database operations."""
    pass


class ParserException(TenderScraperException):
    """Exception raised during document parsing."""
    pass


class NetworkException(TenderScraperException):
    """Exception raised during network operations."""
    pass


class RetryException(TenderScraperException):
    """Exception raised when max retries exceeded."""
    pass


class ConfigurationException(TenderScraperException):
    """Exception raised for configuration errors."""
    pass


class ValidationException(TenderScraperException):
    """Exception raised for data validation errors."""
    pass

