"""Mapping editor dialog for editing cell mappings.

This module provides a dialog window for editing cell mappings
for settlement and statement files.
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QGroupBox,
    QFormLayout,
    QSpinBox,
)
from PySide6.QtCore import Qt
from typing import Dict, Any, List, Optional
import re


class MappingDialog(QDialog):
    """Dialog for editing cell mappings.
    
    Allows users to edit:
    - Field mappings (name, resident_number, payment, income_tax, local_income_tax)
    - Fixed values (business_code, resident_status, tax_rate)
    - Settlement input range
    - Statement start row
    """
    
    def __init__(self, parent=None, mappings: Optional[Dict[str, Any]] = None):
        """Initialize mapping dialog.
        
        Args:
            parent: Parent window
            mappings: Current mappings to edit (uses defaults if None)
        """
        super().__init__(parent)
        self.setWindowTitle("매핑 편집")
        self.setMinimumSize(600, 700)
        
        # Convert old format to new format if needed
        self.mappings = mappings or self._get_default_mappings()
        self.mappings = self._convert_to_new_format(self.mappings)
        self.result_mappings: Optional[Dict[str, Any]] = None
        
        layout = QVBoxLayout(self)
        
        # Settlement input range
        range_group = QGroupBox("정산서 입력 범위")
        range_layout = QFormLayout()
        self.range_input = QLineEdit()
        self.range_input.setText(self.mappings.get("settlement_input_range", "B1:B100"))
        range_layout.addRow("범위 (예: B1:B100):", self.range_input)
        range_group.setLayout(range_layout)
        layout.addWidget(range_group)
        
        # Statement start row
        start_row_group = QGroupBox("명세서 시작 행")
        start_row_layout = QFormLayout()
        self.start_row_spin = QSpinBox()
        self.start_row_spin.setMinimum(1)
        self.start_row_spin.setMaximum(1000)
        self.start_row_spin.setValue(self.mappings.get("statement_start_row", 2))
        start_row_layout.addRow("시작 행 번호:", self.start_row_spin)
        start_row_group.setLayout(start_row_layout)
        layout.addWidget(start_row_group)
        
        # Field mappings
        field_mappings = self.mappings.get("field_mappings", {})
        
        # 이름
        name_group = QGroupBox("이름")
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("정산서 열:"))
        self.name_settlement_input = QLineEdit()
        name_mapping = field_mappings.get("name", {})
        self.name_settlement_input.setText(name_mapping.get("settlement_column", ""))
        self.name_settlement_input.setMaximumWidth(50)
        name_layout.addWidget(self.name_settlement_input)
        name_layout.addWidget(QLabel("명세서 열:"))
        self.name_statement_input = QLineEdit()
        self.name_statement_input.setText(name_mapping.get("statement_column", "E"))
        self.name_statement_input.setMaximumWidth(50)
        name_layout.addWidget(self.name_statement_input)
        name_layout.addStretch()
        name_group.setLayout(name_layout)
        layout.addWidget(name_group)
        
        # 주민번호
        resident_group = QGroupBox("주민번호")
        resident_layout = QHBoxLayout()
        resident_layout.addWidget(QLabel("명세서 열:"))
        self.resident_statement_input = QLineEdit()
        resident_mapping = field_mappings.get("resident_number", {})
        self.resident_statement_input.setText(resident_mapping.get("statement_column", "F"))
        self.resident_statement_input.setMaximumWidth(50)
        resident_layout.addWidget(self.resident_statement_input)
        resident_layout.addStretch()
        resident_group.setLayout(resident_layout)
        layout.addWidget(resident_group)
        
        # 지급액
        payment_group = QGroupBox("지급액")
        payment_layout = QHBoxLayout()
        payment_layout.addWidget(QLabel("정산서 열:"))
        self.payment_settlement_input = QLineEdit()
        payment_mapping = field_mappings.get("payment", {})
        self.payment_settlement_input.setText(payment_mapping.get("settlement_column", ""))
        self.payment_settlement_input.setMaximumWidth(50)
        payment_layout.addWidget(self.payment_settlement_input)
        payment_layout.addWidget(QLabel("명세서 열:"))
        self.payment_statement_input = QLineEdit()
        self.payment_statement_input.setText(payment_mapping.get("statement_column", "H"))
        self.payment_statement_input.setMaximumWidth(50)
        payment_layout.addWidget(self.payment_statement_input)
        payment_layout.addStretch()
        payment_group.setLayout(payment_layout)
        layout.addWidget(payment_group)
        
        # 소득세
        income_tax_group = QGroupBox("소득세")
        income_tax_layout = QHBoxLayout()
        income_tax_layout.addWidget(QLabel("정산서 열:"))
        self.income_tax_settlement_input = QLineEdit()
        income_tax_mapping = field_mappings.get("income_tax", {})
        self.income_tax_settlement_input.setText(income_tax_mapping.get("settlement_column", ""))
        self.income_tax_settlement_input.setMaximumWidth(50)
        income_tax_layout.addWidget(self.income_tax_settlement_input)
        income_tax_layout.addWidget(QLabel("명세서 열:"))
        self.income_tax_statement_input = QLineEdit()
        self.income_tax_statement_input.setText(income_tax_mapping.get("statement_column", "J"))
        self.income_tax_statement_input.setMaximumWidth(50)
        income_tax_layout.addWidget(self.income_tax_statement_input)
        income_tax_layout.addStretch()
        income_tax_group.setLayout(income_tax_layout)
        layout.addWidget(income_tax_group)
        
        # 지방소득세
        local_tax_group = QGroupBox("지방소득세")
        local_tax_layout = QHBoxLayout()
        local_tax_layout.addWidget(QLabel("정산서 열:"))
        self.local_tax_settlement_input = QLineEdit()
        local_tax_mapping = field_mappings.get("local_income_tax", {})
        self.local_tax_settlement_input.setText(local_tax_mapping.get("settlement_column", ""))
        self.local_tax_settlement_input.setMaximumWidth(50)
        local_tax_layout.addWidget(self.local_tax_settlement_input)
        local_tax_layout.addWidget(QLabel("명세서 열:"))
        self.local_tax_statement_input = QLineEdit()
        self.local_tax_statement_input.setText(local_tax_mapping.get("statement_column", "K"))
        self.local_tax_statement_input.setMaximumWidth(50)
        local_tax_layout.addWidget(self.local_tax_statement_input)
        local_tax_layout.addStretch()
        local_tax_group.setLayout(local_tax_layout)
        layout.addWidget(local_tax_group)
        
        # Fixed values
        fixed_values = self.mappings.get("fixed_values", {})
        fixed_group = QGroupBox("고정값")
        fixed_layout = QFormLayout()
        
        # 업종코드
        business_code_layout = QHBoxLayout()
        business_code_layout.addWidget(QLabel("열:"))
        self.business_code_col_input = QLineEdit()
        business_code = fixed_values.get("business_code", {})
        self.business_code_col_input.setText(business_code.get("column", "D"))
        self.business_code_col_input.setMaximumWidth(50)
        business_code_layout.addWidget(self.business_code_col_input)
        business_code_layout.addWidget(QLabel("값:"))
        self.business_code_value_input = QLineEdit()
        self.business_code_value_input.setText(str(business_code.get("value", 940918)))
        business_code_layout.addWidget(self.business_code_value_input)
        business_code_layout.addStretch()
        fixed_layout.addRow("업종코드", business_code_layout)
        
        # 내외국인
        resident_status_layout = QHBoxLayout()
        resident_status_layout.addWidget(QLabel("열:"))
        self.resident_status_col_input = QLineEdit()
        resident_status = fixed_values.get("resident_status", {})
        self.resident_status_col_input.setText(resident_status.get("column", "G"))
        self.resident_status_col_input.setMaximumWidth(50)
        resident_status_layout.addWidget(self.resident_status_col_input)
        resident_status_layout.addWidget(QLabel("값:"))
        self.resident_status_value_input = QLineEdit()
        self.resident_status_value_input.setText(str(resident_status.get("value", 1)))
        resident_status_layout.addWidget(self.resident_status_value_input)
        resident_status_layout.addStretch()
        fixed_layout.addRow("내외국인", resident_status_layout)
        
        # 세율
        tax_rate_layout = QHBoxLayout()
        tax_rate_layout.addWidget(QLabel("열:"))
        self.tax_rate_col_input = QLineEdit()
        tax_rate = fixed_values.get("tax_rate", {})
        self.tax_rate_col_input.setText(tax_rate.get("column", "I"))
        self.tax_rate_col_input.setMaximumWidth(50)
        tax_rate_layout.addWidget(self.tax_rate_col_input)
        tax_rate_layout.addWidget(QLabel("값:"))
        self.tax_rate_value_input = QLineEdit()
        self.tax_rate_value_input.setText(str(tax_rate.get("value", 3)))
        tax_rate_layout.addWidget(self.tax_rate_value_input)
        tax_rate_layout.addStretch()
        fixed_layout.addRow("세율", tax_rate_layout)
        
        fixed_group.setLayout(fixed_layout)
        layout.addWidget(fixed_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.save_button = QPushButton("저장")
        self.cancel_button = QPushButton("취소")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
    
    def _convert_to_new_format(self, mappings: Dict[str, Any]) -> Dict[str, Any]:
        """Convert old format to new format if needed.
        
        Args:
            mappings: Mappings in old or new format
            
        Returns:
            Mappings in new format
        """
        # If already in new format, return as is
        if "field_mappings" in mappings:
            return mappings
        
        # Convert from old format
        old_data_cols = mappings.get("settlement_data_columns", ["C", "I", "J", "K"])
        old_output_cols = mappings.get("statement_output_columns", ["E", "H", "J", "K"])
        old_fixed = mappings.get("statement_fixed_values", {})
        
        field_mappings = {}
        if len(old_data_cols) >= 1 and len(old_output_cols) >= 1:
            field_mappings["name"] = {
                "settlement_column": old_data_cols[0],
                "statement_column": old_output_cols[0]
            }
        if len(old_data_cols) >= 2 and len(old_output_cols) >= 2:
            field_mappings["payment"] = {
                "settlement_column": old_data_cols[1],
                "statement_column": old_output_cols[1]
            }
        if len(old_data_cols) >= 3 and len(old_output_cols) >= 3:
            field_mappings["income_tax"] = {
                "settlement_column": old_data_cols[2],
                "statement_column": old_output_cols[2]
            }
        if len(old_data_cols) >= 4 and len(old_output_cols) >= 4:
            field_mappings["local_income_tax"] = {
                "settlement_column": old_data_cols[3],
                "statement_column": old_output_cols[3]
            }
        
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
        
        return {
            "settlement_input_range": mappings.get("settlement_input_range", "B1:B100"),
            "statement_start_row": mappings.get("statement_start_row", 2),
            "field_mappings": field_mappings,
            "fixed_values": fixed_values
        }
    
    def _get_default_mappings(self) -> Dict[str, Any]:
        """Get default mapping structure.
        
        Returns:
            Dictionary with default mappings
        """
        return {
            "settlement_input_range": "B1:B100",
            "statement_start_row": 2,
            "field_mappings": {
                "name": {
                    "settlement_column": "C",
                    "statement_column": "E"
                },
                "resident_number": {
                    "driver_list_column": "A",
                    "statement_column": "F"
                },
                "payment": {
                    "settlement_column": "I",
                    "statement_column": "H"
                },
                "income_tax": {
                    "settlement_column": "J",
                    "statement_column": "J"
                },
                "local_income_tax": {
                    "settlement_column": "K",
                    "statement_column": "K"
                }
            },
            "fixed_values": {
                "business_code": {
                    "column": "D",
                    "value": 940918
                },
                "resident_status": {
                    "column": "G",
                    "value": 1
                },
                "tax_rate": {
                    "column": "I",
                    "value": 3
                }
            }
        }
    
    def _validate_column(self, col_str: str) -> bool:
        """Validate column string (e.g., 'A', 'B', 'AA').
        
        Args:
            col_str: Column string to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not col_str:
            return False
        col_str = col_str.strip().upper()
        # Column should be one or more letters
        return bool(re.match(r'^[A-Z]+$', col_str))
    
    def accept(self) -> None:
        """Validate and save mappings."""
        try:
            # Validate settlement input range
            range_str = self.range_input.text().strip()
            if not range_str or ':' not in range_str:
                raise ValueError("정산서 입력 범위를 올바르게 입력해주세요 (예: B1:B100)")
            
            # Validate and collect field mappings
            field_mappings = {}
            
            # Name
            name_settlement = self.name_settlement_input.text().strip().upper()
            name_statement = self.name_statement_input.text().strip().upper()
            if not self._validate_column(name_settlement) or not self._validate_column(name_statement):
                raise ValueError("이름의 정산서 열과 명세서 열을 올바르게 입력해주세요")
            field_mappings["name"] = {
                "settlement_column": name_settlement,
                "statement_column": name_statement
            }
            
            # Resident number
            resident_statement = self.resident_statement_input.text().strip().upper()
            if not self._validate_column(resident_statement):
                raise ValueError("주민번호의 명세서 열을 올바르게 입력해주세요")
            field_mappings["resident_number"] = {
                "statement_column": resident_statement
            }
            
            # Payment
            payment_settlement = self.payment_settlement_input.text().strip().upper()
            payment_statement = self.payment_statement_input.text().strip().upper()
            if not self._validate_column(payment_settlement) or not self._validate_column(payment_statement):
                raise ValueError("지급액의 정산서 열과 명세서 열을 올바르게 입력해주세요")
            field_mappings["payment"] = {
                "settlement_column": payment_settlement,
                "statement_column": payment_statement
            }
            
            # Income tax
            income_tax_settlement = self.income_tax_settlement_input.text().strip().upper()
            income_tax_statement = self.income_tax_statement_input.text().strip().upper()
            if not self._validate_column(income_tax_settlement) or not self._validate_column(income_tax_statement):
                raise ValueError("소득세의 정산서 열과 명세서 열을 올바르게 입력해주세요")
            field_mappings["income_tax"] = {
                "settlement_column": income_tax_settlement,
                "statement_column": income_tax_statement
            }
            
            # Local income tax
            local_tax_settlement = self.local_tax_settlement_input.text().strip().upper()
            local_tax_statement = self.local_tax_statement_input.text().strip().upper()
            if not self._validate_column(local_tax_settlement) or not self._validate_column(local_tax_statement):
                raise ValueError("지방소득세의 정산서 열과 명세서 열을 올바르게 입력해주세요")
            field_mappings["local_income_tax"] = {
                "settlement_column": local_tax_settlement,
                "statement_column": local_tax_statement
            }
            
            # Validate and collect fixed values
            fixed_values = {}
            
            # Business code
            business_code_col = self.business_code_col_input.text().strip().upper()
            if not self._validate_column(business_code_col):
                raise ValueError("업종코드의 열을 올바르게 입력해주세요")
            try:
                business_code_value = int(self.business_code_value_input.text().strip())
            except ValueError:
                raise ValueError("업종코드의 값은 숫자여야 합니다")
            fixed_values["business_code"] = {
                "column": business_code_col,
                "value": business_code_value
            }
            
            # Resident status
            resident_status_col = self.resident_status_col_input.text().strip().upper()
            if not self._validate_column(resident_status_col):
                raise ValueError("내외국인의 열을 올바르게 입력해주세요")
            try:
                resident_status_value = int(self.resident_status_value_input.text().strip())
            except ValueError:
                raise ValueError("내외국인의 값은 숫자여야 합니다")
            fixed_values["resident_status"] = {
                "column": resident_status_col,
                "value": resident_status_value
            }
            
            # Tax rate
            tax_rate_col = self.tax_rate_col_input.text().strip().upper()
            if not self._validate_column(tax_rate_col):
                raise ValueError("세율의 열을 올바르게 입력해주세요")
            try:
                tax_rate_value = int(self.tax_rate_value_input.text().strip())
            except ValueError:
                raise ValueError("세율의 값은 숫자여야 합니다")
            fixed_values["tax_rate"] = {
                "column": tax_rate_col,
                "value": tax_rate_value
            }
            
            # Build result mappings
            self.result_mappings = {
                "settlement_input_range": range_str,
                "statement_start_row": self.start_row_spin.value(),
                "field_mappings": field_mappings,
                "fixed_values": fixed_values
            }
            
            super().accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "입력 오류", str(e))
    
    def get_mappings(self) -> Optional[Dict[str, Any]]:
        """Get edited mappings.
        
        Returns:
            Dictionary with edited mappings, or None if dialog was cancelled
        """
        return self.result_mappings
