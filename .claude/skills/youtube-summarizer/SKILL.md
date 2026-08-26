---
name: youtube-summarizer
description: YouTube 영상 정보 추출 및 핵심 내용 정리. "유튜브", "YouTube", "영상 정리", "영상 요약", "유튜브 정리", "영상 분석" 등을 언급하거나 YouTube URL을 제공하면 자동 실행. 메타데이터 + 자막 추출 → AI 요약 → 노션 DB 저장까지 전체 워크플로우 수행.
allowed-tools: Bash, Read, Write, WebFetch
---

# YouTube 영상 요약 스킬

YouTube URL을 받아 영상 정보를 추출하고, 핵심 내용을 정리하여 노션 DB에 저장하는 End-to-End 자동화 스킬.

**전용 스크립트**: `scripts/youtube_extract.py`

## 전체 워크플로우

```
[1] YouTube URL 입력 확인
       ↓
[2] youtube_extract.py로 메타데이터 + 자막 추출
       ↓
[3] AI 핵심 내용 분석/요약
       ↓
[4] 노션 DB에 페이지 생성 + 본문 블록 추가
```

---

## Step 1: URL 확인

YouTube URL 패턴 인식:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`

URL이 없으면 사용자에게 요청.

---

## Step 2: 영상 정보 추출

### 스크립트 실행

```bash
NOTION_TOKEN=$(grep NOTION_TOKEN .env | cut -d= -f2) \
python3 .claude/skills/youtube-summarizer/scripts/youtube_extract.py "YOUTUBE_URL" \
  -o "$TEMP/youtube_extract_result.json"
```

> 워크스페이스 루트에서 실행. Windows에서는 `$TEMP` 환경변수 사용.

### 추출 데이터
- **메타데이터**: 제목, 채널명, 업로드일, 조회수, 좋아요, 영상 길이, 설명, 태그, 썸네일
- **자막**: 한국어 우선 → 영어 → 기타 언어 순으로 자동 탐색

---

## Step 3: AI 핵심 내용 분석

추출된 자막 텍스트를 기반으로 다음을 분석:

### 3.1 요약
- 영상의 핵심 메시지 3줄 요약
- 주요 주제/키워드

### 3.2 핵심 내용 정리
- 타임라인별 주요 포인트 (자막 timestamp 활용)
- 핵심 인사이트 목록
- 인용할 만한 문장

### 3.3 업무 활용 포인트 ({브랜드명} 관점)
- 마케팅/브랜딩 관련 인사이트
- 경쟁사/시장 동향 관련 정보
- 액션 아이템 도출

### 자막이 없는 경우
- 영상 설명(description)과 태그 기반으로 요약
- WebFetch로 영상 페이지에서 추가 정보 수집
- "자막 없음" 명시

---

## Step 4: 노션 DB 저장

### 대상 DB
- **DB ID**: `305a2681d76d8117b15c000c9056ae0c`
- 사용자가 다른 DB를 지정하면 해당 DB 사용

### 4.1 DB 속성 확인
먼저 DB 속성을 조회하여 사용 가능한 필드 파악:
```bash
NOTION_TOKEN=$(grep NOTION_TOKEN .env | cut -d= -f2) \
python3 .claude/skills/notion-handler/scripts/notion_api.py get-db \
  --id "305a2681d76d8117b15c000c9056ae0c"
```

### 4.2 페이지 생성
DB 속성에 맞게 페이지를 생성합니다. 일반적인 패턴:

```bash
NOTION_TOKEN=$(grep NOTION_TOKEN .env | cut -d= -f2) \
python3 .claude/skills/notion-handler/scripts/notion_api.py create-page \
  --parent "DB_ID" \
  --properties '{
    "이름": "영상 제목",
    "URL": "https://youtube.com/watch?v=...",
    "채널": "채널명",
    "날짜": "2026-02-12"
  }'
```

> 실제 DB 속성에 맞게 properties를 조정하세요. title 타입 속성이 "이름"이 아닐 수 있습니다.

### 4.3 본문 블록 추가

```bash
NOTION_TOKEN=$(grep NOTION_TOKEN .env | cut -d= -f2) \
python3 .claude/skills/notion-handler/scripts/notion_api.py append-blocks \
  --id "PAGE_ID" \
  --blocks '[
    {"type": "callout", "text": "3줄 요약 내용", "emoji": "🎬"},
    {"type": "heading_2", "text": "영상 정보"},
    {"type": "bulleted_list_item", "text": "채널: 채널명"},
    {"type": "bulleted_list_item", "text": "업로드: 2026-02-12"},
    {"type": "bulleted_list_item", "text": "조회수: 123,456회"},
    {"type": "bulleted_list_item", "text": "길이: 15:30"},
    {"type": "bookmark", "url": "https://youtube.com/watch?v=..."},
    {"type": "divider"},
    {"type": "heading_2", "text": "핵심 내용"},
    {"type": "numbered_list_item", "text": "포인트 1"},
    {"type": "numbered_list_item", "text": "포인트 2"},
    {"type": "numbered_list_item", "text": "포인트 3"},
    {"type": "divider"},
    {"type": "heading_2", "text": "인사이트 & 액션"},
    {"type": "bulleted_list_item", "text": "인사이트 1"},
    {"type": "bulleted_list_item", "text": "인사이트 2"},
    {"type": "divider"},
    {"type": "heading_2", "text": "자막 원문"},
    {"type": "toggle", "text": "전체 자막 보기"}
  ]'
```

> 블록은 최대 100개까지 한 번에 추가 가능. 자막이 길면 분할 추가.

---

## 사용 예시

### 예시 1: URL 직접 제공
```
사용자: "이 영상 정리해줘 https://www.youtube.com/watch?v=ABC123DEF45"

Claude:
1. 메타데이터 + 자막 추출
2. 핵심 내용 요약
3. 노션 DB에 저장
4. 요약 결과 보여주기
```

### 예시 2: 여러 영상
```
사용자: "이 유튜브 영상들 정리해서 노션에 넣어줘"
- URL1
- URL2

Claude:
1. 각 영상별 추출 + 요약
2. 각각 노션 DB에 저장
3. 전체 요약 보여주기
```

### 예시 3: 특정 관점 분석
```
사용자: "이 영상에서 마케팅 인사이트 뽑아줘 https://..."

Claude:
1. 추출 + 요약
2. 마케팅 관점 중심으로 분석
3. {브랜드명} 적용 포인트 도출
4. 노션 저장
```

---

## 의존성

- **필요 패키지**: `pip install yt-dlp youtube-transcript-api requests`
- **노션 API**: `NOTION_TOKEN` 환경변수 (.env 파일)
- **notion-handler 스킬**: 노션 저장에 사용

## 파일 구조

```
youtube-summarizer/
├── SKILL.md                     # 이 파일 (SOP)
└── scripts/
    └── youtube_extract.py       # 영상 정보 추출
```

---

## 트러블슈팅

### 자막이 추출되지 않을 때
- 해당 영상에 자막이 없을 수 있음
- `--no-transcript` 옵션으로 메타데이터만 추출
- 영상 설명(description) 기반으로 요약

### yt-dlp 에러
```bash
# 최신 버전으로 업데이트
python3 -m pip install -U yt-dlp
```

### 노션 저장 실패
- DB가 Integration에 공유되어 있는지 확인
- DB 속성 타입과 값이 일치하는지 확인
- `NOTION_TOKEN` 환경변수 확인

---

## 버전 히스토리

- **v1.0.0 (2026-02-12)**: 초기 작성 - 메타데이터/자막 추출, AI 요약, 노션 저장
