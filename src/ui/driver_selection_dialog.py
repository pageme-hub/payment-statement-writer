"""Driver selection dialog for handling duplicate names.

This module provides a dialog window for selecting a driver
when multiple drivers match the same cleaned name.
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)
from PySide6.QtCore import Qt
from typing import List, Optional
from src.services.driver_list_reader import DriverInfo


class DriverSelectionDialog(QDialog):
    """Dialog for selecting a driver when multiple matches are found.
    
    Displays a table with driver information (name, baemin rider ID,
    coupang rider ID, resident number) and allows user to select one.
    """
    
    def __init__(self, parent=None, name: str = "", drivers: List[DriverInfo] = None):
        """Initialize driver selection dialog.
        
        Args:
            parent: Parent window
            name: Original name from settlement file
            drivers: List of DriverInfo objects matching the name
        """
        super().__init__(parent)
        self.setWindowTitle("라이더 선택")
        self.setMinimumSize(700, 400)
        
        self.name = name
        self.drivers = drivers or []
        self.selected_driver: Optional[DriverInfo] = None
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(f"'{name}' 이름과 일치하는 라이더가 여러 명 있습니다.\n원하는 라이더를 선택해주세요.")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["이름", "배플 라이더 ID", "쿠팡 라이더 ID", "주민번호"])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        # Populate table
        self.table.setRowCount(len(self.drivers))
        for row, driver in enumerate(self.drivers):
            self.table.setItem(row, 0, QTableWidgetItem(driver.name or ""))
            self.table.setItem(row, 1, QTableWidgetItem(driver.baemin_rider_id or ""))
            self.table.setItem(row, 2, QTableWidgetItem(driver.coupang_rider_id or ""))
            self.table.setItem(row, 3, QTableWidgetItem(driver.resident_number or ""))
            
            # Make items non-editable
            for col in range(4):
                item = self.table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        
        # Select first row by default
        if self.table.rowCount() > 0:
            self.table.selectRow(0)
        
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.select_button = QPushButton("선택")
        self.cancel_button = QPushButton("취소")
        self.select_button.clicked.connect(self.accept_selection)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
    
    def accept_selection(self) -> None:
        """Handle selection button click."""
        current_row = self.table.currentRow()
        if current_row < 0 or current_row >= len(self.drivers):
            QMessageBox.warning(self, "선택 오류", "라이더를 선택해주세요.")
            return
        
        self.selected_driver = self.drivers[current_row]
        self.accept()
    
    def get_selected_driver(self) -> Optional[DriverInfo]:
        """Get the selected driver.
        
        Returns:
            Selected DriverInfo, or None if dialog was cancelled
        """
        return self.selected_driver
