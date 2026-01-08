"""Driver list reader for extracting resident numbers from driver list file.

This module handles reading driver list Excel files to extract
name-resident number mappings.
"""

from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass
from src.utils.excel_helper import ExcelHelper
from src.models.config import Configuration
import re


@dataclass
class DriverInfo:
    """Driver information from driver list file."""
    name: str
    baemin_rider_id: Optional[str]
    coupang_rider_id: Optional[str]
    resident_number: Optional[str]


class DriverListReader:
    """Reads driver list file and provides name to driver info mapping.
    
    Attributes:
        file_path: Path to the driver list file
        name_to_drivers: Dictionary mapping cleaned names to list of DriverInfo
    """
    
    def __init__(self, file_path: str, config: Optional[Configuration] = None):
        """Initialize DriverListReader.
        
        Args:
            file_path: Path to driver list Excel file
            config: Configuration object (creates new one if None)
        """
        self.file_path = Path(file_path)
        self.name_to_drivers: Dict[str, List[DriverInfo]] = {}
        
        if config is None:
            config = Configuration()
            config.load()
        self.config = config
    
    def load_driver_list(self) -> Dict[str, List[DriverInfo]]:
        """Load driver list and create name to driver info mapping.
        
        Reads the driver list file and creates a dictionary mapping
        cleaned names (with numbers removed) to list of DriverInfo.
        Multiple drivers can have the same cleaned name.
        
        Assumes column structure:
        - A: 이름
        - B: 배플 라이더 ID (optional)
        - C: 쿠팡 라이더 ID (optional)
        - D: 주민번호
        
        Returns:
            Dictionary mapping cleaned names to list of DriverInfo
            
        Raises:
            FileNotFoundError: If driver list file doesn't exist
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"기사명단 파일을 찾을 수 없습니다: {self.file_path}")
        
        workbook = ExcelHelper.load_workbook(str(self.file_path), data_only=True)
        worksheet = workbook.active  # Use active sheet
        
        # Default column structure: A=이름, B=배플 라이더 ID, C=쿠팡 라이더 ID, D=주민번호
        name_column = "A"
        baemin_id_column = "B"
        coupang_id_column = "C"
        resident_column = "D"
        
        # Read all rows (skip header row if exists)
        # Try to detect header row by checking if first row contains text that looks like headers
        start_row = 1
        first_row_name = ExcelHelper.get_cell_value(worksheet, f"{name_column}1")
        if first_row_name and isinstance(first_row_name, str):
            # Check if it looks like a header (contains common header words)
            header_keywords = ["이름", "성명", "name", "기사", "주민번호", "resident", "라이더", "rider"]
            if any(keyword in str(first_row_name).lower() for keyword in header_keywords):
                start_row = 2
        
        # Read up to row 1000 (adjust as needed)
        max_row = min(worksheet.max_row, 1000)
        
        self.name_to_drivers = {}
        for row_num in range(start_row, max_row + 1):
            name_cell = f"{name_column}{row_num}"
            baemin_id_cell = f"{baemin_id_column}{row_num}"
            coupang_id_cell = f"{coupang_id_column}{row_num}"
            resident_cell = f"{resident_column}{row_num}"
            
            name_value = ExcelHelper.get_cell_value(worksheet, name_cell)
            baemin_id_value = ExcelHelper.get_cell_value(worksheet, baemin_id_cell)
            coupang_id_value = ExcelHelper.get_cell_value(worksheet, coupang_id_cell)
            resident_value = ExcelHelper.get_cell_value(worksheet, resident_cell)
            
            if name_value:
                # Remove numbers from name for matching
                name_str = str(name_value).strip()
                cleaned_name = self._remove_numbers_from_name(name_str)
                
                if cleaned_name:
                    driver_info = DriverInfo(
                        name=name_str,  # Original name with numbers
                        baemin_rider_id=str(baemin_id_value).strip() if baemin_id_value else None,
                        coupang_rider_id=str(coupang_id_value).strip() if coupang_id_value else None,
                        resident_number=str(resident_value).strip() if resident_value else None
                    )
                    
                    # Add to dictionary (multiple drivers can have same cleaned name)
                    if cleaned_name not in self.name_to_drivers:
                        self.name_to_drivers[cleaned_name] = []
                    self.name_to_drivers[cleaned_name].append(driver_info)
        
        workbook.close()
        return self.name_to_drivers
    
    def _remove_numbers_from_name(self, name: str) -> str:
        """Remove numbers from name string.
        
        Args:
            name: Name string that may contain numbers
            
        Returns:
            Name string with numbers removed
        """
        # Remove all digits from the string
        return re.sub(r'\d', '', name).strip()
    
    def get_drivers_by_name(self, name: str) -> List[DriverInfo]:
        """Get list of drivers matching a given name.
        
        Args:
            name: Name to look up (numbers will be removed automatically)
            
        Returns:
            List of DriverInfo matching the name (empty list if not found)
        """
        cleaned_name = self._remove_numbers_from_name(name)
        return self.name_to_drivers.get(cleaned_name, [])
    
    def get_single_driver(self, name: str) -> Optional[DriverInfo]:
        """Get single driver for a given name.
        
        If multiple drivers match, returns the first one.
        Use get_drivers_by_name() to handle duplicates.
        
        Args:
            name: Name to look up (numbers will be removed automatically)
            
        Returns:
            DriverInfo if found, None otherwise
        """
        drivers = self.get_drivers_by_name(name)
        return drivers[0] if drivers else None
