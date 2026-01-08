"""Filename parser for extracting month and company name from settlement file names.

This module parses settlement file names in the format
'ㅇㅇ mm월 w주차 정산표.xlsx' to extract month and company name.
"""

import re
from typing import Optional, Tuple
from datetime import datetime


class FilenameParser:
    """Parser for settlement file names.
    
    Extracts month and company name from file names in the format:
    'ㅇㅇ mm월 w주차 정산표.xlsx'
    
    This is used to automatically set year/month combo boxes when
    a settlement file is selected (FR-005, FR-006).
    """
    
    # Pattern: company_name + space + month + 월 + space + week + 주차 + space + 정산표.xlsx
    FILENAME_PATTERN = re.compile(
        r'(.+?)\s+(\d+)월\s+\d+주차\s+정산표\.xlsx',
        re.UNICODE
    )
    
    @classmethod
    def parse_filename(cls, filename: str) -> Optional[Tuple[str, int, int]]:
        """Parse filename to extract company name, month, and week.
        
        Args:
            filename: Settlement file name (e.g., 'ABC 1월 1주차 정산표.xlsx')
            
        Returns:
            Tuple of (company_name, month, week) if parsing succeeds, None otherwise
            
        Raises:
            ValueError: If filename format is invalid (handled by returning None)
            
        Example:
            >>> FilenameParser.parse_filename('ABC 1월 1주차 정산표.xlsx')
            ('ABC', 1, 1)
        """
        try:
            match = cls.FILENAME_PATTERN.match(filename)
            if not match:
                return None
            
            company_name = match.group(1).strip()
            if not company_name:
                return None
            
            month = int(match.group(2))
            if month < 1 or month > 12:
                return None
            
            # Week extraction would require another group, but it's not used currently
            # For now, we'll extract it if needed
            week_match = re.search(r'(\d+)주차', filename)
            week = int(week_match.group(1)) if week_match else 0
            
            return (company_name, month, week)
        except (ValueError, AttributeError):
            # Handle parsing errors gracefully
            return None
    
    @classmethod
    def extract_month(cls, filename: str) -> Optional[int]:
        """Extract month number from filename.
        
        Args:
            filename: Settlement file name
            
        Returns:
            Month number (1-12) if found, None otherwise
        """
        result = cls.parse_filename(filename)
        if result:
            return result[1]
        return None
    
    @classmethod
    def extract_company_name(cls, filename: str) -> Optional[str]:
        """Extract company name from filename.
        
        Extracts the text before the first space in the filename.
        For example: "배플 12월 5주차 정산표(1231합산).xlsx" -> "배플"
        
        Args:
            filename: Settlement file name
            
        Returns:
            Company name if found, None otherwise
        """
        # First try the existing pattern-based extraction
        result = cls.parse_filename(filename)
        if result:
            return result[0]
        
        # Fallback: extract text before first space
        # Remove extension first
        name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
        # Extract text before first space
        if ' ' in name_without_ext:
            company_name = name_without_ext.split(' ', 1)[0].strip()
            if company_name:
                return company_name
        
        return None
    
    @classmethod
    def suggest_year(cls, month: int) -> int:
        """Suggest year based on current date and extracted month.
        
        If the extracted month is in the future relative to current month,
        assume it's from the previous year. Otherwise, use current year.
        
        Args:
            month: Extracted month (1-12)
            
        Returns:
            Suggested year (e.g., 2024, 2025)
        """
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        
        # If extracted month is greater than current month, likely from previous year
        # (e.g., if we're in January and file says "12월", it's probably December of last year)
        if month > current_month:
            return current_year - 1
        
        return current_year

