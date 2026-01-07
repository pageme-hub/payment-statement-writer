# Feature Specification: 간이지급명세서 자동입력기

**Feature Branch**: `001-auto-statement-filler`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "간이지급명세서 자동입력기를 만들어라."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 간이지급명세서 자동 생성 (Priority: P1)

사용자가 정산서 파일과 명세서 템플릿 파일을 선택하고, 년도와 월을 설정한 후 작업을 시작하면, 시스템이 정산서에서 데이터를 추출하여 명세서에 자동으로 입력하고 저장된 명세서 파일을 생성합니다.

**Why this priority**: 이 기능이 핵심 가치를 제공합니다. 수동 입력 작업을 자동화하여 시간을 절약하고 오류를 줄입니다.

**Independent Test**: 정산서 파일과 명세서 템플릿 파일을 준비하고, UI에서 파일을 선택하고 년/월을 설정한 후 작업 시작 버튼을 클릭하여 완성된 명세서 파일이 생성되는지 확인합니다.

**Acceptance Scenarios**:

1. **Given** 사용자가 프로그램을 실행하고, **When** 정산서 파일과 명세서 파일을 선택하고 년/월을 설정한 후 작업 시작 버튼을 클릭하면, **Then** 정산서에서 데이터가 추출되어 명세서에 입력되고 저장된 파일이 생성됩니다.

2. **Given** 정산서 파일명이 'ㅇㅇ mm월 w주차 정산표.xlsx' 형식일 때, **When** 파일을 선택하면, **Then** 파일명에서 월을 추출하여 현재 날짜와 비교하여 년도를 자동으로 추측하고 년/월 콤보박스가 자동으로 설정됩니다.

3. **Given** 작업이 진행 중일 때, **When** 사용자가 UI를 확인하면, **Then** 작업 현황이 로그 화면에 표시됩니다.

4. **Given** 작업이 완료되었을 때, **When** 저장된 파일을 확인하면, **Then** 파일명이 '간이지급명세서_ㅇㅇyy년m월분.xlsx' 형식이며 기존 서식이 유지됩니다.

---

### Edge Cases

- 정산서 파일의 '월간정산' 시트에 B1:B100 범위에 값이 1 이상인 숫자가 없는 경우 어떻게 처리할까요?
- 정산서 파일명에서 월을 추출할 수 없는 경우 (예: 파일명 형식이 다름) 어떻게 처리할까요?
- 정산서 파일이나 명세서 파일이 이미 열려있거나 다른 프로그램에서 사용 중인 경우 어떻게 처리할까요?
- 정산서 파일의 '월간정산' 시트가 존재하지 않는 경우 어떻게 처리할까요?
- 명세서 파일의 'Sheet1' 시트가 존재하지 않는 경우 어떻게 처리할까요?
- 저장할 위치에 동일한 이름의 파일이 이미 존재하는 경우 어떻게 처리할까요?
- 정산서 파일에서 추출한 데이터 행 수가 100개를 초과하는 경우 어떻게 처리할까요?
- 정산서 파일의 셀에 잘못된 형식의 데이터가 있는 경우 (예: 텍스트, 날짜 등) 어떻게 처리할까요?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to select a settlement file (정산서 파일) through a file selection dialog
- **FR-002**: System MUST allow users to select a statement template file (명세서 파일) through a file selection dialog
- **FR-003**: System MUST display the selected file paths in labels
- **FR-004**: System MUST provide year and month selection combo boxes
- **FR-005**: System MUST automatically extract month from settlement file name in format 'ㅇㅇ mm월 w주차 정산표.xlsx' and suggest year based on current date
- **FR-006**: System MUST automatically update year and month combo boxes when settlement file is selected
- **FR-007**: System MUST parse settlement file '월간정산' sheet B1:B100 range to extract rows with numeric values >= 1
- **FR-008**: System MUST parse columns C, I, J, K from '월간정산' sheet for extracted rows only
- **FR-009**: System MUST write parsed data to statement file 'Sheet1' sheet columns E, H, J, K starting from row 2
- **FR-010**: System MUST fill additional columns in data rows:
  - Column A: row number - 1
  - Column B: selected year from combo box
  - Column C: selected month from combo box
  - Column D: 940918
  - Column G: 1
  - Column I: 3
- **FR-011**: System MUST preserve existing formatting in statement file when writing data
- **FR-012**: System MUST save statement file with name format '간이지급명세서_ㅇㅇyy년m월분.xlsx' in program directory
- **FR-013**: System MUST extract company name (ㅇㅇ) from settlement file for use in output filename
- **FR-014**: System MUST manage input/output mappings through JSON configuration file (setting.json)
- **FR-015**: System MUST NOT hardcode cell mappings - all mappings MUST be stored in setting.json
- **FR-016**: System MUST save statement file path to setting.json when loaded
- **FR-017**: System MUST automatically load statement file path from setting.json on program startup
- **FR-018**: System MUST display work progress log in UI during processing
- **FR-019**: System MUST provide a "Start Work" button to initiate the processing
- **FR-020**: System MUST display additional explanation label below statement file selection button

### Key Entities *(include if feature involves data)*

- **Settlement File (정산서 파일)**: Excel file containing monthly settlement data with '월간정산' sheet. File name format: 'ㅇㅇ mm월 w주차 정산표.xlsx'. Contains company name, month, week information, and settlement data in columns B, C, I, J, K.

- **Statement Template File (명세서 파일)**: Excel template file with 'Sheet1' sheet where data will be written. Contains pre-formatted cells that must be preserved. Path is stored in setting.json for automatic loading.

- **Configuration File (setting.json)**: JSON file storing cell mappings (input/output ranges), statement file path, and other configuration settings. Must be used instead of hardcoded values.

- **Extracted Row Data**: Data extracted from settlement file for rows where column B value >= 1. Contains values from columns C, I, J, K for each valid row.

- **Output Statement File**: Generated Excel file containing filled statement data. File name format: '간이지급명세서_ㅇㅇyy년m월분.xlsx' where ㅇㅇ is company name, yy is year, m is month.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete the entire statement generation process (file selection, configuration, processing, saving) in under 2 minutes for a typical settlement file with up to 100 rows
- **SC-002**: System successfully processes settlement files with valid data format without manual intervention in 95% of cases
- **SC-003**: Generated statement files maintain all existing formatting and structure from the template
- **SC-004**: System correctly extracts and maps data from settlement file to statement file with 100% accuracy for valid input data
- **SC-005**: Users can successfully generate statements without needing to manually configure cell mappings (all mappings managed through setting.json)

## Technical Constraints *(optional)*

This section documents technical implementation constraints that must be considered during planning and development.

### Development Environment

- **Programming Language**: Python
- **Development OS**: macOS or Windows 11
- **Target Deployment OS**: Windows 11

### Technology Stack

- **Data Processing/Excel File Manipulation**: pandas (as needed), openpyxl
- **GUI Framework**: PySide6

### Implementation Notes

These constraints are derived from project constitution principles (minimalism) and ensure consistency with the specified technology stack. All implementation must adhere to these constraints while meeting the functional requirements outlined above.
