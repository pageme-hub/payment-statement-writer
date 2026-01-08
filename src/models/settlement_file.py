"""Settlement file model for parsing and data extraction.

This module handles parsing of settlement Excel files to extract
valid rows and data columns according to the configuration.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import re
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
        """Extract data columns for valid rows using new field mapping structure.
        
        This method reads the specified columns based on field_mappings for
        each valid row identified by parse_valid_rows(). The name column
        is used as a key column - if it's empty, the row is skipped.
        All values are read as calculated values (formula results).
        
        Also applies data processing:
        - Removes numbers from name field
        - Filters out rows where all numeric values are 0
        
        Returns:
            List of dictionaries, each containing:
            - row: Row number
            - name: Name value (with numbers removed)
            - payment: Payment value
            - income_tax: Income tax value
            - local_income_tax: Local income tax value
            
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
        
        # Get field mappings (new format) or convert from old format
        field_mappings = cell_mappings.get("field_mappings", {})
        if not field_mappings:
            # Fallback to old format conversion
            old_data_cols = cell_mappings.get("settlement_data_columns", ["C", "I", "J", "K"])
            old_output_cols = cell_mappings.get("statement_output_columns", ["E", "H", "J", "K"])
            field_mappings = {}
            if len(old_data_cols) >= 1:
                field_mappings["name"] = {"settlement_column": old_data_cols[0]}
            if len(old_data_cols) >= 2:
                field_mappings["payment"] = {"settlement_column": old_data_cols[1]}
            if len(old_data_cols) >= 3:
                field_mappings["income_tax"] = {"settlement_column": old_data_cols[2]}
            if len(old_data_cols) >= 4:
                field_mappings["local_income_tax"] = {"settlement_column": old_data_cols[3]}
        
        # Get name column (key column)
        name_mapping = field_mappings.get("name", {})
        name_column = name_mapping.get("settlement_column", "C")
        
        # Get other columns
        payment_mapping = field_mappings.get("payment", {})
        payment_column = payment_mapping.get("settlement_column", "I")
        
        income_tax_mapping = field_mappings.get("income_tax", {})
        income_tax_column = income_tax_mapping.get("settlement_column", "J")
        
        local_tax_mapping = field_mappings.get("local_income_tax", {})
        local_tax_column = local_tax_mapping.get("settlement_column", "K")
        
        self.row_data = []
        for row_num in self.valid_rows:
            # Check name column (key column) - skip if empty
            name_cell_address = f"{name_column}{row_num}"
            name_value = ExcelHelper.get_cell_value(worksheet, name_cell_address)
            
            # Skip row if name column is empty
            if name_value is None or (isinstance(name_value, str) and not name_value.strip()):
                continue
            
            # Extract all columns for this row
            payment_value = ExcelHelper.get_cell_value(worksheet, f"{payment_column}{row_num}")
            income_tax_value = ExcelHelper.get_cell_value(worksheet, f"{income_tax_column}{row_num}")
            local_tax_value = ExcelHelper.get_cell_value(worksheet, f"{local_tax_column}{row_num}")
            
            # Remove numbers from name
            cleaned_name = self._remove_numbers_from_name(str(name_value) if name_value else "")
            
            # Convert numeric values
            payment_num = self._to_numeric(payment_value)
            income_tax_num = self._to_numeric(income_tax_value)
            local_tax_num = self._to_numeric(local_tax_value)
            
            # Filter out rows where all numeric values are 0 (except name)
            if payment_num == 0 and income_tax_num == 0 and local_tax_num == 0:
                continue
            
            row_dict = {
                "row": row_num,
                "name": cleaned_name,
                "payment": payment_num,
                "income_tax": income_tax_num,
                "local_income_tax": local_tax_num
            }
            self.row_data.append(row_dict)
        
        workbook.close()
        return self.row_data
    
    def _remove_numbers_from_name(self, name: str) -> str:
        """Remove numbers from name string.
        
        Args:
            name: Name string that may contain numbers
            
        Returns:
            Name string with numbers removed
        """
        # Remove all digits from the string
        return re.sub(r'\d', '', name).strip()
    
    def _to_numeric(self, value: Any) -> float:
        """Convert value to numeric, returning 0 if conversion fails.
        
        Args:
            value: Value to convert
            
        Returns:
            Numeric value (0 if conversion fails)
        """
        if value is None:
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                # Remove commas and convert
                cleaned = value.replace(',', '').strip()
                return float(cleaned) if cleaned else 0.0
            except ValueError:
                return 0.0
        return 0.0

