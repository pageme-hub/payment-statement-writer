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
    
    def write_data(self, row_data: List[Dict[str, Any]], driver_list_data: Optional[Dict[str, str]] = None) -> None:
        """Write data to statement columns using new field mapping structure.
        
        This method writes the extracted settlement data to the statement
        template, preserving all existing formatting (FR-009, FR-011).
        
        Args:
            row_data: List of dictionaries containing data to write.
                     Each dict should have keys: name, payment, income_tax, local_income_tax
            driver_list_data: Dictionary mapping names to resident numbers (optional)
                     
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
        
        # Get field mappings (new format) or convert from old format
        field_mappings = cell_mappings.get("field_mappings", {})
        if not field_mappings:
            # Fallback to old format conversion
            old_data_cols = cell_mappings.get("settlement_data_columns", ["C", "I", "J", "K"])
            old_output_cols = cell_mappings.get("statement_output_columns", ["E", "H", "J", "K"])
            field_mappings = {}
            if len(old_data_cols) >= 1 and len(old_output_cols) >= 1:
                field_mappings["name"] = {"statement_column": old_output_cols[0]}
            if len(old_data_cols) >= 2 and len(old_output_cols) >= 2:
                field_mappings["payment"] = {"statement_column": old_output_cols[1]}
            if len(old_data_cols) >= 3 and len(old_output_cols) >= 3:
                field_mappings["income_tax"] = {"statement_column": old_output_cols[2]}
            if len(old_data_cols) >= 4 and len(old_output_cols) >= 4:
                field_mappings["local_income_tax"] = {"statement_column": old_output_cols[3]}
        
        # Get statement columns from field mappings
        name_col = field_mappings.get("name", {}).get("statement_column", "E")
        resident_number_col = field_mappings.get("resident_number", {}).get("statement_column", "F")
        payment_col = field_mappings.get("payment", {}).get("statement_column", "H")
        income_tax_col = field_mappings.get("income_tax", {}).get("statement_column", "J")
        local_tax_col = field_mappings.get("local_income_tax", {}).get("statement_column", "K")
        
        # Get start row
        start_row = cell_mappings.get("statement_start_row", 2)
        
        # Write data to each row
        for idx, data_row in enumerate(row_data):
            target_row = start_row + idx
            
            # Write name
            ExcelHelper.write_value(worksheet, f"{name_col}{target_row}", data_row.get("name"), preserve_format=True)
            
            # Write resident number (from driver list if available)
            if driver_list_data:
                name = data_row.get("name", "")
                resident_number = driver_list_data.get(name, "")
                ExcelHelper.write_value(worksheet, f"{resident_number_col}{target_row}", resident_number, preserve_format=True)
            
            # Write payment
            ExcelHelper.write_value(worksheet, f"{payment_col}{target_row}", data_row.get("payment"), preserve_format=True)
            
            # Write income tax
            ExcelHelper.write_value(worksheet, f"{income_tax_col}{target_row}", data_row.get("income_tax"), preserve_format=True)
            
            # Write local income tax
            ExcelHelper.write_value(worksheet, f"{local_tax_col}{target_row}", data_row.get("local_income_tax"), preserve_format=True)
        
        # Save the workbook (will be saved to new file later)
        self._workbook = workbook
        self._worksheet = worksheet
    
    def fill_additional_columns(self, year: int, month: int) -> None:
        """Fill additional columns A, B, C and fixed value columns.
        
        This method fills the additional columns:
        - Column A: row number starting from 1
        - Column B: selected year
        - Column C: selected month
        - Fixed value columns (from fixed_values mapping)
        
        Args:
            year: Selected year from UI
            month: Selected month from UI
        """
        if not hasattr(self, '_worksheet'):
            raise ValueError("Must call write_data() first")
        
        worksheet = self._worksheet
        
        # Get configuration
        company_name = getattr(self, 'company_name', None)
        cell_mappings = self.config.get_cell_mappings(company_name)
        
        # Get fixed values (new format) or convert from old format
        fixed_values = cell_mappings.get("fixed_values", {})
        if not fixed_values:
            # Fallback to old format conversion
            old_fixed = cell_mappings.get("statement_fixed_values", {})
            fixed_values = {
                "business_code": {
                    "column": "D",
                    "value": old_fixed.get("column_d", 940918)
                },
                "resident_status": {
                    "column": "G",
                    "value": old_fixed.get("column_g", 1)
                },
                "tax_rate": {
                    "column": "I",
                    "value": old_fixed.get("column_i", 3)
                }
            }
        
        start_row = cell_mappings.get("statement_start_row", 2)
        
        # Calculate number of rows with data
        if not hasattr(self, '_data_row_count'):
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
            
            # Fixed values
            business_code = fixed_values.get("business_code", {})
            if business_code:
                col = business_code.get("column", "D")
                value = business_code.get("value", 940918)
                ExcelHelper.write_value(worksheet, f"{col}{target_row}", value, preserve_format=True)
            
            resident_status = fixed_values.get("resident_status", {})
            if resident_status:
                col = resident_status.get("column", "G")
                value = resident_status.get("value", 1)
                ExcelHelper.write_value(worksheet, f"{col}{target_row}", value, preserve_format=True)
            
            tax_rate = fixed_values.get("tax_rate", {})
            if tax_rate:
                col = tax_rate.get("column", "I")
                value = tax_rate.get("value", 3)
                ExcelHelper.write_value(worksheet, f"{col}{target_row}", value, preserve_format=True)
    
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

