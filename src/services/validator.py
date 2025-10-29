"""
Data validation service
"""

from typing import Dict, List
from datetime import datetime

from src.utils.logger import log
from src.utils.exceptions import ValidationException


class DataValidator:
    """Service for validating extracted data."""
    
    def validate_tender(self, tender_data: Dict) -> bool:
        """
        Validate tender data.
        
        Args:
            tender_data: Dictionary with tender information
            
        Returns:
            True if valid
            
        Raises:
            ValidationException: If validation fails
        """
        required_fields = ['tender_id', 'work_name', 'department']
        
        for field in required_fields:
            if field not in tender_data or not tender_data[field]:
                raise ValidationException(f"Missing required field: {field}")
        
        return True
    
    def validate_date(self, date_str: str) -> bool:
        """
        Validate date format.
        
        Args:
            date_str: Date string
            
        Returns:
            True if valid date format
        """
        date_formats = [
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%Y-%m-%d',
            '%d-%m-%y',
            '%d/%m/%y'
        ]
        
        for fmt in date_formats:
            try:
                datetime.strptime(date_str, fmt)
                return True
            except ValueError:
                continue
        
        log.warning(f"Invalid date format: {date_str}")
        return False
    
    def validate_amount(self, amount_str: str) -> bool:
        """
        Validate currency amount.
        
        Args:
            amount_str: Amount string
            
        Returns:
            True if valid amount format
        """
        # Remove currency symbols and commas
        cleaned = amount_str.replace('Rs.', '').replace('INR', '').replace(',', '').strip()
        
        try:
            amount = float(cleaned)
            return amount >= 0
        except ValueError:
            log.warning(f"Invalid amount format: {amount_str}")
            return False

