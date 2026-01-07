"""Settlement file model for parsing and data extraction.

This module handles parsing of settlement Excel files to extract
valid rows and data columns according to the configuration.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from src.utils.excel_helper import ExcelHelper
from src.models.config import Configuration


class SettlementFile:
    """Represents a settlement file and provides parsing functionality.
    
    Attributes:
        file_path: Path to the settlement file
        company_name: Company name extracted from filename
        month: Month extracted from filename
        week: Week extracted from filename
        sheet_name: Name of the sheet to read ('월간정산')
        valid_rows: List of row numbers with valid data (B column >= 1)
        row_data: List of dictionaries containing extracted data
    """
    
    def __init__(self, file_path: str, config: Optional[Configuration] = None):
        """Initialize SettlementFile.
        
        Args:
            file_path: Path to settlement Excel file
            config: Configuration object (creates new one if None)
        """
        self.file_path = Path(file_path)
        self.company_name: str = ""
        self.month: int = 0
        self.week: int = 0
        self.sheet_name: str = "월간정산"
        self.valid_rows: List[int] = []
        self.row_data: List[Dict[str, Any]] = []
        
        if config is None:
            config = Configuration()
            config.load()
        self.config = config
    
    def parse_valid_rows(self) -> List[int]:
        """Extract rows with B column value >= 1 from B1:B100 range.
        
        This method scans the B column (B1:B100) to find rows where
        the value is a number >= 1. These rows are considered valid
        for data extraction (FR-007).
        
        Returns:
            List of row numbers (1-based) with valid data
            
        Raises:
            FileNotFoundError: If settlement file doesn't exist
            KeyError: If '월간정산' sheet doesn't exist
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Settlement file not found: {self.file_path}")
        
        workbook = ExcelHelper.load_workbook(str(self.file_path), data_only=True)
        worksheet = ExcelHelper.get_sheet(workbook, self.sheet_name)
        
        # Get configuration (use company-specific mapping if available)
        company_name = getattr(self, 'company_name', None)
        cell_mappings = self.config.get_cell_mappings(company_name)
        input_range = cell_mappings.get("settlement_input_range", "B1:B100")
        
        # Parse range (e.g., "B1:B100")
        range_parts = input_range.split(":")
        start_col = range_parts[0][0]  # 'B'
        start_row = int(range_parts[0][1:])  # 1
        end_row = int(range_parts[1][1:])  # 100
        
        # Read B column values
        values = ExcelHelper.read_column(worksheet, start_col, start_row, end_row)
        
        # Find rows with value >= 1
        self.valid_rows = []
        for idx, value in enumerate(values, start=start_row):
            if isinstance(value, (int, float)) and value >= 1:
                self.valid_rows.append(idx)
        
        workbook.close()
        return self.valid_rows
    
    def parse_data_columns(self) -> List[Dict[str, Any]]:
        """Extract C, I, J, K columns for valid rows only.
        
        This method reads the specified columns (C, I, J, K) for
        each valid row identified by parse_valid_rows(). The first column
        (C) is used as a key column - if it's empty, the row is skipped.
        All values are read as calculated values (formula results).
        
        Returns:
            List of dictionaries, each containing:
            - row: Row number
            - col_c: Value from column C (key column)
            - col_i: Value from column I
            - col_j: Value from column J
            - col_k: Value from column K
            
        Raises:
            ValueError: If valid_rows is empty (must call parse_valid_rows first)
        """
        if not self.valid_rows:
            raise ValueError("Must call parse_valid_rows() first")
        
        workbook = ExcelHelper.load_workbook(str(self.file_path), data_only=True)
        worksheet = ExcelHelper.get_sheet(workbook, self.sheet_name)
        
        # Get configuration
        company_name = getattr(self, 'company_name', None)
        cell_mappings = self.config.get_cell_mappings(company_name)
        data_columns = cell_mappings.get("settlement_data_columns", ["C", "I", "J", "K"])
        
        if not data_columns:
            raise ValueError("settlement_data_columns must contain at least one column")
        
        # First column is the key column
        key_column = data_columns[0]
        
        self.row_data = []
        for row_num in self.valid_rows:
            # Check key column (first column) - skip if empty
            key_cell_address = f"{key_column}{row_num}"
            key_value = ExcelHelper.get_cell_value(worksheet, key_cell_address)
            
            # Skip row if key column is empty
            if key_value is None or (isinstance(key_value, str) and not key_value.strip()):
                continue
            
            # Extract all columns for this row
            row_dict = {"row": row_num}
            for col in data_columns:
                cell_address = f"{col}{row_num}"
                value = ExcelHelper.get_cell_value(worksheet, cell_address)
                row_dict[f"col_{col.lower()}"] = value
            self.row_data.append(row_dict)
        
        workbook.close()
        return self.row_data

