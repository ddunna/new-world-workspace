---
name: excel-to-csv
description: Excel(.xlsx) 파일을 CSV로 변환. "엑셀 변환", "xlsx to csv", "엑셀 CSV", "시트 변환", "엑셀 파일 변환", "엑셀을 CSV로", "xlsx 변환" 언급 시 자동 실행.
argument-hint: [xlsx 파일 경로]
allowed-tools: Bash, Read
---

# Excel → CSV 변환

`.xlsx` 파일을 받아 시트 정보를 확인하고 CSV로 변환합니다.

## 작업 순서

### Step 1: 파일 경로 확인

`$ARGUMENTS`에서 `.xlsx` 파일 경로를 추출합니다.
경로가 없으면 사용자에게 파일 경로를 요청합니다.

### Step 2: 시트 목록 조회

변환 전 시트 정보를 먼저 보여줍니다:

```bash
python3 .claude/skills/excel-to-csv/scripts/excel_to_csv.py list-sheets --file "$FILE_PATH"
```

결과를 표 형태로 사용자에게 보여줍니다:
```
📊 시트 목록 (총 N개)
┌─────────────┬──────┬──────┐
│ 시트명       │ 행 수 │ 열 수 │
├─────────────┼──────┼──────┤
│ Sheet1      │  150 │    8 │
│ 데이터       │  300 │   12 │
└─────────────┴──────┴──────┘
```

### Step 3: CSV 변환 실행

모든 시트를 CSV로 변환합니다:

```bash
python3 .claude/skills/excel-to-csv/scripts/excel_to_csv.py convert --file "$FILE_PATH"
```

### Step 4: 결과 요약

변환 완료 후 저장된 파일 목록을 알려줍니다:
```
✅ 변환 완료!
저장 위치: [원본 파일과 같은 폴더]
- 파일명_Sheet1.csv
- 파일명_데이터.csv
```

## 파일 명명 규칙

- **시트 1개**: `원본파일명.csv`
- **시트 2개 이상**: `원본파일명_시트명.csv`

## 인코딩

- **UTF-8 with BOM** (`utf-8-sig`) 사용
- Excel에서 열었을 때 한글이 깨지지 않습니다

## 에러 대응

| 에러 상황 | 대응 |
|----------|------|
| 파일을 찾을 수 없음 | 경로를 다시 확인하고 사용자에게 안내 |
| `openpyxl` 미설치 | `pip install openpyxl` 실행 후 재시도 |
| 파일 권한 오류 | 파일이 다른 프로그램에서 열려있는지 확인 안내 |
| `.xlsx` 아닌 파일 | `.xlsx` 형식만 지원한다고 안내 |
