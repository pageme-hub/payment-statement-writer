# 간이지급명세서 자동입력기 개발 문서

## 개요

간이지급명세서 자동입력기는 정산서 Excel 파일에서 데이터를 추출하여 명세서 템플릿에 자동으로 입력하고 저장하는 데스크톱 애플리케이션입니다.

## 기술 스택

- **언어**: Python 3.12+
- **GUI 프레임워크**: PySide6
- **Excel 처리**: openpyxl (주요), pandas (필요시)
- **설정 관리**: JSON (표준 라이브러리)

## 프로젝트 구조

```
src/
├── models/          # 데이터 모델
│   ├── config.py           # 설정 파일 관리
│   ├── settlement_file.py  # 정산서 파일 파싱
│   └── statement_file.py   # 명세서 파일 읽기/쓰기
├── services/       # 비즈니스 로직
│   ├── file_processor.py   # 파일 처리 오케스트레이션
│   └── filename_parser.py # 파일명 파싱
├── ui/             # 사용자 인터페이스
│   └── main_window.py      # 메인 윈도우
└── utils/          # 유틸리티
    └── excel_helper.py     # Excel 파일 조작 헬퍼
```

## 주요 기능

### 1. 파일 선택 및 설정

- 정산서 파일 선택 (FR-001)
- 명세서 템플릿 파일 선택 (FR-002)
- 파일명에서 월 자동 추출 및 년도 추천 (FR-005, FR-006)
- 설정 파일 자동 로드/저장 (FR-016, FR-017)

### 2. 데이터 처리

- 정산서 파일에서 유효한 행 추출 (B열 값 >= 1)
- C, I, J, K 열 데이터 추출
- 명세서 템플릿에 데이터 입력 (E, H, J, K 열)
- 추가 열 자동 채우기 (A, B, C, D, G, I 열)
- 기존 서식 유지 (FR-011)

### 3. 출력 파일 생성

- 파일명 형식: `간이지급명세서_ㅇㅇyy년m월분.xlsx`
- 프로그램 디렉토리에 저장

## 설정 파일 (setting.json)

모든 셀 매핑과 파일 경로는 `setting.json`에 저장됩니다 (FR-014, FR-015).

### 기본 구조

```json
{
  "statement_template_path": "",
  "cell_mappings": {
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
}
```

## 설치 및 실행 방법

### 1. 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python -m venv .venv

# 가상환경 활성화
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

### 2. 의존성 설치

```bash
pip install PySide6 pandas openpyxl
```

또는 pyproject.toml을 사용하는 경우:

```bash
pip install -e .
```

### 3. 프로그램 실행

```bash
python main.py
```

### 4. 가상환경 비활성화 (작업 완료 후)

```bash
deactivate
```

## 개발 원칙 (Constitution)

1. **최소주의**: PySide6, pandas, openpyxl만 사용
2. **학습 가능성**: 모든 함수에 docstring 필수
3. **점진적 개발**: 기능 단위로 커밋
4. **실용성 우선**: 동작하는 코드 우선, 테스트는 선택적

## 오류 처리

- 파일이 존재하지 않음: FileNotFoundError
- 시트가 없음: KeyError
- 파일이 사용 중: PermissionError
- 데이터 형식 오류: ValueError
- 파일명 파싱 실패: 경고 메시지, 수동 입력 요청

## 향후 개선 사항

- 엣지 케이스 처리 강화
- 로깅 시스템 개선
- 성능 최적화
- 사용자 가이드 추가

