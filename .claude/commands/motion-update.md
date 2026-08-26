---
description: {캠페인명} 대시보드 데이터 전체 업데이트 (검색어 수집 + 구글시트 → 대시보드 sync)
---

{캠페인명} 캠페인 대시보드 데이터를 한번에 업데이트합니다.

## 실행 (순서대로)

### 1단계: 네이버 키워드 검색량 수집
```bash
python .claude/skills/naver-keyword-trend/scripts/fetch_keyword_trend.py
```

### 2단계: 구글시트 → 대시보드 전체 sync
```bash
python sync_sheets_to_dashboard.py
```

## 실행 후 결과 요약

사용자에게 아래 내용을 표 형태로 보여주세요:
- 16개 키워드별 검색량 (PC + 모바일 합산)
- 구글시트 업데이트 성공 여부
- data.json 업데이트 성공 여부 (searchTrendData + landingPageTraffic 등)
