# Quick Start Guide: 간이지급명세서 자동입력기

**Created**: 2025-01-27  
**Purpose**: 개발자 및 사용자를 위한 빠른 시작 가이드

## 개발자용 Quick Start

### 사전 요구사항

- Python 3.12 이상
- macOS 또는 Windows 11 (개발 환경)
- Windows 11 (배포 대상)

### 프로젝트 설정

1. **가상환경 생성 및 활성화**:
   ```bash
   # 가상환경 생성
   python -m venv .venv
   
   # 가상환경 활성화
   # macOS/Linux:
   source .venv/bin/activate
   # Windows:
   .venv\Scripts\activate
   ```

2. **의존성 설치** (가상환경 활성화 후):
   ```bash
   pip install PySide6 pandas openpyxl
   ```

2. **프로젝트 구조 확인**:
   ```
   src/
   ├── models/
   ├── services/
   ├── ui/
   └── utils/
   ```

3. **설정 파일 생성**:
   - 프로젝트 루트에 `setting.json` 파일 생성
   - `contracts/setting-schema.json` 참고하여 기본 구조 작성

### 기본 설정 파일 (setting.json)

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

### 개발 워크플로우

1. **메인 윈도우 실행**:
   ```python
   # src/ui/main_window.py에서 시작
   python -m src.ui.main_window
   ```

2. **기능별 개발 순서** (Constitution 원칙 III: 점진적 개발):
   - 파일 선택 UI 구현
   - 파일명 파싱 로직 구현
   - Excel 파일 읽기 구현
   - 데이터 변환 로직 구현
   - Excel 파일 쓰기 구현
   - 각 단계마다 커밋

3. **문서화** (Constitution 원칙 II: 학습 가능성):
   - 모든 함수에 docstring 작성
   - 주요 로직에 "왜" 주석 추가
   - `/docs` 디렉토리에 개발 문서 작성

## 사용자용 Quick Start

### 프로그램 실행

1. **가상환경 활성화** (필요한 경우):
   ```bash
   # macOS/Linux:
   source .venv/bin/activate
   # Windows:
   .venv\Scripts\activate
   ```

2. **프로그램 시작**:
   - 실행 파일 또는 `python main.py` 실행

2. **명세서 템플릿 파일 설정** (최초 1회):
   - "명세서 파일 선택" 버튼 클릭
   - 명세서 템플릿 파일 선택
   - 프로그램이 자동으로 경로를 저장 (다음 실행 시 자동 로드)

3. **정산서 파일 처리**:
   - "정산서 파일 선택" 버튼 클릭
   - 정산서 파일 선택 (형식: 'ㅇㅇ mm월 w주차 정산표.xlsx')
   - 프로그램이 자동으로 년/월을 추측하여 콤보박스 설정
   - 필요시 년/월 수동 조정
   - "작업 시작" 버튼 클릭
   - 작업 현황 로그 확인
   - 완료 후 저장된 파일 확인

### 입력 파일 형식

**정산서 파일**:
- 파일명: `ㅇㅇ mm월 w주차 정산표.xlsx` (예: `ABC 1월 1주차 정산표.xlsx`)
- 시트명: `월간정산`
- 데이터 위치:
  - B1:B100: 유효한 행 판단 (값 >= 1)
  - C, I, J, K 열: 추출할 데이터

**명세서 템플릿 파일**:
- 시트명: `Sheet1`
- 서식: 기존 서식 유지됨 (변경되지 않음)

### 출력 파일

- 파일명 형식: `간이지급명세서_ㅇㅇyy년m월분.xlsx`
- 예: `간이지급명세서_ABC24년1월분.xlsx`
- 저장 위치: 프로그램이 있는 폴더

## 문제 해결

### 파일명 파싱 실패

**증상**: 파일 선택 후 년/월이 자동으로 설정되지 않음

**해결**:
- 파일명이 'ㅇㅇ mm월 w주차 정산표.xlsx' 형식인지 확인
- 수동으로 년/월 콤보박스 설정

### 시트를 찾을 수 없음

**증상**: "필요한 시트를 찾을 수 없습니다" 오류

**해결**:
- 정산서 파일에 '월간정산' 시트가 있는지 확인
- 명세서 템플릿 파일에 'Sheet1' 시트가 있는지 확인

### 파일이 사용 중입니다

**증상**: "파일이 다른 프로그램에서 사용 중입니다" 오류

**해결**:
- Excel이나 다른 프로그램에서 파일을 닫기
- 파일이 읽기 전용인지 확인

### 서식이 변경됨

**증상**: 출력 파일의 서식이 원본과 다름

**해결**:
- openpyxl의 서식 보존 기능 확인
- 템플릿 파일의 서식이 올바른지 확인

## 다음 단계

- [ ] `/speckit.tasks` 명령으로 작업 목록 생성
- [ ] 각 작업을 순차적으로 구현
- [ ] Constitution 원칙에 따라 점진적으로 커밋
- [ ] 문서화 유지

