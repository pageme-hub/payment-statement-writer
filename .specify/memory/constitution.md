<!--
Sync Impact Report:
- Version change: N/A → 1.0.0 (initial constitution)
- Modified principles: N/A (new)
- Added sections: Core Principles (4 principles), Governance
- Removed sections: N/A
- Templates requiring updates:
  - ✅ plan-template.md (Constitution Check section will reference new principles)
  - ✅ spec-template.md (no direct changes needed, but principles may influence requirements)
  - ✅ tasks-template.md (no direct changes needed, but principles may influence task structure)
- Follow-up TODOs: RATIFICATION_DATE needs to be set by project maintainer
-->

# payment-statement-writer Constitution

## Core Principles

### I. 최소주의 (Minimalism)

PySide6, pandas, openpyxl만 사용. 불필요한 추상화, 프레임워크, 라이브러리 금지. 표준 라이브러리 우선 사용.

**Rationale**: 프로젝트 복잡도를 최소화하고 의존성을 줄여 유지보수성을 향상시킵니다. 학습 목적에 맞게 핵심 라이브러리만 사용하여 프로젝트 구조를 단순하게 유지합니다.

### II. 학습 가능성 (Learnability)

모든 함수에 docstring 필수 (목적, 파라미터, 반환값, 예시). `/docs` 디렉토리에 개발 문서 작성. 주요 로직에 "왜" 이렇게 했는지 주석 필수.

**Rationale**: 코드베이스가 학습 자료로 활용될 수 있도록 문서화를 철저히 합니다. 새로운 개발자가 빠르게 이해할 수 있도록 의도와 배경을 명확히 설명합니다.

### III. 점진적 개발 (Incremental Commits)

기능 단위로 커밋/푸시 필수. 커밋 메시지는 구현 내용을 명확히 설명. 작은 단계로 나누어 개발 (히스토리 = 학습 자료).

**Rationale**: 개발 과정이 학습 자료가 되도록 각 단계를 명확히 기록합니다. 작은 단위의 커밋으로 문제 발생 시 롤백과 디버깅이 용이합니다.

### IV. 실용성 우선 (Pragmatic)

동작하는 코드 > 완벽한 설계. UI는 기능 중심, 디자인은 2순위. 테스트는 선택적 (핵심 로직만).

**Rationale**: 완벽한 설계보다 실제로 동작하는 코드를 우선시합니다. 학습 목적에 맞게 빠르게 프로토타입을 만들고 개선하는 방식으로 진행합니다.

## Governance

Constitution이 모든 개발 결정의 기준. 학습 목적 최우선, 코드 품질은 2순위. 커밋 누락 시 반드시 보완.

**Amendment Procedure**: Constitution 수정 시 버전을 증가시키고 변경 사항을 명확히 문서화해야 합니다. 주요 원칙 변경은 MAJOR 버전 증가, 새로운 원칙 추가는 MINOR 버전 증가, 명확화나 오타 수정은 PATCH 버전 증가를 의미합니다.

**Compliance Review**: 모든 PR과 커밋은 Constitution 원칙을 준수해야 합니다. 원칙 위반 시 반드시 정당화하거나 수정해야 합니다.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): 프로젝트 유지보수자가 설정 필요 | **Last Amended**: 2025-01-27
