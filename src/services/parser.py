"""
Document parser service
This module will be implemented in Issue #7
"""

from pathlib import Path
from typing import Dict, Optional
import re

from src.utils.logger import log
from src.utils.exceptions import ParserException
from config.constants import PATTERNS


class DocumentParser:
    """Service for parsing tender documents."""
    
    def parse_document(self, file_path: Path) -> Dict[str, str]:
        """
        Parse document and extract fields.
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dictionary of extracted fields
        """
        file_ext = file_path.suffix.lower()
        
        try:
            if file_ext == '.pdf':
                return self.parse_pdf(file_path)
            elif file_ext in ['.xls', '.xlsx']:
                return self.parse_excel(file_path)
            elif file_ext in ['.doc', '.docx']:
                return self.parse_word(file_path)
            else:
                log.warning(f"Unsupported file type: {file_ext}")
                return {}
        except Exception as e:
            log.error(f"Failed to parse document {file_path}: {e}")
            raise ParserException(f"Parsing failed: {e}")
    
    def parse_pdf(self, file_path: Path) -> Dict[str, str]:
        """
        Parse PDF document.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary of extracted fields
        """
        # TODO: Implement in Issue #7
        log.info(f"Parsing PDF: {file_path.name}")
        
        # This will use pdfplumber to:
        # 1. Extract text from PDF
        # 2. Apply regex patterns for EMD, dates, amounts
        # 3. Return structured data
        
        return {}
    
    def parse_excel(self, file_path: Path) -> Dict[str, str]:
        """
        Parse Excel document.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Dictionary of extracted fields
        """
        # TODO: Implement in Issue #7
        log.info(f"Parsing Excel: {file_path.name}")
        return {}
    
    def parse_word(self, file_path: Path) -> Dict[str, str]:
        """
        Parse Word document.
        
        Args:
            file_path: Path to Word file
            
        Returns:
            Dictionary of extracted fields
        """
        # TODO: Implement in Issue #7
        log.info(f"Parsing Word: {file_path.name}")
        return {}
    
    def extract_emd(self, text: str) -> Optional[str]:
        """
        Extract EMD amount from text using regex.
        
        Args:
            text: Document text
            
        Returns:
            EMD amount or None
        """
        match = re.search(PATTERNS['emd'], text, re.IGNORECASE)
        return match.group(1) if match else None

