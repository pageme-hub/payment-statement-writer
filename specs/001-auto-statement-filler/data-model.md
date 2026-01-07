# Data Model: 간이지급명세서 자동입력기

**Created**: 2025-01-27  
**Purpose**: 데이터 구조 및 엔티티 정의

## Entities

### SettlementFile (정산서 파일)

정산서 Excel 파일을 나타내는 엔티티입니다.

**Attributes**:
- `file_path` (string): 정산서 파일의 전체 경로
- `company_name` (string): 파일명에서 추출한 업체명 (ㅇㅇ)
- `month` (integer): 파일명에서 추출한 월 (mm)
- `week` (integer): 파일명에서 추출한 주차 (w)
- `sheet_name` (string): '월간정산' (고정값)

**Data Extraction**:
- `valid_rows` (list of integers): B1:B100 범위에서 값이 1 이상인 숫자를 가진 행 번호 목록
- `row_data` (list of dict): 유효한 행의 데이터
  - 각 dict는 `{row: int, col_c: value, col_i: value, col_j: value, col_k: value}` 형식

**Validation Rules**:
- 파일이 존재해야 함
- '월간정산' 시트가 존재해야 함
- 파일명 형식이 'ㅇㅇ mm월 w주차 정산표.xlsx'여야 함 (선택적, 파싱 실패 시 경고)

**State Transitions**:
1. 파일 선택 → 파일 경로 설정
2. 파일명 파싱 → company_name, month, week 추출
3. 데이터 파싱 → valid_rows, row_data 추출

### StatementTemplate (명세서 템플릿 파일)

명세서 Excel 템플릿 파일을 나타내는 엔티티입니다.

**Attributes**:
- `file_path` (string): 명세서 템플릿 파일의 전체 경로
- `sheet_name` (string): 'Sheet1' (고정값)
- `start_row` (integer): 데이터 입력 시작 행 (2, 고정값)

**Data Writing**:
- 입력 열: E, H, J, K (정산서 데이터에서)
- 추가 열:
  - A: 행번호 - 1
  - B: 선택된 년도
  - C: 선택된 월
  - D: 940918 (고정값)
  - G: 1 (고정값)
  - I: 3 (고정값)

**Validation Rules**:
- 파일이 존재해야 함
- 'Sheet1' 시트가 존재해야 함
- 기존 서식이 유지되어야 함 (FR-011)

**State Transitions**:
1. 파일 선택 → 파일 경로 설정
2. 데이터 입력 → 새 파일 생성 (서식 유지)

### Configuration (설정)

setting.json 파일을 나타내는 엔티티입니다.

**Attributes**:
- `statement_template_path` (string): 명세서 템플릿 파일 경로 (FR-016, FR-017)
- `cell_mappings` (dict): 셀 매핑 정보
  - `settlement_input_range` (string): "B1:B100"
  - `settlement_data_columns` (list): ["C", "I", "J", "K"]
  - `statement_output_columns` (list): ["E", "H", "J", "K"]
  - `statement_start_row` (integer): 2
  - `statement_fixed_values` (dict): 
    - `column_d`: 940918
    - `column_g`: 1
    - `column_i`: 3

**Validation Rules**:
- JSON 형식이 유효해야 함
- 필수 필드가 존재해야 함

**State Transitions**:
1. 프로그램 시작 → 설정 파일 로드 (FR-017)
2. 명세서 파일 선택 → statement_template_path 저장 (FR-016)
3. 설정 변경 → 설정 파일 저장

### ExtractedRowData (추출된 행 데이터)

정산서에서 추출된 단일 행의 데이터를 나타내는 엔티티입니다.

**Attributes**:
- `row_number` (integer): 원본 정산서 파일의 행 번호
- `column_c` (number): C열 값
- `column_i` (number): I열 값
- `column_j` (number): J열 값
- `column_k` (number): K열 값

**Validation Rules**:
- 모든 값이 숫자여야 함 (선택적, 오류 처리 필요)
- row_number는 1 이상 100 이하

**Usage**:
- 명세서 파일의 특정 행에 매핑되어 기록됨
- 행 번호는 명세서의 A열에 "row_number - 1"로 기록됨

### OutputStatementFile (출력 명세서 파일)

생성된 명세서 파일을 나타내는 엔티티입니다.

**Attributes**:
- `file_path` (string): 저장될 파일의 전체 경로
- `file_name` (string): 파일명 ('간이지급명세서_ㅇㅇyy년m월분.xlsx' 형식)
- `company_name` (string): 업체명 (정산서에서 추출)
- `year` (integer): 선택된 년도
- `month` (integer): 선택된 월
- `data_rows` (integer): 입력된 데이터 행 수

**File Naming**:
- 형식: `간이지급명세서_{company_name}{year}년{month}월분.xlsx`
- 예: `간이지급명세서_ABC24년1월분.xlsx`

**Validation Rules**:
- 파일명 형식이 올바르야 함 (FR-012)
- 기존 서식이 유지되어야 함 (FR-011, SC-003)

## Data Flow

### Processing Flow

1. **SettlementFile** 선택 및 파싱
   - 파일명에서 company_name, month 추출
   - '월간정산' 시트에서 valid_rows 추출
   - valid_rows의 C, I, J, K 열 데이터 추출 → **ExtractedRowData** 리스트 생성

2. **StatementTemplate** 선택
   - 파일 경로를 **Configuration**에 저장

3. **Configuration** 로드
   - setting.json에서 셀 매핑 정보 로드
   - 명세서 템플릿 경로 자동 로드 (프로그램 시작 시)

4. **ExtractedRowData** 리스트를 **StatementTemplate**에 매핑
   - 각 ExtractedRowData를 명세서의 특정 행에 기록
   - 추가 열 (A, B, C, D, G, I) 채우기

5. **OutputStatementFile** 생성
   - 파일명 생성 (company_name, year, month 사용)
   - 프로그램 디렉토리에 저장

## Relationships

- **SettlementFile** → **ExtractedRowData**: 1:N (하나의 정산서에서 여러 행 추출)
- **ExtractedRowData** → **OutputStatementFile**: N:1 (여러 행이 하나의 출력 파일에 기록)
- **Configuration** → **StatementTemplate**: 1:1 (설정에 템플릿 경로 저장)
- **SettlementFile** → **OutputStatementFile**: 1:1 (정산서에서 출력 파일 생성)

## Edge Cases Handling

### 데이터 부족
- valid_rows가 비어있음: 사용자에게 경고, 처리 중단 또는 빈 파일 생성

### 파일명 파싱 실패
- company_name, month 추출 실패: 사용자에게 경고, 수동 입력 요청

### 파일 접근 오류
- 파일이 열려있음: 사용자에게 오류 메시지, 재시도 옵션 제공

### 데이터 형식 오류
- 숫자가 아닌 값: 해당 행 스킵 또는 오류 로그 기록

