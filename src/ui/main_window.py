"""Main window for the payment statement writer application.

This module contains the PySide6 main window implementation
with file selection, year/month selection, and processing controls.
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QDialog,
)
from PySide6.QtCore import Qt, QThread, Signal
from pathlib import Path
from src.models.config import Configuration
from src.services.file_processor import FileProcessor
from src.services.filename_parser import FilenameParser
from src.ui.mapping_dialog import MappingDialog
from datetime import datetime


class MainWindow(QMainWindow):
    """Main application window.
    
    Provides UI for:
    - Settlement file selection (FR-001)
    - Statement template file selection (FR-002)
    - Year and month selection (FR-004)
    - Start work button (FR-019)
    - Progress log display (FR-018)
    """
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.setWindowTitle("간이지급명세서 자동입력기")
        self.setMinimumSize(600, 500)
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Company name selection
        company_group = QHBoxLayout()
        company_label = QLabel("업체명:")
        self.company_combo = QComboBox()
        self.company_combo.setEditable(True)
        self.company_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        company_group.addWidget(company_label)
        company_group.addWidget(self.company_combo)
        company_group.addStretch()
        layout.addLayout(company_group)
        
        # File selection section - Settlement file
        settlement_group = QVBoxLayout()
        settlement_label = QLabel("정산서 파일:")
        self.settlement_path_label = QLabel("선택된 파일 없음")
        self.settlement_path_label.setWordWrap(True)
        self.settlement_button = QPushButton("정산서 파일 선택")
        settlement_group.addWidget(settlement_label)
        settlement_group.addWidget(self.settlement_path_label)
        settlement_group.addWidget(self.settlement_button)
        layout.addLayout(settlement_group)
        
        # File selection section - Statement template file
        statement_group = QVBoxLayout()
        statement_label = QLabel("명세서 파일:")
        self.statement_path_label = QLabel("선택된 파일 없음")
        self.statement_path_label.setWordWrap(True)
        self.statement_button = QPushButton("명세서 파일 선택")
        statement_explanation = QLabel("명세서 템플릿 파일을 선택하세요.")
        statement_explanation.setStyleSheet("color: gray; font-size: 10pt;")
        statement_group.addWidget(statement_label)
        statement_group.addWidget(self.statement_path_label)
        statement_group.addWidget(self.statement_button)
        statement_group.addWidget(statement_explanation)
        layout.addLayout(statement_group)
        
        # Year and month selection
        date_group = QHBoxLayout()
        year_label = QLabel("년도:")
        self.year_combo = QComboBox()
        # Populate with recent years
        current_year = 2024
        for year in range(current_year - 2, current_year + 3):
            self.year_combo.addItem(str(year), year)
        self.year_combo.setCurrentText(str(current_year))
        
        month_label = QLabel("월:")
        self.month_combo = QComboBox()
        for month in range(1, 13):
            self.month_combo.addItem(f"{month}월", month)
        
        date_group.addWidget(year_label)
        date_group.addWidget(self.year_combo)
        date_group.addWidget(month_label)
        date_group.addWidget(self.month_combo)
        date_group.addStretch()
        layout.addLayout(date_group)
        
        # Mapping edit button
        self.mapping_button = QPushButton("매핑 편집")
        layout.addWidget(self.mapping_button)
        
        # Start work button
        self.start_button = QPushButton("작업 시작")
        self.start_button.setMinimumHeight(40)
        layout.addWidget(self.start_button)
        
        # Progress log
        log_label = QLabel("작업 현황:")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(log_label)
        layout.addWidget(self.log_text)
        
        # Initialize configuration and file paths
        self.config = Configuration()
        self.config.load()
        self.settlement_path: str = ""
        self.statement_template_path: str = ""
        
        # Load statement template path from config (FR-017)
        self._load_statement_template_path()
        
        # Load company list and set current company
        self._load_company_list()
        
        # Connect signals
        self.settlement_button.clicked.connect(self.select_settlement_file)
        self.statement_button.clicked.connect(self.select_statement_file)
        self.company_combo.currentTextChanged.connect(self._on_company_changed)
        self.mapping_button.clicked.connect(self.edit_mapping)
        self.start_button.clicked.connect(self.start_processing)
    
    def _load_statement_template_path(self) -> None:
        """Load statement template path from setting.json on startup (FR-017)."""
        template_path = self.config.get_statement_template_path()
        if template_path and Path(template_path).exists():
            self.statement_template_path = template_path
            self.statement_path_label.setText(template_path)
            self.log_message(f"명세서 템플릿 파일 자동 로드: {template_path}")
    
    def select_settlement_file(self) -> None:
        """Handle settlement file selection (FR-001)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "정산서 파일 선택",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        if file_path:
            self.settlement_path = file_path
            self.settlement_path_label.setText(file_path)
            self.log_message(f"정산서 파일 선택: {file_path}")
            
            # Auto-extract month and suggest year (FR-005, FR-006)
            self._auto_set_year_month(file_path)
    
    def select_statement_file(self) -> None:
        """Handle statement template file selection (FR-002)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "명세서 템플릿 파일 선택",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        if file_path:
            self.statement_template_path = file_path
            self.statement_path_label.setText(file_path)
            self.log_message(f"명세서 템플릿 파일 선택: {file_path}")
            
            # Save to setting.json (FR-016)
            self.config.set_statement_template_path(file_path)
            self.config.save()
            self.log_message("명세서 파일 경로가 설정에 저장되었습니다.")
    
    def _load_company_list(self) -> None:
        """Load company list from configuration and populate combo box."""
        companies = self.config.get_company_list()
        self.company_combo.clear()
        self.company_combo.addItems(companies)
        
        # Set current company if exists
        current_company = self.config.get_current_company()
        if current_company:
            index = self.company_combo.findText(current_company)
            if index >= 0:
                self.company_combo.setCurrentIndex(index)
            else:
                self.company_combo.setCurrentText(current_company)
    
    def _on_company_changed(self, company_name: str) -> None:
        """Handle company name change and load corresponding mapping preset."""
        if not company_name:
            return
        
        # Save current company
        self.config.set_current_company(company_name)
        self.config.save()
        
        # Load mapping preset for this company
        if self.config.has_company_mapping(company_name):
            mappings = self.config.get_cell_mappings(company_name)
            self.log_message(f"업체 '{company_name}'의 매핑 프리셋을 로드했습니다.")
        else:
            # Use default mappings
            self.log_message(f"업체 '{company_name}'의 매핑 정보가 없습니다. 기본 매핑을 사용합니다.")
    
    def _auto_set_year_month(self, file_path: str) -> None:
        """Automatically extract month and suggest year from filename (FR-005, FR-006)."""
        filename = Path(file_path).name
        month = FilenameParser.extract_month(filename)
        company_name = FilenameParser.extract_company_name(filename)
        
        # Set company name if extracted
        if company_name:
            # Check if this is a new company
            if not self.config.has_company_mapping(company_name):
                reply = QMessageBox.question(
                    self,
                    "새 업체 감지",
                    f"'{company_name}' 업체의 매핑 정보가 없습니다.\n새로 추가하시겠습니까?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    # Add to combo box if not exists
                    if self.company_combo.findText(company_name) < 0:
                        self.company_combo.addItem(company_name)
                    self.company_combo.setCurrentText(company_name)
                    # Open mapping dialog
                    self.edit_mapping()
            else:
                # Set company combo box
                index = self.company_combo.findText(company_name)
                if index >= 0:
                    self.company_combo.setCurrentIndex(index)
                else:
                    self.company_combo.setCurrentText(company_name)
        
        if month:
            # Set month combo box
            for i in range(self.month_combo.count()):
                if self.month_combo.itemData(i) == month:
                    self.month_combo.setCurrentIndex(i)
                    break
            
            # Suggest year
            suggested_year = FilenameParser.suggest_year(month)
            
            # Set year combo box
            for i in range(self.year_combo.count()):
                if self.year_combo.itemData(i) == suggested_year:
                    self.year_combo.setCurrentIndex(i)
                    break
            
            self.log_message(f"파일명에서 월 추출: {month}월, 년도 추천: {suggested_year}년")
        else:
            self.log_message("경고: 파일명에서 월을 추출할 수 없습니다. 수동으로 설정해주세요.")
    
    def edit_mapping(self) -> None:
        """Open mapping editor dialog."""
        company_name = self.company_combo.currentText().strip()
        
        # Get current mappings for this company or default
        if company_name and self.config.has_company_mapping(company_name):
            current_mappings = self.config.get_cell_mappings(company_name)
        else:
            current_mappings = self.config.get_cell_mappings()
        
        # Open dialog
        dialog = MappingDialog(self, current_mappings)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_mappings = dialog.get_mappings()
            if new_mappings:
                # Save mappings for current company
                if company_name:
                    self.config.set_cell_mappings(new_mappings, company_name)
                    # Add to combo box if new
                    if self.company_combo.findText(company_name) < 0:
                        self.company_combo.addItem(company_name)
                    self.company_combo.setCurrentText(company_name)
                else:
                    # Save as default
                    self.config.set_cell_mappings(new_mappings)
                
                self.config.save()
                self.log_message("매핑이 저장되었습니다.")
    
    def start_processing(self) -> None:
        """Handle start work button click (FR-019)."""
        # Validate inputs
        if not self.settlement_path:
            QMessageBox.warning(self, "오류", "정산서 파일을 선택해주세요.")
            return
        
        if not self.statement_template_path:
            QMessageBox.warning(self, "오류", "명세서 템플릿 파일을 선택해주세요.")
            return
        
        # Get year and month
        year = self.year_combo.currentData()
        month = self.month_combo.currentData()
        
        if not year or not month:
            QMessageBox.warning(self, "오류", "년도와 월을 선택해주세요.")
            return
        
        # Disable button during processing
        self.start_button.setEnabled(False)
        self.log_message("=" * 50)
        self.log_message("작업 시작...")
        
        try:
            # Get current company name for mapping
            company_name = self.company_combo.currentText().strip()
            
            # Create processor with company-specific config
            processor = FileProcessor(self.config)
            processor.set_progress_callback(self.log_message)
            
            # Get current company name for mapping
            company_name = self.company_combo.currentText().strip()
            
            # Process files
            output_path = processor.process_files(
                self.settlement_path,
                self.statement_template_path,
                year,
                month,
                company_name=company_name if company_name else None
            )
            
            QMessageBox.information(
                self,
                "완료",
                f"작업이 완료되었습니다!\n\n저장된 파일:\n{output_path}"
            )
            
        except FileNotFoundError as e:
            QMessageBox.critical(self, "오류", f"파일을 찾을 수 없습니다:\n{str(e)}")
            self.log_message(f"오류: {str(e)}")
        except KeyError as e:
            QMessageBox.critical(self, "오류", f"필요한 시트를 찾을 수 없습니다:\n{str(e)}")
            self.log_message(f"오류: {str(e)}")
        except ValueError as e:
            QMessageBox.critical(self, "오류", f"데이터 처리 오류:\n{str(e)}")
            self.log_message(f"오류: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"예상치 못한 오류가 발생했습니다:\n{str(e)}")
            self.log_message(f"오류: {str(e)}")
        finally:
            self.start_button.setEnabled(True)
    
    def log_message(self, message: str) -> None:
        """Add a message to the progress log (FR-018).
        
        Args:
            message: Message to add to the log
        """
        self.log_text.append(message)

