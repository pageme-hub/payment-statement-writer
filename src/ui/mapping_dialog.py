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


class MappingDialog(QDialog):
    """Dialog for editing cell mappings.
    
    Allows users to edit:
    - Settlement input range
    - Settlement data columns
    - Statement output columns
    - Statement start row
    - Fixed values
    """
    
    def __init__(self, parent=None, mappings: Optional[Dict[str, Any]] = None):
        """Initialize mapping dialog.
        
        Args:
            parent: Parent window
            mappings: Current mappings to edit (uses defaults if None)
        """
        super().__init__(parent)
        self.setWindowTitle("매핑 편집")
        self.setMinimumSize(500, 400)
        
        self.mappings = mappings or self._get_default_mappings()
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
        
        # Settlement data columns
        settlement_cols_group = QGroupBox("정산서 데이터 열")
        settlement_cols_layout = QFormLayout()
        self.settlement_cols_input = QLineEdit()
        settlement_cols = self.mappings.get("settlement_data_columns", ["C", "I", "J", "K"])
        self.settlement_cols_input.setText(",".join(settlement_cols))
        settlement_cols_layout.addRow("열 (쉼표로 구분, 예: C,I,J,K):", self.settlement_cols_input)
        settlement_cols_group.setLayout(settlement_cols_layout)
        layout.addWidget(settlement_cols_group)
        
        # Statement output columns
        statement_cols_group = QGroupBox("명세서 출력 열")
        statement_cols_layout = QFormLayout()
        self.statement_cols_input = QLineEdit()
        statement_cols = self.mappings.get("statement_output_columns", ["E", "H", "J", "K"])
        self.statement_cols_input.setText(",".join(statement_cols))
        statement_cols_layout.addRow("열 (쉼표로 구분, 예: E,H,J,K):", self.statement_cols_input)
        statement_cols_group.setLayout(statement_cols_layout)
        layout.addWidget(statement_cols_group)
        
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
        
        # Fixed values
        fixed_values_group = QGroupBox("고정값")
        fixed_values_layout = QFormLayout()
        self.column_d_input = QLineEdit()
        fixed_values = self.mappings.get("statement_fixed_values", {})
        self.column_d_input.setText(str(fixed_values.get("column_d", 940918)))
        fixed_values_layout.addRow("D열 값:", self.column_d_input)
        
        self.column_g_input = QLineEdit()
        self.column_g_input.setText(str(fixed_values.get("column_g", 1)))
        fixed_values_layout.addRow("G열 값:", self.column_g_input)
        
        self.column_i_input = QLineEdit()
        self.column_i_input.setText(str(fixed_values.get("column_i", 3)))
        fixed_values_layout.addRow("I열 값:", self.column_i_input)
        
        fixed_values_group.setLayout(fixed_values_layout)
        layout.addWidget(fixed_values_group)
        
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
    
    def _get_default_mappings(self) -> Dict[str, Any]:
        """Get default mapping structure.
        
        Returns:
            Dictionary with default mappings
        """
        return {
            "settlement_input_range": "B1:B100",
            "settlement_data_columns": ["C", "I", "J", "K"],
            "statement_output_columns": ["E", "H", "J", "K"],
            "statement_start_row": 2,
            "statement_fixed_values": {
                "column_d": 940918,
                "column_g": 1,
                "column_i": 3
            }
        }
    
    def accept(self) -> None:
        """Validate and save mappings."""
        try:
            # Parse settlement data columns
            settlement_cols_str = self.settlement_cols_input.text().strip()
            settlement_cols = [col.strip().upper() for col in settlement_cols_str.split(",") if col.strip()]
            if not settlement_cols:
                raise ValueError("정산서 데이터 열을 입력해주세요.")
            
            # Parse statement output columns
            statement_cols_str = self.statement_cols_input.text().strip()
            statement_cols = [col.strip().upper() for col in statement_cols_str.split(",") if col.strip()]
            if not statement_cols:
                raise ValueError("명세서 출력 열을 입력해주세요.")
            
            if len(settlement_cols) != len(statement_cols):
                raise ValueError("정산서 데이터 열과 명세서 출력 열의 개수가 일치해야 합니다.")
            
            # Parse fixed values
            try:
                column_d = int(self.column_d_input.text().strip())
            except ValueError:
                raise ValueError("D열 값은 숫자여야 합니다.")
            
            try:
                column_g = int(self.column_g_input.text().strip())
            except ValueError:
                raise ValueError("G열 값은 숫자여야 합니다.")
            
            try:
                column_i = int(self.column_i_input.text().strip())
            except ValueError:
                raise ValueError("I열 값은 숫자여야 합니다.")
            
            # Build result mappings
            self.result_mappings = {
                "settlement_input_range": self.range_input.text().strip(),
                "settlement_data_columns": settlement_cols,
                "statement_output_columns": statement_cols,
                "statement_start_row": self.start_row_spin.value(),
                "statement_fixed_values": {
                    "column_d": column_d,
                    "column_g": column_g,
                    "column_i": column_i
                }
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

