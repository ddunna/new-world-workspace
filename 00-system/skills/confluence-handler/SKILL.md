---
name: confluence-handler
description: Confluence 페이지/스페이스 관리 및 콘텐츠 작성. "컨플루언스", "Confluence", "위키", "문서 작성", "컨플 페이지", "스페이스", "문서화", "회의록 업로드", "아티클 저장" 등을 언급하면 자동 실행.
allowed-tools: Bash, Read, Write
---

# Confluence Handler Skill

## Prerequisites

### Required: 환경변수 설정

```bash
export CONFLUENCE_URL="https://your-domain.atlassian.net"
export CONFLUENCE_EMAIL="your-email@company.com"
export CONFLUENCE_API_TOKEN="your_api_token_here"
```

**API 토큰 발급**: [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

**설정 가이드**: `00-system/confluence-setup-guide.md` 참조

---

## 주요 기능

### 1. 스페이스 (Space)

#### 스페이스 목록 조회
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py list-spaces
```

#### 스페이스 생성
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-space \
  --key "TEAM" \
  --name "팀 위키" \
  --description "팀 프로젝트 문서 공간"
```

#### 스페이스 정보 조회
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py get-space --key "TEAM"
```

---

### 2. 페이지 (Page)

#### 페이지 생성
```bash
# 루트 페이지 생성
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
  --space "TEAM" \
  --title "프로젝트 계획서" \
  --body "<h1>개요</h1><p>프로젝트 내용...</p>"

# 하위 페이지 생성 (계층 구조)
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
  --space "TEAM" \
  --title "상세 일정" \
  --body "<p>일정 내용...</p>" \
  --parent "123456"
```

**페이지 계층 구조 관리**:
- `--parent` 옵션으로 부모 페이지 ID 지정
- 여러 단계 깊이 구조 가능 (루트 → 섹션 → 상세 페이지)
- 페이지 ID는 생성 시 반환되거나 URL에서 확인

#### 페이지 조회
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py get-page --id "123456"

# 본문 포함 조회
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py get-page \
  --id "123456" \
  --expand "body.storage,version,space"
```

#### 페이지 수정
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py update-page \
  --id "123456" \
  --title "수정된 제목" \
  --body "<h1>수정된 내용</h1><p>새 본문...</p>"
```

**버전 관리**:
- Confluence는 자동으로 페이지 버전 관리
- 수정 시 자동으로 버전 증가
- `get-page`의 `--expand version` 옵션으로 버전 정보 확인

#### 페이지 삭제
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py delete-page --id "123456"
```

#### 대량 페이지 생성
```bash
# 루트 페이지 생성 후 ID 저장
ROOT_ID=$(python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
  --space "MKT" \
  --title "Q1 캠페인" \
  --body "<h1>프로젝트 개요</h1>" \
  --return-id)

# 하위 페이지들 자동 생성
for section in "일정" "예산" "리소스" "실행계획"; do
  python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
    --space "MKT" \
    --title "$section" \
    --parent "$ROOT_ID" \
    --body "<h1>$section</h1><p>내용...</p>"
done
```

---

### 3. 마크다운 변환

#### 마크다운 → Confluence 스토리지 형식
```bash
# 변환만 수행 (출력 확인)
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py convert-md-to-storage \
  --file "document.md"

# 직접 페이지 생성
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page-from-md \
  --space "TEAM" \
  --title "문서 제목" \
  --file "document.md"

# 하위 페이지로 생성 + 레이블 추가
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page-from-md \
  --space "MKT" \
  --title "회의록" \
  --file "40-personal/41-daily/2026-02-26_meeting.md" \
  --parent "123456" \
  --labels "회의록,주간미팅,마케팅"
```

**지원 마크다운 문법**:
| 마크다운 | Confluence |
|---------|-----------|
| `# 제목` | `<h1>제목</h1>` |
| `## 부제목` | `<h2>부제목</h2>` |
| `**굵게**` | `<strong>굵게</strong>` |
| `*기울임*` | `<em>기울임</em>` |
| `` `코드` `` | `<code>코드</code>` |
| `[링크](url)` | `<a href="url">링크</a>` |
| `- 항목` | `<ul><li>항목</li></ul>` |
| `1. 항목` | `<ol><li>항목</li></ol>` |

---

### 4. 검색

#### 기본 검색 (CQL)
```bash
# 키워드 검색
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py search \
  --query "프로젝트"

# 스페이스 내 검색
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py search \
  --query "space=TEAM AND type=page"

# 최근 수정된 페이지
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py search \
  --query "type=page ORDER BY lastmodified DESC" \
  --limit 10
```

#### 고급 CQL 쿼리

**복합 필터링**:
```bash
# 특정 기간 + 스페이스 + 레이블
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py search \
  --query 'space=MKT AND label="캠페인" AND lastModified>="2026-01-01"' \
  --limit 50
```

**제목/본문 검색**:
```bash
# 제목에 특정 단어 포함
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py search \
  --query 'title~"{브랜드명}" AND space=MKT'

# 본문에 특정 단어 포함
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py search \
  --query 'text~"브랜드 캠페인" AND type=page'
```

**마케팅팀 맞춤 쿼리**:
```bash
# Q1 관련 모든 문서
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py search \
  --query 'space=MKT AND (label="Q1" OR title~"Q1" OR text~"1분기")'

# 내가 작성한 최근 문서
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py search \
  --query 'creator=currentUser() AND lastModified>="2026-02-01" ORDER BY lastmodified DESC'

# 특정 캠페인 관련 모든 자료
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py search \
  --query 'space=MKT AND (label="신제품캠페인" OR ancestor=123456)'
```

---

### 5. 첨부파일 (Attachments)

#### 파일 업로드
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py upload-attachment \
  --page-id "123456" \
  --file "report.pdf"
```

#### 대량 첨부파일 업로드
```bash
# 폴더 내 모든 이미지 업로드
for img in images/*.{jpg,png}; do
  python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py upload-attachment \
    --page-id "123456" \
    --file "$img"
done
```

#### 첨부파일 목록 조회
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py list-attachments \
  --page-id "123456"
```

#### 첨부파일 다운로드
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py download-attachment \
  --attachment-id "att123" \
  --output "downloaded_file.pdf"
```

**이미지 본문 삽입**:
```bash
# 1. 이미지 업로드
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py upload-attachment \
  --page-id "123456" \
  --file "banner.jpg"

# 2. 페이지 본문에 이미지 삽입 (Storage Format)
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py update-page \
  --id "123456" \
  --body '<h1>캠페인 소개</h1>
<ac:image>
  <ri:attachment ri:filename="banner.jpg" />
</ac:image>
<p>내용...</p>'
```

---

### 6. 코멘트 (Comments)

#### 코멘트 추가
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py add-comment \
  --page-id "123456" \
  --body "<p>리뷰 의견: 좋습니다!</p>"
```

#### 코멘트 조회
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py get-comments \
  --page-id "123456"
```

---

### 7. 레이블 (Labels)

#### 레이블 추가
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py add-labels \
  --page-id "123456" \
  --labels "프로젝트,마케팅,Q1"
```

#### 레이블 조회
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py get-labels \
  --page-id "123456"
```

#### 레이블 삭제
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py remove-label \
  --page-id "123456" \
  --label "마케팅"
```

#### 자동 레이블 태깅 전략

**날짜 기반**:
```bash
# 현재 연도/분기 자동 태깅
YEAR=$(date +%Y)
QUARTER="Q$(($(date +%-m-1)/3+1))"

python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py add-labels \
  --page-id "123456" \
  --labels "$YEAR,$QUARTER"
```

**카테고리 기반**:
```bash
# 페이지 제목에 따라 자동 분류
TITLE="브랜드 캠페인 기획서"
LABELS="브랜드,캠페인,기획"

python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py add-labels \
  --page-id "123456" \
  --labels "$LABELS"
```

---

### 8. 페이지 트리 (Page Tree)

#### 자식 페이지 조회
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py get-child-pages \
  --page-id "123456"
```

#### 페이지 계층 구조 조회 (재귀적)
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py get-page-tree \
  --page-id "123456" \
  --depth 3
```

**출력 예시**:
```
🌳 페이지 트리 (depth=3):
- Q1 캠페인 (ID: 123456)
  - 일정 (ID: 123457)
    - 1월 일정 (ID: 123460)
    - 2월 일정 (ID: 123461)
  - 예산 (ID: 123458)
  - 리소스 (ID: 123459)
```

---

### 9. 템플릿 활용

#### 미리 정의된 템플릿으로 페이지 생성

**회의록 템플릿**:
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-from-template \
  --space "TEAM" \
  --template "meeting-notes" \
  --title "2026-02-26 주간 회의" \
  --vars '{"date": "2026-02-26", "attendees": "{이름}, 김팀장"}'
```

**프로젝트 계획서 템플릿**:
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-from-template \
  --space "MKT" \
  --template "project-plan" \
  --title "Q1 캠페인 계획서" \
  --vars '{"project_name": "Q1 캠페인", "owner": "{이름}"}'
```

#### 사용 가능한 템플릿
| 템플릿 ID | 설명 | 필수 변수 |
|----------|------|----------|
| `meeting-notes` | 회의록 | `date`, `attendees` |
| `project-plan` | 프로젝트 계획서 | `project_name`, `owner` |

**커스텀 템플릿 추가 방법**:
`confluence_api.py`의 `TEMPLATES` 딕셔너리에 HTML 템플릿 추가

---

## Confluence 스토리지 형식 (Storage Format)

### 기본 태그

| 태그 | 설명 | 예시 |
|------|------|------|
| `<h1>`, `<h2>`, `<h3>` | 제목 | `<h1>제목</h1>` |
| `<p>` | 본문 | `<p>내용</p>` |
| `<strong>`, `<em>` | 강조 | `<strong>중요</strong>` |
| `<ul>`, `<ol>`, `<li>` | 목록 | `<ul><li>항목</li></ul>` |
| `<a href="">` | 링크 | `<a href="url">링크</a>` |
| `<code>` | 인라인 코드 | `<code>code</code>` |

### 매크로 (Structured Macros)

#### 코드 블록
```xml
<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">python</ac:parameter>
  <ac:plain-text-body><![CDATA[
def hello():
    print("Hello, World!")
  ]]></ac:plain-text-body>
</ac:structured-macro>
```

**지원 언어**: `python`, `javascript`, `java`, `bash`, `sql`, `xml`, `json`, `yaml`, etc.

#### 정보 패널
```xml
<ac:structured-macro ac:name="info">
  <ac:rich-text-body>
    <p>중요한 정보입니다.</p>
  </ac:rich-text-body>
</ac:structured-macro>
```

**패널 타입**:
- `info` - 파란색 정보 패널
- `note` - 노란색 노트 패널
- `warning` - 빨간색 경고 패널
- `tip` - 초록색 팁 패널

#### 경고 패널
```xml
<ac:structured-macro ac:name="warning">
  <ac:rich-text-body>
    <p>⚠️ 주의: 이 작업은 되돌릴 수 없습니다.</p>
  </ac:rich-text-body>
</ac:structured-macro>
```

#### 표 (Table)
```xml
<table>
  <tbody>
    <tr>
      <th>제목</th>
      <th>상태</th>
      <th>담당자</th>
    </tr>
    <tr>
      <td>캠페인 기획</td>
      <td>진행중</td>
      <td>{이름}</td>
    </tr>
    <tr>
      <td>소재 제작</td>
      <td>완료</td>
      <td>김디자이너</td>
    </tr>
  </tbody>
</table>
```

#### 이미지 삽입
```xml
<!-- 첨부파일 이미지 -->
<ac:image>
  <ri:attachment ri:filename="banner.jpg" />
</ac:image>

<!-- 외부 URL 이미지 -->
<ac:image>
  <ri:url ri:value="https://example.com/image.jpg" />
</ac:image>
```

#### 사용자 멘션
```xml
<ac:link>
  <ri:user ri:account-id="USER_ACCOUNT_ID" />
</ac:link>
```

#### 페이지 링크
```xml
<ac:link>
  <ri:page ri:content-title="다른 페이지 제목" />
</ac:link>
```

### 복잡한 구조 예시

**캠페인 브리프 페이지**:
```xml
<h1>Q1 브랜드 캠페인 브리프</h1>

<ac:structured-macro ac:name="info">
  <ac:rich-text-body>
    <p><strong>캠페인 기간:</strong> 2026-03-01 ~ 2026-03-31</p>
    <p><strong>담당자:</strong> {이름} (마케팅팀)</p>
  </ac:rich-text-body>
</ac:structured-macro>

<h2>개요</h2>
<p>신제품 런칭을 위한 브랜드 캠페인</p>

<h2>타겟</h2>
<ul>
  <li>연령: 30-40대</li>
  <li>관심사: 인테리어, 라이프스타일</li>
</ul>

<h2>주요 메시지</h2>
<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">text</ac:parameter>
  <ac:plain-text-body><![CDATA[
"삶의 모든 순간을 위한 공간, {브랜드명}"
  ]]></ac:plain-text-body>
</ac:structured-macro>

<h2>예산</h2>
<table>
  <tbody>
    <tr><th>항목</th><th>예산</th></tr>
    <tr><td>미디어 바잉</td><td>5,000만원</td></tr>
    <tr><td>콘텐츠 제작</td><td>2,000만원</td></tr>
  </tbody>
</table>

<ac:structured-macro ac:name="warning">
  <ac:rich-text-body>
    <p>예산 승인 필요 (CFO 결재)</p>
  </ac:rich-text-body>
</ac:structured-macro>

<h2>참고 자료</h2>
<ac:image>
  <ri:attachment ri:filename="campaign_mockup.jpg" />
</ac:image>
```

---

## CQL (Confluence Query Language) 참조

### 기본 쿼리

| 쿼리 | 설명 |
|------|------|
| `type=page` | 페이지만 검색 |
| `type=blogpost` | 블로그 포스트만 검색 |
| `space=TEAM` | 특정 스페이스 내 검색 |
| `title~"프로젝트"` | 제목에 "프로젝트" 포함 |
| `text~"마케팅"` | 본문에 "마케팅" 포함 |
| `label="Q1"` | 레이블이 "Q1"인 페이지 |
| `creator=currentUser()` | 내가 만든 페이지 |
| `lastModified>="2026-01-01"` | 최근 수정일 필터 |

### 고급 쿼리

#### 복합 조건 (AND, OR, NOT)
```sql
-- AND: 모든 조건 만족
space=MKT AND type=page AND label="캠페인"

-- OR: 조건 중 하나 만족
title~"Q1" OR title~"1분기" OR label="Q1"

-- NOT: 조건 제외
space=MKT AND NOT label="archive"

-- 복합 조건
(space=MKT OR space=BRAND) AND type=page AND lastModified>="2026-01-01"
```

#### 날짜 필터
```sql
-- 특정 날짜 이후
lastModified>="2026-02-01"

-- 특정 날짜 범위
lastModified>="2026-01-01" AND lastModified<"2026-02-01"

-- 최근 7일
lastModified>=now("-7d")

-- 이번 달
lastModified>=startOfMonth()
```

#### 정렬 (ORDER BY)
```sql
-- 최근 수정순
type=page ORDER BY lastmodified DESC

-- 제목 알파벳순
space=MKT ORDER BY title ASC

-- 생성일순
type=page ORDER BY created DESC
```

#### 계층 구조 검색
```sql
-- 특정 페이지의 하위 페이지
ancestor=123456

-- 특정 페이지와 모든 하위 페이지
id=123456 OR ancestor=123456
```

#### 사용자 기반 검색
```sql
-- 내가 작성한 페이지
creator=currentUser()

-- 특정 사용자가 작성
creator=your-email@company.com

-- 내가 최근 수정한 페이지
contributor=currentUser() ORDER BY lastmodified DESC
```

### 마케팅팀 실전 쿼리

#### Q1 캠페인 관련 모든 문서
```sql
space=MKT AND (
  label="Q1" OR
  label="1분기" OR
  title~"Q1" OR
  text~"1분기 캠페인"
)
ORDER BY lastmodified DESC
```

#### 이번 주 작성/수정된 문서
```sql
space=MKT AND (
  created>=startOfWeek() OR
  lastModified>=startOfWeek()
)
ORDER BY lastmodified DESC
```

#### 특정 프로젝트 전체 문서 트리
```sql
-- 프로젝트 루트 페이지 ID가 123456일 때
(id=123456 OR ancestor=123456) AND type=page
```

#### 리뷰 필요한 문서 (레이블 기반)
```sql
space=MKT AND label="review-needed" AND NOT label="approved"
ORDER BY created ASC
```

#### 아카이브 후보 (오래된 문서)
```sql
space=MKT AND
lastModified<"2025-01-01" AND
NOT label="keep" AND
NOT label="archive"
ORDER BY lastmodified ASC
```

---

## 사용 예시

### 1. 회의록 자동 업로드
```bash
# Daily Note 마크다운 파일을 Confluence 페이지로 변환
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page-from-md \
  --space "TEAM" \
  --title "2026-02-26 주간 회의록" \
  --file "40-personal/41-daily/2026-02-26_meeting.md" \
  --labels "회의록,주간미팅"
```

### 2. 프로젝트 문서화
```bash
# 1. 루트 페이지 생성
ROOT_ID=$(python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
  --space "MKT" \
  --title "Q1 캠페인 프로젝트" \
  --body "<h1>프로젝트 개요</h1>" \
  --return-id)

# 2. 하위 페이지들 생성
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
  --space "MKT" \
  --title "일정" \
  --parent "$ROOT_ID" \
  --body "<p>일정 내용...</p>"

python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
  --space "MKT" \
  --title "예산" \
  --parent "$ROOT_ID" \
  --body "<p>예산 내용...</p>"
```

### 3. 검색 및 아카이빙
```bash
# 오래된 페이지 찾기
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py search \
  --query 'space=TEAM AND type=page AND lastModified<"2025-01-01"' \
  --limit 50

# 특정 페이지 삭제
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py delete-page --id "123456"
```

### 4. 대량 마이그레이션
```bash
# 로컬 마크다운 파일들을 Confluence로 일괄 업로드
for file in 30-knowledge/{브랜드명}/*.md; do
  python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page-from-md \
    --space "TEAM" \
    --title "$(basename "$file" .md)" \
    --file "$file" \
    --labels "지식베이스,{브랜드명}"
done
```

### 5. {브랜드명} 마케팅팀 캠페인 문서 생성

**시나리오**: 신제품 런칭 캠페인 문서 구조 자동 생성

```bash
#!/bin/bash
# create_campaign_docs.sh

SPACE="MKT"
CAMPAIGN="{브랜드명}_신제품_런칭_2026Q1"

# 1. 캠페인 루트 페이지 생성
ROOT_ID=$(python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-from-template \
  --space "$SPACE" \
  --template "project-plan" \
  --title "$CAMPAIGN" \
  --vars '{"project_name": "{브랜드명} 신제품 런칭", "owner": "{이름}"}' \
  --return-id)

# 2. 하위 섹션 생성
sections=("브리프" "타겟분석" "크리에이티브" "미디어플랜" "예산" "일정" "KPI")

for section in "${sections[@]}"; do
  python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
    --space "$SPACE" \
    --title "${CAMPAIGN}_${section}" \
    --parent "$ROOT_ID" \
    --body "<h1>$section</h1><p>작성 중...</p>"
done

# 3. 자동 레이블 태깅
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py add-labels \
  --page-id "$ROOT_ID" \
  --labels "캠페인,신제품,Q1,2026,{브랜드명}"

echo "✅ 캠페인 문서 구조 생성 완료!"
echo "🔗 URL: https://your-domain.atlassian.net/wiki/spaces/$SPACE/pages/$ROOT_ID"
```

### 6. 모니터링 리포트 자동 업로드

**시나리오**: `/monitoring` 스킬 실행 결과를 Confluence에 자동 업로드

```bash
# 1. 모니터링 실행 (가정: 결과가 00-inbox/monitoring_report.md에 저장됨)
# /monitoring 명령 실행

# 2. Confluence 업로드
TODAY=$(date +%Y-%m-%d)
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page-from-md \
  --space "MKT" \
  --title "브랜드 모니터링 리포트 $TODAY" \
  --file "00-inbox/monitoring_report.md" \
  --labels "모니터링,리포트,{브랜드명},$(date +%Y),$(date +%m월)"

# 3. 코멘트 추가
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py add-comment \
  --page-id "PAGE_ID" \
  --body "<p>자동 생성된 리포트입니다. 리뷰 부탁드립니다.</p>"
```

### 7. Daily Review → Confluence 자동화

**시나리오**: 매일 저녁 Daily Review를 Confluence 개인 페이지에 자동 업로드

```bash
#!/bin/bash
# daily_to_confluence.sh

TODAY=$(date +%Y-%m-%d)
DAILY_FILE="40-personal/41-daily/${TODAY}_daily-review.md"

if [ -f "$DAILY_FILE" ]; then
  python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page-from-md \
    --space "~{이름}" \
    --title "Daily Review $TODAY" \
    --file "$DAILY_FILE" \
    --parent "DAILY_ROOT_PAGE_ID" \
    --labels "daily,개인,$(date +%Y-%m)"

  echo "✅ Daily Review 업로드 완료!"
else
  echo "❌ Daily Review 파일이 없습니다: $DAILY_FILE"
fi
```

**Cron 자동화**:
```bash
# 매일 저녁 6시 자동 실행
0 18 * * * cd /path/to/your-workspace && ./daily_to_confluence.sh
```

### 8. 경쟁사 분석 리포트 공유

**시나리오**: 경쟁사 리뷰 분석 결과를 팀 위키에 공유

```bash
# 1. 경쟁사 분석 실행 (가정)
# /competitor-review-analyzer 실행

# 2. Confluence 업로드
REPORT_DATE=$(date +%Y-%m-%d)
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page-from-md \
  --space "MKT" \
  --title "경쟁사 리뷰 분석 $REPORT_DATE" \
  --file "00-inbox/competitor_analysis.md" \
  --parent "COMPETITOR_ANALYSIS_ROOT_ID" \
  --labels "경쟁사,리뷰분석,$(date +%Y-%m)"

# 3. 정보 패널 추가
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py update-page \
  --id "PAGE_ID" \
  --body "$(cat <<EOF
<ac:structured-macro ac:name="info">
  <ac:rich-text-body>
    <p><strong>분석 대상:</strong> 한샘, 리바트, 에몬스</p>
    <p><strong>분석 기간:</strong> 최근 1개월</p>
    <p><strong>AI 분석:</strong> Claude Sonnet 4.5</p>
  </ac:rich-text-body>
</ac:structured-macro>
$(cat 00-inbox/competitor_analysis_html.txt)
EOF
)"
```

### 9. SNS 콘텐츠 아카이빙

**시나리오**: 발행된 SNS 콘텐츠를 Confluence에 기록

```bash
# SNS 콘텐츠 로그
CONTENT_TITLE="인스타그램_신제품_소개_$(date +%Y%m%d)"

python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
  --space "MKT" \
  --title "$CONTENT_TITLE" \
  --parent "SNS_ARCHIVE_PAGE_ID" \
  --body "<h1>신제품 소개 포스트</h1>
<p><strong>플랫폼:</strong> Instagram</p>
<p><strong>발행일:</strong> $(date +%Y-%m-%d)</p>
<h2>본문</h2>
<p>새로운 {브랜드명} 소파 라인업을 소개합니다...</p>
<h2>이미지</h2>
<ac:image><ri:attachment ri:filename=\"instagram_post.jpg\" /></ac:image>
<h2>성과</h2>
<table>
  <tbody>
    <tr><th>지표</th><th>수치</th></tr>
    <tr><td>좋아요</td><td>1,234</td></tr>
    <tr><td>댓글</td><td>56</td></tr>
    <tr><td>도달</td><td>45,678</td></tr>
  </tbody>
</table>"

# 레이블 추가
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py add-labels \
  --page-id "PAGE_ID" \
  --labels "SNS,인스타그램,신제품,$(date +%Y-%m)"
```

### 10. 지식베이스 구축

**시나리오**: 로컬 PKM 지식을 Confluence로 이전

```bash
#!/bin/bash
# migrate_knowledge.sh

KB_ROOT_ID=$(python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
  --space "TEAM" \
  --title "마케팅 지식베이스" \
  --body "<h1>{브랜드명} 마케팅 지식 저장소</h1>" \
  --return-id)

# 카테고리별 하위 페이지 생성
categories=("브랜드전략" "캠페인사례" "미디어가이드" "크리에이티브팁" "데이터분석")

for category in "${categories[@]}"; do
  CAT_ID=$(python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
    --space "TEAM" \
    --title "$category" \
    --parent "$KB_ROOT_ID" \
    --body "<h1>$category</h1>" \
    --return-id)

  # 해당 카테고리의 마크다운 파일들 업로드
  for file in 30-knowledge/{브랜드명}/$category/*.md; do
    [ -f "$file" ] || continue
    python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page-from-md \
      --space "TEAM" \
      --title "$(basename "$file" .md)" \
      --file "$file" \
      --parent "$CAT_ID" \
      --labels "지식베이스,$category"
  done
done

echo "✅ 지식베이스 마이그레이션 완료!"
```

### 11. 팀 온보딩 문서 생성

**시나리오**: 신규 팀원을 위한 온보딩 가이드 자동 생성

```bash
ONBOARDING_ROOT=$(python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
  --space "MKT" \
  --title "마케팅팀 온보딩 가이드" \
  --body "<h1>환영합니다! 🎉</h1>
<ac:structured-macro ac:name=\"info\">
  <ac:rich-text-body>
    <p>이 페이지는 마케팅팀 신규 팀원을 위한 온보딩 가이드입니다.</p>
  </ac:rich-text-body>
</ac:structured-macro>" \
  --return-id)

# 온보딩 섹션들
onboarding_sections=(
  "팀소개:팀 구성원, 역할, 연락처"
  "업무프로세스:캠페인 기획, 실행, 보고 프로세스"
  "툴가이드:사용하는 도구들 (Claude, Notion, Confluence)"
  "리소스:템플릿, 가이드라인, 브랜드 에셋"
  "FAQ:자주 묻는 질문"
)

for section in "${onboarding_sections[@]}"; do
  TITLE="${section%%:*}"
  DESC="${section#*:}"

  python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
    --space "MKT" \
    --title "$TITLE" \
    --parent "$ONBOARDING_ROOT" \
    --body "<h1>$TITLE</h1><p>$DESC</p>"
done
```

### 12. 주간/월간 리포트 자동화

**시나리오**: 주간 마케팅 활동 리포트 템플릿 자동 생성

```bash
#!/bin/bash
# weekly_report.sh

WEEK_NUM=$(date +%V)
YEAR=$(date +%Y)
WEEK_START=$(date -d "last monday" +%Y-%m-%d)
WEEK_END=$(date -d "next sunday" +%Y-%m-%d)

python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
  --space "MKT" \
  --title "주간 마케팅 리포트 ${YEAR}W${WEEK_NUM}" \
  --parent "WEEKLY_REPORTS_ROOT_ID" \
  --body "<h1>주간 마케팅 리포트</h1>
<p><strong>기간:</strong> $WEEK_START ~ $WEEK_END</p>

<h2>🎯 이번 주 목표</h2>
<ul>
  <li>목표 1</li>
  <li>목표 2</li>
</ul>

<h2>✅ 완료 업무</h2>
<table>
  <tbody>
    <tr><th>업무</th><th>담당자</th><th>상태</th></tr>
    <tr><td>캠페인 A 기획</td><td>{이름}</td><td>완료</td></tr>
  </tbody>
</table>

<h2>📊 주요 지표</h2>
<table>
  <tbody>
    <tr><th>채널</th><th>지표</th><th>수치</th></tr>
    <tr><td>Instagram</td><td>도달</td><td>100K</td></tr>
  </tbody>
</table>

<h2>🚧 이슈 및 개선사항</h2>
<ac:structured-macro ac:name=\"warning\">
  <ac:rich-text-body>
    <p>예산 초과 주의</p>
  </ac:rich-text-body>
</ac:structured-macro>

<h2>📅 다음 주 계획</h2>
<ul>
  <li>계획 1</li>
  <li>계획 2</li>
</ul>"

# 자동 레이블
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py add-labels \
  --page-id "PAGE_ID" \
  --labels "주간리포트,${YEAR},W${WEEK_NUM},마케팅"

echo "✅ 주간 리포트 생성 완료!"
```

---

## 실전 워크플로우

### 마케팅팀 Daily 루틴

**오전**: 어제 작업 리뷰
```bash
# 어제 수정된 우리 팀 문서 확인
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py search \
  --query 'space=MKT AND lastModified>=startOfDay("-1d") AND contributor=currentUser()' \
  --limit 10
```

**오후**: 회의록 업로드
```bash
# Daily Note → Confluence
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page-from-md \
  --space "TEAM" \
  --title "$(date +%Y-%m-%d) 마케팅팀 데일리 미팅" \
  --file "40-personal/41-daily/$(date +%Y-%m-%d)_meeting.md" \
  --labels "회의록,daily"
```

**저녁**: Daily Review 공유
```bash
# Daily Review → Confluence 개인 페이지
./scripts/daily_to_confluence.sh
```

### 주간 리뷰 프로세스

**금요일 오후**: 주간 리포트 생성
```bash
./scripts/weekly_report.sh
```

**월요일 오전**: 지난주 리뷰
```bash
# 지난주 생성된 모든 문서 확인
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py search \
  --query 'space=MKT AND created>=startOfWeek("-1w") AND created<startOfWeek()' \
  --limit 50
```

### 캠페인 론칭 체크리스트

1. **프로젝트 구조 생성**
   ```bash
   ./scripts/create_campaign_docs.sh
   ```

2. **브리프 작성** (Confluence 웹에서)

3. **첨부 자료 업로드**
   ```bash
   python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py upload-attachment \
     --page-id "CAMPAIGN_ROOT_ID" \
     --file "creative_brief.pdf"
   ```

4. **팀원 리뷰 요청** (코멘트)
   ```bash
   python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py add-comment \
     --page-id "CAMPAIGN_ROOT_ID" \
     --body "<p>@팀장님 리뷰 부탁드립니다!</p>"
   ```

5. **최종 승인 후 레이블 변경**
   ```bash
   python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py add-labels \
     --page-id "CAMPAIGN_ROOT_ID" \
     --labels "approved,ready-to-launch"
   ```

---

## 에러 핸들링

### 자주 발생하는 오류

#### 1. "Unauthorized" (401)
**원인**:
- API 토큰이 잘못됨
- 환경변수 미설정

**해결**:
```bash
# 환경변수 확인
echo $CONFLUENCE_URL
echo $CONFLUENCE_EMAIL
echo $CONFLUENCE_API_TOKEN

# 토큰 재발급 (필요 시)
# https://id.atlassian.com/manage-profile/security/api-tokens
```

#### 2. "Page not found" (404)
**원인**:
- 페이지 ID가 잘못됨
- 페이지가 삭제됨
- 접근 권한 없음

**해결**:
```bash
# 페이지 검색으로 확인
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py search \
  --query "title~\"페이지제목\""

# 스페이스 내 모든 페이지 조회
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py search \
  --query "space=TEAM AND type=page"
```

#### 3. "Version conflict" (409)
**원인**:
- 다른 사용자가 동시에 수정
- 버전 번호가 맞지 않음

**해결**:
```bash
# 현재 페이지 정보 조회 (최신 버전 확인)
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py get-page \
  --id "123456" \
  --expand "version"

# 다시 수정 시도 (자동으로 최신 버전 가져옴)
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py update-page \
  --id "123456" \
  --body "새 내용"
```

#### 4. "Invalid request" (400)
**원인**:
- 필수 파라미터 누락
- 잘못된 Storage Format
- 스페이스 Key 오타 (대소문자 구분)

**해결**:
```bash
# 스페이스 Key 확인 (대문자로)
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py list-spaces

# Storage Format 검증
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py convert-md-to-storage \
  --file "test.md"
```

#### 5. "Rate limit exceeded" (429)
**원인**:
- API 호출 제한 초과 (Atlassian Cloud 제한)

**해결**:
```bash
# 대량 작업 시 sleep 추가
for file in *.md; do
  python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page-from-md \
    --space "TEAM" \
    --title "$(basename "$file" .md)" \
    --file "$file"
  sleep 2  # 2초 대기
done
```

### 디버깅 팁

#### JSON 출력으로 상세 정보 확인
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py get-page \
  --id "123456" \
  --expand "body.storage,version,space,ancestors" \
  --json
```

#### CQL 쿼리 테스트
```bash
# 간단한 쿼리부터 시작
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py search \
  --query "type=page" \
  --limit 5 \
  --json
```

#### 마크다운 변환 미리보기
```bash
# 변환 결과 확인 후 파일로 저장
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py convert-md-to-storage \
  --file "test.md" > output.html

# 브라우저에서 확인
```

---

## CLI 명령어 요약

| 명령어 | 설명 |
|--------|------|
| `list-spaces` | 스페이스 목록 조회 |
| `create-space` | 스페이스 생성 |
| `get-space` | 스페이스 정보 조회 |
| `create-page` | 페이지 생성 |
| `get-page` | 페이지 조회 |
| `update-page` | 페이지 수정 |
| `delete-page` | 페이지 삭제 |
| `create-page-from-md` | 마크다운 파일로 페이지 생성 |
| `convert-md-to-storage` | 마크다운 → Confluence 형식 변환 |
| `search` | CQL 검색 |
| `upload-attachment` | 파일 업로드 |
| `list-attachments` | 첨부파일 목록 |
| `download-attachment` | 첨부파일 다운로드 |
| `add-comment` | 코멘트 추가 |
| `get-comments` | 코멘트 조회 |
| `add-labels` | 레이블 추가 |
| `get-labels` | 레이블 조회 |
| `remove-label` | 레이블 삭제 |
| `get-child-pages` | 자식 페이지 조회 |
| `get-page-tree` | 페이지 트리 조회 |
| `create-from-template` | 템플릿으로 페이지 생성 |

---

## 보안

- `CONFLUENCE_API_TOKEN`은 환경변수로 관리
- 토큰을 코드나 문서에 하드코딩 금지
- API 토큰은 읽기/쓰기 권한 최소화
- 중요 페이지 삭제 시 백업 필수
- `.env` 파일은 `.gitignore`에 추가

---

## FAQ

### Q: 마크다운 변환이 완벽하지 않아요
**A**:
- 현재 기본 마크다운 문법만 지원 (제목, 강조, 링크, 목록, 코드블록)
- 복잡한 형식은 Confluence에서 직접 편집
- 또는 Storage Format HTML을 직접 작성

### Q: 이미지를 본문에 삽입하려면?
**A**:
1. 먼저 `upload-attachment`로 이미지 업로드
2. `update-page`로 `<ac:image>` 태그 사용하여 삽입
3. 첨부파일명 정확히 입력

### Q: 페이지 권한 설정은?
**A**:
- API로는 권한 설정 제한적
- Confluence 웹에서 페이지 설정 → 권한 관리

### Q: 대량 작업 시 속도가 느려요
**A**:
- API Rate Limit 존재 (Atlassian Cloud)
- `sleep` 명령으로 요청 간격 조정
- 백그라운드 작업 활용

### Q: 페이지를 복제하고 싶어요
**A**:
```bash
# 1. 원본 페이지 조회
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py get-page \
  --id "123456" \
  --expand "body.storage" \
  --json > original.json

# 2. 본문 추출 후 새 페이지 생성
# (수동으로 body 값 복사 또는 jq 사용)
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page \
  --space "TEAM" \
  --title "복사본" \
  --body "$(cat body.html)"
```

### Q: 스페이스 Key를 모르겠어요
**A**:
```bash
# 모든 스페이스 조회
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py list-spaces

# 또는 Confluence URL에서 확인
# https://your-domain.atlassian.net/wiki/spaces/MKT/...
#                                           ^^^
```

### Q: 페이지 히스토리를 볼 수 있나요?
**A**:
- API로 히스토리 조회는 제한적
- Confluence 웹에서 페이지 → "..." → "Page History" 확인

---

## Version History

- **v1.1.0 (2026-02-26)**:
  - 대폭 개선: 노션 스킬 스타일로 재구성
  - 사용 예시 12개 추가 (마케팅팀 특화)
  - CQL 고급 쿼리 섹션 추가
  - Storage Format 상세 설명 추가
  - 실전 워크플로우 섹션 추가
  - 에러 핸들링 가이드 추가
  - FAQ 섹션 추가
- **v1.0.0 (2026-02-12)**: 초기 작성 - Space/Page/Search/Attachment/Comment/Label/Template 지원
