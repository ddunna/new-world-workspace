---
name: naver-keyword-trend
description: 네이버 키워드 검색량 수집 스킬. `/motion-update` 커맨드의 1단계로 사용됨.
allowed-tools: Bash, Read, Write, Edit
---

# 네이버 키워드 검색량 수집

네이버 검색광고 키워드도구 API를 통해 {캠페인명} 캠페인 16개 키워드의 월간 검색량을 수집하고,
구글시트 `검색트렌드` 탭 + 대시보드 `data.json`에 자동 반영합니다.

> **참고**: 이 스킬은 `/motion-update` 커맨드에 통합되었습니다.
> 단독 실행보다 `/motion-update`를 사용하면 랜딩페이지 유입 등 전체 대시보드 데이터까지 함께 sync됩니다.

## 전제조건

- `.env` — 네이버 검색광고 API 키 (`NAVER_AD_CUSTOMER_ID`, `NAVER_AD_ACCESS_LICENSE`, `NAVER_AD_SECRET_KEY`)
- `token.json` — 구글 OAuth 토큰 (Sheets 스코프 포함)
- Python 패키지: `google-api-python-client`, `google-auth-oauthlib`, `python-dotenv`
- Windows: `py` 명령 사용

## 실행 방법

```bash
py .claude/skills/naver-keyword-trend/scripts/fetch_keyword_trend.py
```

## 데이터 흐름

1. 네이버 검색광고 API 호출 (14개 키워드, 3회 배치)
2. 구글시트 `검색트렌드` 시트에 오늘 날짜 행 append/update
3. `data.json`의 `searchTrendData`에 오늘 엔트리 추가/갱신

## 16개 타겟 키워드

| 그룹 | 키워드 |
|------|--------|
| 브랜드 | {브랜드명}, {브랜드명}모션, {브랜드명}{모델명}, {모델명}{브랜드명} |
| 바젤 | {브랜드명}모션베드, {브랜드명}바젤모션베드, {브랜드명}바젤, 바젤침대 |
| 업모션 | {브랜드명}업모션, {브랜드명}모션테이블, 업모션테이블, {브랜드명}업모션테이블 |
| 뉴트 | {브랜드명}모션데스크, {브랜드명}뉴트, {브랜드명}뉴트모션데스크, 뉴트모션데스크 |

## 참고

- 키워드도구 API는 **월간 검색량**만 제공 (일별 불가)
- 매일 실행하면 그날의 월간 스냅샷을 기록하는 방식
- 구글시트 스프레드시트 ID: `{SPREADSHEET_ID}`
