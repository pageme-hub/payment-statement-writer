"""Excel file manipulation utilities using openpyxl.

This module provides wrapper functions around openpyxl to handle
Excel file reading and writing while preserving formatting.
"""

from pathlib import Path
from typing import List, Any, Optional
import openpyxl
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet


class ExcelHelper:
    """Utility class for Excel file operations with formatting preservation.
    
    This class wraps openpyxl functionality to provide a simple interface
    for reading and writing Excel files while maintaining existing formatting
    (FR-011, SC-003).
    """
    
    @staticmethod
    def load_workbook(file_path: str, data_only: bool = False) -> Workbook:
        """Load an Excel workbook from file path.
        
        Args:
            file_path: Path to Excel file
            data_only: If True, read calculated values instead of formulas
            
        Returns:
            openpyxl Workbook object
            
        Raises:
            FileNotFoundError: If file doesn't exist
            openpyxl.utils.exceptions.InvalidFileException: If file is not a valid Excel file
        """
        return load_workbook(file_path, data_only=data_only)
    
    @staticmethod
    def get_sheet(workbook: Workbook, sheet_name: str) -> Worksheet:
        """Get a worksheet by name from workbook.
        
        Args:
            workbook: openpyxl Workbook object
            sheet_name: Name of the sheet to retrieve
            
        Returns:
            Worksheet object
            
        Raises:
            KeyError: If sheet doesn't exist
        """
        return workbook[sheet_name]
    
    @staticmethod
    def read_range(worksheet: Worksheet, range_str: str) -> List[Any]:
        """Read values from a cell range.
        
        Args:
            worksheet: Worksheet to read from
            range_str: Excel range string (e.g., 'B1:B100')
            
        Returns:
            List of cell values in the range
        """
        cells = worksheet[range_str]
        values = []
        for row in cells:
            for cell in row:
                values.append(cell.value)
        return values
    
    @staticmethod
    def read_column(worksheet: Worksheet, column: str, start_row: int, end_row: int) -> List[Any]:
        """Read values from a column range.
        
        Args:
            worksheet: Worksheet to read from
            column: Column letter (e.g., 'B', 'C')
            start_row: Starting row number (1-based)
            end_row: Ending row number (1-based)
            
        Returns:
            List of cell values in the column range (calculated values, not formulas)
        """
        values = []
        for row_num in range(start_row, end_row + 1):
            cell = worksheet[f"{column}{row_num}"]
            # Get calculated value (formula result), not the formula itself
            values.append(cell.value)
        return values
    
    @staticmethod
    def get_cell_value(worksheet: Worksheet, cell_address: str) -> Any:
        """Get calculated value from a cell (formula result, not formula).
        
        Args:
            worksheet: Worksheet to read from
            cell_address: Cell address (e.g., 'A1', 'B2')
            
        Returns:
            Calculated value from the cell (None if empty)
        """
        cell = worksheet[cell_address]
        return cell.value
    
    @staticmethod
    def write_value(worksheet: Worksheet, cell_address: str, value: Any, preserve_format: bool = True) -> None:
        """Write a value to a cell while preserving formatting.
        
        Args:
            worksheet: Worksheet to write to
            cell_address: Cell address (e.g., 'A1', 'B2')
            value: Value to write
            preserve_format: If True, preserve existing cell formatting
        """
        cell = worksheet[cell_address]
        if preserve_format:
            # openpyxl은 셀의 value를 변경해도 기본적으로 서식이 유지됩니다.
            # StyleProxy 에러를 방지하기 위해 서식을 명시적으로 복사하지 않고
            # value만 변경합니다. 이렇게 하면 기존 서식이 자동으로 유지됩니다.
            cell.value = value
        else:
            cell.value = value
    
    @staticmethod
    def save_workbook(workbook: Workbook, file_path: str) -> None:
        """Save workbook to file.
        
        Args:
            workbook: openpyxl Workbook to save
            file_path: Path where to save the file
            
        Raises:
            PermissionError: If file is open or cannot be written
        """
        workbook.save(file_path)
    
    @staticmethod
    def copy_worksheet_format(source_ws: Worksheet, target_ws: Worksheet) -> None:
        """Copy formatting from source worksheet to target worksheet.
        
        This method copies cell formatting (fonts, fills, borders, etc.)
        to preserve the template's appearance.
        
        Args:
            source_ws: Source worksheet to copy formatting from
            target_ws: Target worksheet to apply formatting to
        """
        for row in source_ws.iter_rows():
            for cell in row:
                target_cell = target_ws[cell.coordinate]
                target_cell.fill = cell.fill
                target_cell.font = cell.font
                target_cell.border = cell.border
                target_cell.alignment = cell.alignment
                target_cell.number_format = cell.number_format

