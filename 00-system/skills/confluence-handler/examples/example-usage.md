# Confluence 스킬 사용 예시

## 시나리오 1: {브랜드명} 마케팅팀 회의록 업로드

### 상황
- 매주 월요일 오전 10시 주간 회의
- 회의록을 Confluence "MKT" 스페이스에 저장
- {브랜드명} 톤앤매너 적용

### 실행 순서

1. **템플릿으로 회의록 페이지 생성**
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-from-template \
  --space "MKT" \
  --template "meeting-notes" \
  --title "2026-02-12 주간 마케팅 회의" \
  --vars '{"date": "2026-02-12", "attendees": "{이름}, 김팀장, 박대리"}'
```

2. **회의 중 작성한 마크다운 파일 업로드**
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page-from-md \
  --space "MKT" \
  --title "2026-02-12 주간 마케팅 회의" \
  --file "40-personal/41-daily/2026-02-12_meeting.md" \
  --labels "회의록,마케팅,주간미팅"
```

---

## 시나리오 2: Q1 캠페인 프로젝트 문서화

### 상황
- "{브랜드명} 봄맞이 캠페인" 프로젝트 시작
- Confluence에 체계적으로 문서화
- 루트 페이지 + 하위 페이지 구조

### 실행 순서

1. **루트 페이지 생성**
```bash
ROOT_ID=$(python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
  --space "MKT" \
  --title "2026 Q1 봄맞이 캠페인" \
  --body "<h1>프로젝트 개요</h1><p>{브랜드명} 봄맞이 캠페인 프로젝트</p>" \
  --return-id)

echo "루트 페이지 ID: $ROOT_ID"
```

2. **하위 페이지 생성 (일정, 예산, 소재, 채널별 전략)**
```bash
# 일정
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
  --space "MKT" \
  --title "📅 일정" \
  --parent "$ROOT_ID" \
  --body "<h2>주요 일정</h2><p>3월 1일 캠페인 시작</p>"

# 예산
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
  --space "MKT" \
  --title "💰 예산" \
  --parent "$ROOT_ID" \
  --body "<h2>예산 배분</h2><p>총 5천만원</p>"

# 소재
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
  --space "MKT" \
  --title "🎨 크리에이티브 소재" \
  --parent "$ROOT_ID" \
  --body "<h2>소재 컨셉</h2><p>봄 라이프스타일 강조</p>"

# 채널별 전략
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
  --space "MKT" \
  --title "📢 채널별 전략" \
  --parent "$ROOT_ID" \
  --body "<h2>SNS, 검색광고, 배너</h2>"
```

3. **레이블 일괄 추가**
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py add-labels \
  --page-id "$ROOT_ID" \
  --labels "Q1,캠페인,봄맞이,2026"
```

---

## 시나리오 3: 경쟁사 분석 리포트 저장

### 상황
- 한샘, 리바트 등 경쟁사 분석 완료
- 분석 결과를 Confluence에 저장
- 이미지, 표, 링크 포함

### 실행 순서

1. **페이지 생성**
```bash
PAGE_ID=$(python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
  --space "MKT" \
  --title "2026-02 경쟁사 분석 리포트" \
  --body "<h1>경쟁사 동향</h1>" \
  --return-id)
```

2. **첨부파일 업로드 (스크린샷, PDF)**
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py upload-attachment \
  --page-id "$PAGE_ID" \
  --file "50-resources/competitor-analysis/hanssem-screenshot.png"

python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py upload-attachment \
  --page-id "$PAGE_ID" \
  --file "50-resources/competitor-analysis/livart-report.pdf"
```

3. **페이지 본문 업데이트 (이미지 포함)**
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py update-page \
  --page-id "$PAGE_ID" \
  --body '<h1>경쟁사 동향 분석</h1>
<h2>한샘</h2>
<p>주요 특징...</p>
<ac:image><ri:attachment ri:filename="hanssem-screenshot.png" /></ac:image>

<h2>리바트</h2>
<p>주요 특징...</p>

<h2>인사이트</h2>
<ac:structured-macro ac:name="info">
  <ac:rich-text-body>
    <p>{브랜드명}은 라이프스타일 강조로 차별화 가능</p>
  </ac:rich-text-body>
</ac:structured-macro>'
```

---

## 시나리오 4: 대만 지사 HQ 공유 자료

### 상황
- 대만 지사와 협업
- 영문 자료 + 한글 자료 동시 관리
- Confluence로 실시간 공유

### 실행 순서

1. **영문 페이지 생성**
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
  --space "GLOBAL" \
  --title "Taiwan HQ - Q1 Campaign Brief" \
  --body "<h1>Campaign Overview</h1><p>brand Spring Campaign 2026...</p>" \
  --labels "Taiwan,HQ,Q1,Campaign"
```

2. **코멘트로 피드백 추가**
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py add-comment \
  --page-id "TAIWAN_PAGE_ID" \
  --body "<p>대만팀 피드백: 현지 선호 컬러는 파스텔톤입니다.</p>"
```

---

## 시나리오 5: 검색 및 아카이빙

### 상황
- 오래된 페이지 정리
- 특정 키워드로 페이지 찾기
- 완료된 프로젝트 아카이빙

### 실행 순서

1. **작년 캠페인 페이지 찾기**
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py search \
  --query 'space=MKT AND type=page AND label="캠페인" AND lastModified>="2025-01-01" AND lastModified<="2025-12-31"' \
  --limit 50
```

2. **특정 페이지 삭제 (주의!)**
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py delete-page \
  --id "OLD_PAGE_ID"
```

3. **최근 수정된 페이지 확인**
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py search \
  --query 'space=MKT AND type=page ORDER BY lastmodified DESC' \
  --limit 10
```

---

## 시나리오 6: 자동화 스크립트 ({브랜드명}팀 전용)

### PKM → Confluence 자동 동기화

```bash
#!/bin/bash
# sync-to-confluence.sh

# {브랜드명} 지식 베이스 폴더의 마크다운 파일들을 Confluence로 동기화

for file in 30-knowledge/{브랜드명}/*.md; do
  filename=$(basename "$file" .md)

  echo "동기화 중: $filename"

  python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page-from-md \
    --space "TEAM" \
    --title "$filename" \
    --file "$file" \
    --labels "지식베이스,{브랜드명},자동동기화"
done

echo "✅ 동기화 완료"
```

### 주간 회의록 자동 생성

```bash
#!/bin/bash
# create-weekly-meeting.sh

DATE=$(date +%Y-%m-%d)
TITLE="${DATE} 주간 마케팅 회의"

python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-from-template \
  --space "MKT" \
  --template "meeting-notes" \
  --title "$TITLE" \
  --vars "{\"date\": \"$DATE\", \"attendees\": \"{이름}, 마케팅팀\"}"

echo "✅ 회의록 페이지 생성 완료: $TITLE"
```

---

## Claude Code에서 사용하는 방법

### 자동 호출 (description 키워드 기반)
```
Claude에게: "이번 회의록을 Confluence MKT 스페이스에 올려줘"
→ confluence-handler 스킬 자동 실행
```

### 수동 호출
```
/confluence-handler 페이지 생성
→ 대화형으로 스페이스, 제목, 내용 입력
```

---

## 팁

1. **페이지 ID 찾기**: Confluence 페이지 URL의 마지막 숫자가 ID입니다.
   - 예: `https://your-domain.atlassian.net/wiki/spaces/MKT/pages/123456/Page+Title`
   - Page ID = `123456`

2. **스페이스 키 확인**: 스페이스 URL의 `/spaces/` 뒤에 있는 짧은 코드입니다.
   - 예: `https://your-domain.atlassian.net/wiki/spaces/MKT/overview`
   - Space Key = `MKT`

3. **마크다운 변환 제한**: 복잡한 표나 특수 형식은 직접 Storage Format으로 작성하세요.

4. **백업**: 중요한 페이지 삭제 전 반드시 백업하세요.
   ```bash
   python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py get-page \
     --id "PAGE_ID" \
     --expand "body.storage" > backup.json
   ```
