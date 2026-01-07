# Tasks: 간이지급명세서 자동입력기

**Input**: Design documents from `/specs/001-auto-statement-filler/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL per Constitution principle IV. No test tasks included unless explicitly requested.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below use single project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan (src/models/, src/services/, src/ui/, src/utils/, docs/)
- [x] T002 Initialize Python project with dependencies in pyproject.toml (PySide6, pandas, openpyxl)
- [x] T003 [P] Create setting.json configuration file with default structure in repository root (refer to contracts/setting-schema.json)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create Configuration model in src/models/config.py to manage setting.json (load, save, validation)
- [x] T005 [P] Create ExcelHelper utility in src/utils/excel_helper.py for openpyxl wrapper functions (read, write, preserve formatting)
- [x] T006 [P] Create FilenameParser service in src/services/filename_parser.py to extract month and company name from settlement file names
- [x] T007 Setup error handling infrastructure (file access errors, parsing errors, validation errors)
- [x] T008 Create base UI window structure in src/ui/main_window.py (PySide6 QMainWindow skeleton)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 간이지급명세서 자동 생성 (Priority: P1) 🎯 MVP

**Goal**: 사용자가 정산서 파일과 명세서 템플릿 파일을 선택하고, 년도와 월을 설정한 후 작업을 시작하면, 시스템이 정산서에서 데이터를 추출하여 명세서에 자동으로 입력하고 저장된 명세서 파일을 생성합니다.

**Independent Test**: 정산서 파일과 명세서 템플릿 파일을 준비하고, UI에서 파일을 선택하고 년/월을 설정한 후 작업 시작 버튼을 클릭하여 완성된 명세서 파일이 생성되는지 확인합니다.

### Implementation for User Story 1

- [x] T009 [P] [US1] Create SettlementFile model in src/models/settlement_file.py (file_path, company_name, month, week, sheet_name, valid_rows, row_data attributes)
- [x] T010 [P] [US1] Create StatementTemplate model in src/models/statement_file.py (file_path, sheet_name, start_row attributes)
- [x] T011 [US1] Implement SettlementFile.parse_valid_rows() method in src/models/settlement_file.py to extract rows with B column value >= 1 from B1:B100 range (depends on T009)
- [x] T012 [US1] Implement SettlementFile.parse_data_columns() method in src/models/settlement_file.py to extract C, I, J, K columns for valid rows (depends on T011)
- [x] T013 [US1] Implement StatementTemplate.write_data() method in src/models/statement_file.py to write data to E, H, J, K columns starting from row 2 with formatting preservation (depends on T010, T005)
- [x] T014 [US1] Implement StatementTemplate.fill_additional_columns() method in src/models/statement_file.py to fill columns A (row-1), B (year), C (month), D (940918), G (1), I (3) (depends on T013)
- [x] T015 [US1] Implement FileProcessor service in src/services/file_processor.py to orchestrate settlement file parsing and statement file writing (depends on T009, T010, T011, T012, T013, T014)
- [x] T016 [US1] Implement OutputStatementFile filename generation in src/services/file_processor.py with format '간이지급명세서_ㅇㅇyy년m월분.xlsx' (depends on T015)
- [x] T017 [US1] Implement UI file selection buttons and path labels in src/ui/main_window.py for settlement file and statement template file (FR-001, FR-002, FR-003)
- [x] T018 [US1] Implement UI year and month combo boxes in src/ui/main_window.py (FR-004)
- [x] T019 [US1] Implement automatic year/month extraction and combo box update when settlement file is selected in src/ui/main_window.py (FR-005, FR-006, depends on T006, T017, T018)
- [x] T020 [US1] Implement "Start Work" button and work progress log display in src/ui/main_window.py (FR-018, FR-019)
- [x] T021 [US1] Implement additional explanation label below statement file selection button in src/ui/main_window.py (FR-020)
- [x] T022 [US1] Connect UI to FileProcessor service in src/ui/main_window.py to execute file processing when "Start Work" button is clicked (depends on T015, T016, T017, T018, T019, T020)
- [x] T023 [US1] Implement automatic statement template path loading from setting.json on program startup in src/ui/main_window.py (FR-017, depends on T004)
- [x] T024 [US1] Implement statement template path saving to setting.json when file is selected in src/ui/main_window.py (FR-016, depends on T004, T017)
- [x] T025 [US1] Add error handling for file access errors, missing sheets, invalid data format in src/services/file_processor.py (depends on T015)
- [x] T026 [US1] Add error handling for filename parsing failures in src/services/filename_parser.py (depends on T006)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can select files, set year/month, and generate statement files.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T027 [P] Add comprehensive docstrings to all functions per Constitution principle II in all source files
- [x] T028 [P] Create development documentation in docs/ directory per Constitution principle II
- [x] T029 Code cleanup and refactoring (remove unused code, improve naming)
- [x] T030 Add logging for all major operations (file selection, parsing, processing, saving)
- [x] T031 Validate quickstart.md scenarios work correctly
- [x] T032 Handle edge cases: empty valid_rows, file already open, duplicate output filename, data format errors

---

## Phase 5: 매핑 편집 기능 추가

**Purpose**: 업체별 매핑 프리셋 관리 및 편집 기능

- [x] T033 Fix StyleProxy error in excel_helper.py write_value method
- [x] T034 [P] Extend Configuration model to support company-specific mapping presets in src/models/config.py
- [x] T035 [P] Create mapping editor dialog UI in src/ui/mapping_dialog.py
- [x] T036 [US1] Add '매핑 편집' button to main window in src/ui/main_window.py
- [x] T037 [US1] Add company name combo box to main window in src/ui/main_window.py
- [x] T038 [US1] Implement automatic mapping preset loading based on company name in src/ui/main_window.py
- [x] T039 [US1] Implement new company detection and mapping creation dialog in src/ui/main_window.py
- [x] T040 [US1] Connect mapping editor dialog to main window in src/ui/main_window.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3)**: Depends on Foundational phase completion
- **Polish (Phase 4)**: Depends on User Story 1 completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within User Story 1

- Models (SettlementFile, StatementTemplate) before services
- Services (FileProcessor) before UI integration
- Core implementation (parsing, writing) before UI connection
- Error handling after core implementation

### Parallel Opportunities

- **Phase 1**: T003 can run in parallel with T001, T002
- **Phase 2**: T005, T006 can run in parallel (different files)
- **Phase 3**: 
  - T009, T010 can run in parallel (different model files)
  - T017, T018, T020, T021 can run in parallel (different UI components)
  - T027, T028 can run in parallel (different documentation files)

---

## Parallel Example: User Story 1

```bash
# Launch all models for User Story 1 together:
Task: "Create SettlementFile model in src/models/settlement_file.py"
Task: "Create StatementTemplate model in src/models/statement_file.py"

# Launch UI components in parallel:
Task: "Implement UI file selection buttons and path labels in src/ui/main_window.py"
Task: "Implement UI year and month combo boxes in src/ui/main_window.py"
Task: "Implement 'Start Work' button and work progress log display in src/ui/main_window.py"
Task: "Implement additional explanation label below statement file selection button in src/ui/main_window.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: Models (SettlementFile, StatementTemplate)
   - Developer B: Services (FileProcessor, FilenameParser)
   - Developer C: UI components (file selection, combo boxes, buttons)
3. Integration: Connect all components together

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- User Story 1 should be independently completable and testable
- Commit after each task or logical group per Constitution principle III
- Stop at checkpoint to validate story independently
- All functions must have docstrings per Constitution principle II
- Avoid: vague tasks, same file conflicts, hardcoded values (use setting.json)

---

## Task Summary

**Total Tasks**: 32
- Phase 1 (Setup): 3 tasks
- Phase 2 (Foundational): 5 tasks
- Phase 3 (User Story 1): 18 tasks
- Phase 4 (Polish): 6 tasks

**Parallel Opportunities**: 10 tasks can run in parallel

**MVP Scope**: Phases 1, 2, and 3 (User Story 1) - 26 tasks total

**Independent Test Criteria**: 
- User Story 1: 정산서 파일과 명세서 템플릿 파일을 준비하고, UI에서 파일을 선택하고 년/월을 설정한 후 작업 시작 버튼을 클릭하여 완성된 명세서 파일이 생성되는지 확인

