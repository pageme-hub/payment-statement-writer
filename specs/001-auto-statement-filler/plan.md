# Implementation Plan: 간이지급명세서 자동입력기

**Branch**: `001-auto-statement-filler` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-auto-statement-filler/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

간이지급명세서 자동입력기는 정산서 Excel 파일에서 데이터를 추출하여 명세서 템플릿에 자동으로 입력하고 저장하는 데스크톱 애플리케이션입니다. PySide6를 사용한 GUI로 파일 선택, 년/월 설정, 작업 실행 기능을 제공하며, pandas와 openpyxl을 활용하여 Excel 파일을 처리합니다. 모든 셀 매핑은 setting.json 파일로 관리하여 하드코딩을 방지합니다.

## Technical Context

**Language/Version**: Python 3.12+ (pyproject.toml에서 requires-python = ">=3.12"로 지정됨)  
**Primary Dependencies**: PySide6 (GUI), pandas (데이터 처리, 필요시), openpyxl (Excel 파일 조작)  
**Storage**: JSON 파일 (setting.json) - 셀 매핑, 명세서 파일 경로 등 설정 저장  
**Testing**: 선택적 (Constitution 원칙 IV에 따라 핵심 로직만)  
**Target Platform**: Windows 11 (배포 대상), macOS 또는 Windows 11 (개발 환경)  
**Project Type**: single (데스크톱 GUI 애플리케이션)  
**Performance Goals**: 
  - 100행 이하 정산서 파일 처리 시 전체 프로세스 2분 이내 완료 (SC-001)
  - Excel 파일 읽기/쓰기 시 기존 서식 100% 유지 (SC-003)
**Constraints**: 
  - Constitution 원칙 I: PySide6, pandas, openpyxl만 사용, 불필요한 추상화 금지
  - Constitution 원칙 II: 모든 함수 docstring 필수, /docs 디렉토리 문서화
  - Constitution 원칙 IV: 동작하는 코드 우선, 테스트는 선택적
  - Windows 11 배포 호환성 필수
**Scale/Scope**: 
  - 단일 사용자 데스크톱 애플리케이션
  - 정산서 파일: 최대 100행 처리 (B1:B100 범위)
  - 명세서 파일: 동일한 행 수만큼 데이터 입력

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase 0 (Pre-Research) Check

**I. Minimalism**: ✅ PASS
- PySide6, pandas, openpyxl만 사용 계획 (Constitution 원칙 I 준수)
- 표준 라이브러리 우선 사용 (json 모듈 등)
- 불필요한 추상화 없음

**II. Learnability**: ✅ PASS
- 모든 함수 docstring 필수 (plan.md에 명시)
- `/docs` 디렉토리 문서화 계획 (Project Structure에 포함)
- 주요 로직 주석 계획 (research.md에 명시)

**III. Incremental Commits**: ✅ PASS
- 기능 단위 커밋 전략 (quickstart.md에 명시)
- 명확한 커밋 메시지 규칙 준수

**IV. Pragmatic**: ✅ PASS
- 동작하는 코드 우선 (Technical Context에 명시)
- 테스트는 선택적 (핵심 로직만)

### Phase 1 (Post-Design) Check

**I. Minimalism**: ✅ PASS
- research.md에서 기술 선택 근거 확인
- PySide6, pandas, openpyxl만 사용 결정
- 추가 의존성 없음

**II. Learnability**: ✅ PASS
- data-model.md에서 엔티티 및 데이터 구조 문서화
- contracts/에서 설정 스키마 정의
- quickstart.md에서 개발자 가이드 제공

**III. Incremental Commits**: ✅ PASS
- quickstart.md에 개발 워크플로우 명시
- 각 단계마다 커밋 계획

**IV. Pragmatic**: ✅ PASS
- 단순한 프로젝트 구조 (single project)
- 불필요한 복잡도 없음

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── settlement_file.py      # 정산서 파일 파싱 및 데이터 추출
│   ├── statement_file.py       # 명세서 파일 읽기/쓰기
│   └── config.py               # setting.json 관리
├── services/
│   ├── file_processor.py       # 파일 처리 로직 (정산서 → 명세서 변환)
│   └── filename_parser.py      # 파일명에서 월/업체명 추출
├── ui/
│   ├── main_window.py          # PySide6 메인 윈도우
│   └── widgets/                # UI 위젯들 (파일 선택, 콤보박스, 로그 등)
└── utils/
    └── excel_helper.py          # Excel 파일 조작 유틸리티 (openpyxl 래퍼)

docs/
└── [개발 문서 - Constitution 원칙 II에 따라 작성]

setting.json                     # 설정 파일 (셀 매핑, 명세서 파일 경로 등)
```

**Structure Decision**: Single project 구조를 선택했습니다. 데스크톱 GUI 애플리케이션이므로 단일 프로젝트로 구성하며, src/ 디렉토리 하위에 models/, services/, ui/, utils/로 모듈을 분리합니다. Constitution 원칙 I (최소주의)에 따라 불필요한 추상화 없이 직접적인 구조를 사용합니다.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations detected. All Constitution principles are satisfied.*
