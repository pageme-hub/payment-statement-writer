# Research: 간이지급명세서 자동입력기

**Created**: 2025-01-27  
**Purpose**: 기술 선택 근거 및 구현 전략 문서화

## Technology Stack Decisions

### Python 3.12+

**Decision**: Python 3.12+ 사용

**Rationale**: 
- 프로젝트의 pyproject.toml에서 이미 requires-python = ">=3.12"로 지정됨
- Excel 파일 처리와 GUI 개발에 Python이 적합
- 풍부한 라이브러리 생태계 (pandas, openpyxl, PySide6)

**Alternatives considered**: 
- Python 3.11: 프로젝트 요구사항이 3.12+이므로 제외
- 다른 언어 (C#, Java): Constitution 원칙 I (최소주의)에 따라 이미 지정된 Python 사용

### PySide6 (GUI Framework)

**Decision**: PySide6 사용

**Rationale**:
- Constitution 원칙 I에서 명시적으로 PySide6 사용 지정
- 크로스 플랫폼 GUI 프레임워크 (개발: macOS/Windows, 배포: Windows 11)
- Qt 기반으로 안정적이고 성숙한 프레임워크
- 파일 다이얼로그, 콤보박스, 라벨 등 필요한 UI 컴포넌트 제공

**Alternatives considered**:
- Tkinter: 표준 라이브러리이지만 Constitution에서 PySide6 명시
- PyQt6: PySide6와 유사하지만 Constitution에서 PySide6 지정
- 웹 기반 (Electron 등): Constitution 원칙 I 위반 (불필요한 복잡도)

### openpyxl (Excel 파일 조작)

**Decision**: openpyxl 사용 (필수), pandas는 필요시 사용

**Rationale**:
- Constitution 원칙 I에서 명시적으로 openpyxl 사용 지정
- Excel 파일의 서식 유지가 중요 (FR-011, SC-003)
- openpyxl은 셀별 서식 보존에 적합
- pandas는 데이터 처리에 유용하지만, 서식 유지가 어려울 수 있음

**Usage Strategy**:
- openpyxl: Excel 파일 읽기/쓰기, 서식 유지 (주요 사용)
- pandas: 복잡한 데이터 필터링이나 변환이 필요한 경우에만 사용

**Alternatives considered**:
- xlrd/xlwt: 구버전 Excel만 지원, .xlsx 제한적
- xlsxwriter: 쓰기 전용, 읽기 불가
- pandas만 사용: 서식 유지 어려움 (FR-011 위반 가능)

### JSON Configuration (setting.json)

**Decision**: JSON 파일로 설정 관리

**Rationale**:
- FR-014, FR-015에서 하드코딩 금지, setting.json 사용 필수
- Python 표준 라이브러리 json 모듈 사용 가능 (Constitution 원칙 I 준수)
- 사람이 읽고 수정하기 쉬운 형식
- 셀 매핑, 파일 경로 등 설정 관리에 적합

**Alternatives considered**:
- YAML: 추가 의존성 필요 (Constitution 원칙 I 위반)
- INI 파일: 중첩 구조 표현 어려움
- 환경 변수: 복잡한 매핑 정보 저장에 부적합

## Implementation Patterns

### Excel 파일 처리 패턴

**Decision**: openpyxl을 사용하여 서식 보존하며 데이터 읽기/쓰기

**Rationale**:
- FR-011: 기존 서식 변형 금지
- SC-003: 생성된 파일이 템플릿의 서식과 구조 100% 유지
- openpyxl의 `copy_worksheet()` 또는 직접 셀 복사로 서식 유지

**Implementation Approach**:
1. 명세서 템플릿 파일을 읽기 전용으로 열기
2. 새 워크북 생성 또는 템플릿 복사
3. 데이터만 특정 셀에 쓰기 (서식은 유지)
4. 저장

**Alternatives considered**:
- pandas로 읽고 openpyxl로 쓰기: 복잡도 증가, 서식 유지 어려움
- 템플릿을 완전히 복사 후 데이터만 수정: 가장 안전한 방법

### 파일명 파싱 패턴

**Decision**: 정규표현식을 사용하여 파일명에서 월/업체명 추출

**Rationale**:
- FR-005: 파일명 형식 'ㅇㅇ mm월 w주차 정산표.xlsx'에서 월 추출
- FR-013: 업체명(ㅇㅇ) 추출하여 출력 파일명에 사용
- Python 표준 라이브러리 `re` 모듈 사용 (Constitution 원칙 I 준수)

**Implementation Approach**:
- 정규표현식: `r'(.+?)\s+(\d+)월\s+\d+주차\s+정산표\.xlsx'`
- 월 추출 후 현재 날짜와 비교하여 년도 추측
- Edge case: 파일명 형식이 다를 경우 사용자에게 경고 및 수동 입력 요청

### 설정 파일 관리 패턴

**Decision**: setting.json을 읽고 쓰는 유틸리티 함수 제공

**Rationale**:
- FR-014, FR-015, FR-016, FR-017에서 설정 파일 사용 필수
- 중앙 집중식 설정 관리로 하드코딩 방지
- 프로그램 시작 시 자동 로드 (FR-017)

**Implementation Approach**:
- `src/models/config.py`에 Config 클래스 또는 함수 제공
- 설정 스키마 정의 (셀 매핑, 파일 경로 등)
- 기본값 제공 및 검증 로직 포함

## Error Handling Strategy

### Excel 파일 처리 오류

**Decision**: 명확한 오류 메시지와 사용자 피드백 제공

**Rationale**:
- Edge cases에서 다양한 오류 시나리오 식별됨
- 사용자가 문제를 이해하고 해결할 수 있도록 명확한 메시지 필요

**Handling Approach**:
- 파일이 열려있거나 사용 중: "파일이 다른 프로그램에서 사용 중입니다" 메시지
- 시트가 없음: "필요한 시트('월간정산' 또는 'Sheet1')를 찾을 수 없습니다" 메시지
- 데이터 형식 오류: "셀 [위치]의 데이터 형식이 올바르지 않습니다" 메시지

### 파일명 파싱 오류

**Decision**: 파싱 실패 시 사용자에게 수동 입력 요청

**Rationale**:
- FR-005에서 자동 추출 실패 시 대안 필요
- 사용자가 수동으로 년/월을 설정할 수 있어야 함

**Handling Approach**:
- 파일명 파싱 시도
- 실패 시 경고 메시지 표시 및 콤보박스는 현재 날짜로 기본값 설정
- 사용자가 수동으로 수정 가능

## Performance Considerations

### Excel 파일 처리 성능

**Decision**: 필요한 범위만 읽고 쓰기 (B1:B100, 특정 열만)

**Rationale**:
- SC-001: 100행 이하 파일 처리 시 2분 이내 완료
- 전체 시트를 읽지 않고 필요한 범위만 처리하여 성능 최적화

**Optimization Approach**:
- B1:B100 범위만 스캔하여 유효한 행 찾기
- 유효한 행의 C, I, J, K 열만 읽기
- 명세서에는 필요한 셀만 쓰기

## Windows 11 배포 고려사항

### 실행 파일 생성

**Decision**: PyInstaller 또는 cx_Freeze 사용 검토 필요 (향후 결정)

**Rationale**:
- 배포 대상: Windows 11
- 사용자가 Python 설치 없이 실행할 수 있어야 함

**Alternatives considered**:
- PyInstaller: 가장 널리 사용, 단일 실행 파일 생성 가능
- cx_Freeze: 대안
- Python 설치 필요: 사용자 편의성 저하

**Note**: 배포는 구현 후 Phase에서 결정 (현재는 구현에 집중)

## 결론

모든 기술 선택은 Constitution 원칙을 준수하며, spec의 요구사항을 만족합니다. 추가 의존성 없이 PySide6, pandas(필요시), openpyxl만 사용하여 최소주의 원칙을 지킵니다.

