# 간이지급명세서 자동입력기

정산서 Excel 파일에서 데이터를 추출하여 명세서 템플릿에 자동으로 입력하고 저장하는 데스크톱 애플리케이션입니다.

## 설치 방법

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

## 실행 방법

```bash
python main.py
```

## 사용 방법

1. **명세서 템플릿 파일 설정** (최초 1회):
   - "명세서 파일 선택" 버튼 클릭
   - 명세서 템플릿 파일 선택
   - 프로그램이 자동으로 경로를 저장 (다음 실행 시 자동 로드)

2. **정산서 파일 처리**:
   - "정산서 파일 선택" 버튼 클릭
   - 정산서 파일 선택 (형식: 'ㅇㅇ mm월 w주차 정산표.xlsx')
   - 프로그램이 자동으로 년/월을 추측하여 콤보박스 설정
   - 필요시 년/월 수동 조정
   - "작업 시작" 버튼 클릭
   - 완료 후 저장된 파일 확인

## 요구사항

- Python 3.12 이상
- macOS 또는 Windows 11 (개발 환경)
- Windows 11 (배포 대상)

## 기술 스택

- PySide6 (GUI)
- pandas (데이터 처리, 필요시)
- openpyxl (Excel 파일 조작)

## 라이선스

이 프로젝트의 라이선스 정보를 여기에 추가하세요.

