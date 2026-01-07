"""Statement file model for reading and writing statement templates.

This module handles reading statement template files and writing
data to them while preserving existing formatting.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from openpyxl import Workbook
from src.utils.excel_helper import ExcelHelper
from src.models.config import Configuration


class StatementTemplate:
    """Represents a statement template file and provides writing functionality.
    
    Attributes:
        file_path: Path to the statement template file
        sheet_name: Name of the sheet to write to ('Sheet1')
        start_row: Starting row number for data input (2)
    """
    
    def __init__(self, file_path: str, config: Optional[Configuration] = None):
        """Initialize StatementTemplate.
        
        Args:
            file_path: Path to statement template Excel file
            config: Configuration object (creates new one if None)
        """
        self.file_path = Path(file_path)
        self.sheet_name: str = "Sheet1"
        self.start_row: int = 2
        
        if config is None:
            config = Configuration()
            config.load()
        self.config = config
    
    def write_data(self, row_data: List[Dict[str, Any]]) -> None:
        """Write data to E, H, J, K columns starting from row 2 with formatting preservation.
        
        This method writes the extracted settlement data to the statement
        template, preserving all existing formatting (FR-009, FR-011).
        
        Args:
            row_data: List of dictionaries containing data to write.
                     Each dict should have keys: col_c, col_i, col_j, col_k
                     
        Raises:
            FileNotFoundError: If template file doesn't exist
            KeyError: If 'Sheet1' sheet doesn't exist
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Statement template file not found: {self.file_path}")
        
        workbook = ExcelHelper.load_workbook(str(self.file_path), data_only=True)
        worksheet = ExcelHelper.get_sheet(workbook, self.sheet_name)
        
        # Get configuration (use company-specific mapping if available)
        company_name = getattr(self, 'company_name', None)
        cell_mappings = self.config.get_cell_mappings(company_name)
        output_columns = cell_mappings.get("statement_output_columns", ["E", "H", "J", "K"])
        data_columns = cell_mappings.get("settlement_data_columns", ["C", "I", "J", "K"])
        
        # Map data columns to output columns
        column_map = dict(zip(data_columns, output_columns))
        
        # Write data to each row
        for idx, data_row in enumerate(row_data):
            target_row = self.start_row + idx
            
            # Write each column
            for data_col, output_col in column_map.items():
                cell_address = f"{output_col}{target_row}"
                value = data_row.get(f"col_{data_col.lower()}")
                ExcelHelper.write_value(worksheet, cell_address, value, preserve_format=True)
        
        # Save the workbook (will be saved to new file later)
        self._workbook = workbook
        self._worksheet = worksheet
    
    def fill_additional_columns(self, year: int, month: int) -> None:
        """Fill additional columns A, B, C, D, G, I with fixed values.
        
        This method fills the additional columns required by FR-010:
        - Column A: row number starting from 1
        - Column B: selected year
        - Column C: selected month
        - Column D: 940918 (fixed)
        - Column G: 1 (fixed)
        - Column I: 3 (fixed)
        
        Args:
            year: Selected year from UI
            month: Selected month from UI
        """
        if not hasattr(self, '_worksheet'):
            raise ValueError("Must call write_data() first")
        
        worksheet = self._worksheet
        
        # Get configuration
        cell_mappings = self.config.get_cell_mappings()
        fixed_values = cell_mappings.get("statement_fixed_values", {})
        start_row = cell_mappings.get("statement_start_row", 2)
        
        # Calculate number of rows with data
        # This should match the number of rows written in write_data()
        # For now, we'll need to track this - assume it's set by write_data
        if not hasattr(self, '_data_row_count'):
            # Estimate from worksheet or use a default
            self._data_row_count = 100  # Will be updated by caller
        
        # Fill each row
        for idx in range(self._data_row_count):
            target_row = start_row + idx
            
            # Column A: row number starting from 1 (not 0)
            ExcelHelper.write_value(worksheet, f"A{target_row}", idx + 1, preserve_format=True)
            
            # Column B: year
            ExcelHelper.write_value(worksheet, f"B{target_row}", year, preserve_format=True)
            
            # Column C: month
            ExcelHelper.write_value(worksheet, f"C{target_row}", month, preserve_format=True)
            
            # Column D: 940918
            col_d_value = fixed_values.get("column_d", 940918)
            ExcelHelper.write_value(worksheet, f"D{target_row}", col_d_value, preserve_format=True)
            
            # Column G: 1
            col_g_value = fixed_values.get("column_g", 1)
            ExcelHelper.write_value(worksheet, f"G{target_row}", col_g_value, preserve_format=True)
            
            # Column I: 3
            col_i_value = fixed_values.get("column_i", 3)
            ExcelHelper.write_value(worksheet, f"I{target_row}", col_i_value, preserve_format=True)
    
    def save_as(self, output_path: str) -> None:
        """Save the modified workbook to a new file.
        
        Args:
            output_path: Path where to save the output file
            
        Raises:
            ValueError: If workbook hasn't been modified yet
        """
        if not hasattr(self, '_workbook'):
            raise ValueError("Must call write_data() first")
        
        ExcelHelper.save_workbook(self._workbook, output_path)
        self._workbook.close()
    
    def set_data_row_count(self, count: int) -> None:
        """Set the number of data rows for fill_additional_columns.
        
        Args:
            count: Number of rows with data
        """
        self._data_row_count = count

