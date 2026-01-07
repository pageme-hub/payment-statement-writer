# Contracts: 간이지급명세서 자동입력기

이 디렉토리는 애플리케이션의 계약(contract)을 정의합니다.

## Files

### setting-schema.json

`setting.json` 설정 파일의 JSON Schema입니다.

**용도**:
- 설정 파일의 구조와 유효성 검증
- 개발 시 참고 자료
- 설정 파일 생성/수정 시 가이드

**주요 내용**:
- `statement_template_path`: 명세서 템플릿 파일 경로
- `cell_mappings`: 정산서와 명세서 간 셀 매핑 정보
  - `settlement_input_range`: 정산서 입력 범위
  - `settlement_data_columns`: 정산서에서 추출할 열
  - `statement_output_columns`: 명세서에 입력할 열
  - `statement_start_row`: 명세서 시작 행
  - `statement_fixed_values`: 고정값 설정

**사용 방법**:
- Python의 `jsonschema` 라이브러리로 검증 가능 (선택적, Constitution 원칙 I에 따라 필요시만)
- 수동으로 설정 파일 작성 시 참고

## Note

GUI 애플리케이션이므로 REST API나 GraphQL 스키마는 필요하지 않습니다. 대신 설정 파일 스키마를 정의하여 데이터 구조의 일관성을 보장합니다.

