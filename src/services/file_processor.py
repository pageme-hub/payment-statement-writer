"""File processor service for orchestrating settlement to statement conversion.

This module coordinates the entire process of reading settlement files,
extracting data, and writing to statement templates.
"""

from pathlib import Path
from typing import Optional, Callable, Dict, List
from src.models.settlement_file import SettlementFile
from src.models.statement_file import StatementTemplate
from src.models.config import Configuration
from src.services.filename_parser import FilenameParser
from src.services.driver_list_reader import DriverListReader, DriverInfo


class FileProcessor:
    """Orchestrates the file processing workflow.
    
    This service coordinates:
    1. Parsing settlement files
    2. Extracting valid rows and data
    3. Writing to statement templates
    4. Generating output filenames
    """
    
    def __init__(self, config: Optional[Configuration] = None):
        """Initialize FileProcessor.
        
        Args:
            config: Configuration object (creates new one if None)
        """
        if config is None:
            config = Configuration()
            config.load()
        self.config = config
        self.progress_callback: Optional[Callable[[str], None]] = None
        self.driver_selection_callback: Optional[Callable[[str, List[DriverInfo]], Optional[DriverInfo]]] = None
    
    def set_progress_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback function for progress updates.
        
        Args:
            callback: Function that takes a message string and displays it
        """
        self.progress_callback = callback
    
    def set_driver_selection_callback(self, callback: Callable[[str, List[DriverInfo]], Optional[DriverInfo]]) -> None:
        """Set callback function for driver selection when duplicates are found.
        
        Args:
            callback: Function that takes name and list of drivers, returns selected driver or None
        """
        self.driver_selection_callback = callback
    
    def _log(self, message: str) -> None:
        """Log a progress message.
        
        Args:
            message: Message to log
        """
        if self.progress_callback:
            self.progress_callback(message)
    
    def process_files(
        self,
        settlement_path: str,
        statement_template_path: str,
        year: int,
        month: int,
        output_dir: Optional[str] = None,
        company_name: Optional[str] = None,
        driver_list_path: Optional[str] = None
    ) -> str:
        """Process settlement file and generate statement file.
        
        This is the main processing method that:
        1. Parses settlement file
        2. Extracts data
        3. Writes to statement template
        4. Saves output file
        
        Args:
            settlement_path: Path to settlement Excel file
            statement_template_path: Path to statement template Excel file
            year: Selected year
            month: Selected month
            output_dir: Directory to save output file (uses program directory if None)
            company_name: Company name for mapping lookup (uses parsed or config if None)
            driver_list_path: Path to driver list Excel file (optional)
            
        Returns:
            Path to the generated output file
            
        Raises:
            FileNotFoundError: If input files don't exist
            KeyError: If required sheets don't exist
            ValueError: If data extraction fails
            PermissionError: If files are open or locked
        """
        # Validate files exist
        if not Path(settlement_path).exists():
            raise FileNotFoundError(f"정산서 파일을 찾을 수 없습니다: {settlement_path}")
        
        if not Path(statement_template_path).exists():
            raise FileNotFoundError(f"명세서 템플릿 파일을 찾을 수 없습니다: {statement_template_path}")
        
        self._log("정산서 파일 로드 중...")
        
        # Parse settlement file
        settlement = SettlementFile(settlement_path, self.config)
        
        # Extract company name and month from filename
        filename = Path(settlement_path).name
        parse_result = FilenameParser.parse_filename(filename)
        
        # Priority: provided company_name > parsed from filename > config current_company
        company_name_for_mapping = company_name
        
        if parse_result:
            settlement.company_name, settlement.month, settlement.week = parse_result
            # If company_name not provided, use parsed name
            if not company_name_for_mapping:
                company_name_for_mapping = settlement.company_name
        
        # Use current company from config if still not set
        if not company_name_for_mapping:
            company_name_for_mapping = self.config.get_current_company()
        
        # Set company name in models for mapping lookup (must be set before parse_valid_rows)
        if company_name_for_mapping:
            settlement.company_name = company_name_for_mapping
            self._log(f"업체명 설정: {company_name_for_mapping}")
            
            # Debug: log which mappings will be used
            mappings = self.config.get_cell_mappings(company_name_for_mapping)
            data_cols = mappings.get("settlement_data_columns", [])
            self._log(f"사용할 데이터 열: {data_cols}")
        
        # Create statement template (will use company_name when getting mappings)
        statement = StatementTemplate(statement_template_path, self.config)
        if company_name_for_mapping:
            statement.company_name = company_name_for_mapping
        
        self._log(f"유효한 행 추출 중...")
        valid_rows = settlement.parse_valid_rows()
        
        if not valid_rows:
            raise ValueError("정산서 파일에서 유효한 데이터를 찾을 수 없습니다 (B열에 값 >= 1인 행이 없음)")
        
        self._log(f"{len(valid_rows)}개의 유효한 행 발견")
        
        self._log("데이터 추출 중...")
        # Ensure company_name is set before parsing
        if company_name_for_mapping:
            settlement.company_name = company_name_for_mapping
        row_data = settlement.parse_data_columns()
        
        # Load driver list if provided
        driver_reader: Optional[DriverListReader] = None
        if driver_list_path and Path(driver_list_path).exists():
            self._log("기사명단 파일 로드 중...")
            try:
                driver_reader = DriverListReader(driver_list_path, self.config)
                driver_name_to_list = driver_reader.load_driver_list()
                self._log(f"기사명단에서 {sum(len(drivers) for drivers in driver_name_to_list.values())}명의 라이더를 로드했습니다.")
            except Exception as e:
                self._log(f"경고: 기사명단 파일을 읽는 중 오류가 발생했습니다: {e}")
                driver_reader = None
        elif driver_list_path:
            self._log(f"경고: 기사명단 파일을 찾을 수 없습니다: {driver_list_path}")
        
        # Process driver list data and handle duplicates
        driver_list_data: Optional[Dict[str, str]] = None
        if driver_reader and row_data:
            driver_list_data = {}
            for row in row_data:
                name = row.get("name", "")
                if name:
                    matching_drivers = driver_reader.get_drivers_by_name(name)
                    
                    if len(matching_drivers) == 0:
                        # No match found
                        self._log(f"경고: '{name}'에 해당하는 라이더를 찾을 수 없습니다.")
                        driver_list_data[name] = ""
                    elif len(matching_drivers) == 1:
                        # Single match - use it directly
                        driver = matching_drivers[0]
                        driver_list_data[name] = driver.resident_number or ""
                    else:
                        # Multiple matches - ask user to select
                        self._log(f"'{name}' 이름과 일치하는 라이더가 {len(matching_drivers)}명 있습니다.")
                        if self.driver_selection_callback:
                            selected_driver = self.driver_selection_callback(name, matching_drivers)
                            if selected_driver:
                                driver_list_data[name] = selected_driver.resident_number or ""
                            else:
                                # User cancelled - skip this row or use empty
                                driver_list_data[name] = ""
                                self._log(f"경고: '{name}' 라이더 선택이 취소되었습니다.")
                        else:
                            # No callback - use first match
                            driver = matching_drivers[0]
                            driver_list_data[name] = driver.resident_number or ""
                            self._log(f"경고: '{name}' 라이더 선택 콜백이 없어 첫 번째 매칭을 사용합니다.")
        
        # Debug: log what columns were read
        if row_data:
            first_row = row_data[0]
            self._log(f"추출된 데이터 샘플 (첫 번째 행): {list(first_row.keys())}")
        
        self._log("명세서 파일 작성 중...")
        try:
            # StatementTemplate is already created above
            statement.write_data(row_data, driver_list_data)
            statement.set_data_row_count(len(row_data))
            statement.fill_additional_columns(year, month)
        except KeyError as e:
            raise KeyError(f"명세서 파일에 필요한 시트('Sheet1')를 찾을 수 없습니다: {e}")
        except PermissionError as e:
            raise PermissionError(f"명세서 파일이 다른 프로그램에서 사용 중이거나 쓰기 권한이 없습니다: {e}")
        
        # Generate output filename
        output_path = self._generate_output_path(
            settlement.company_name or "업체",
            year,
            month,
            output_dir
        )
        
        self._log(f"파일 저장 중: {output_path}")
        statement.save_as(output_path)
        
        self._log("작업 완료!")
        return str(output_path)
    
    def _generate_output_path(
        self,
        company_name: str,
        year: int,
        month: int,
        output_dir: Optional[str] = None
    ) -> str:
        """Generate output file path with format '간이지급명세서_ㅇㅇyy년m월분.xlsx'.
        
        Args:
            company_name: Company name extracted from settlement file
            year: Selected year (2-digit format)
            month: Selected month
            output_dir: Output directory (uses program directory if None)
            
        Returns:
            Full path to output file
        """
        if output_dir is None:
            # Use program directory (repository root)
            output_dir = Path(__file__).parent.parent.parent
        
        output_dir = Path(output_dir)
        
        # Format: 간이지급명세서_ㅇㅇyy년m월분.xlsx
        year_short = year % 100  # 2-digit year
        filename = f"간이지급명세서_{company_name}{year_short}년{month}월분.xlsx"
        
        return str(output_dir / filename)

