# Confluence Handler Skill

Confluence 페이지/스페이스 관리 및 콘텐츠 작성 자동화 스킬

## 📋 주요 기능

### 1. 스페이스 관리
- 스페이스 목록 조회
- 스페이스 생성
- 스페이스 정보 확인

### 2. 페이지 관리
- 페이지 생성 (루트/하위)
- 페이지 조회
- 페이지 수정
- 페이지 삭제
- **마크다운 → Confluence 자동 변환**

### 3. 검색
- CQL (Confluence Query Language) 검색
- 키워드, 스페이스, 날짜, 레이블 필터링

### 4. 첨부파일
- 파일 업로드
- 첨부파일 목록 조회
- 첨부파일 다운로드

### 5. 코멘트
- 코멘트 추가
- 코멘트 조회

### 6. 레이블
- 레이블 추가
- 레이블 조회
- 레이블 삭제

### 7. 페이지 트리
- 자식 페이지 조회
- 페이지 계층 구조 확인

### 8. 템플릿
- 회의록 템플릿
- 프로젝트 계획서 템플릿
- 커스텀 템플릿 확장 가능

## 🚀 빠른 시작

### 1. 환경변수 설정
```bash
export CONFLUENCE_URL="https://your-domain.atlassian.net"
export CONFLUENCE_EMAIL="your-email@company.com"
export CONFLUENCE_API_TOKEN="your_api_token_here"
```

### 2. Python 패키지 설치
```bash
pip install requests
```

### 3. 테스트
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py list-spaces
```

## 📖 사용 예시

### 회의록 업로드
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-page-from-md \
  --space "MKT" \
  --title "2026-02-12 주간 회의록" \
  --file "meeting-notes.md" \
  --labels "회의록,마케팅"
```

### 프로젝트 문서 생성
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py create-from-template \
  --space "MKT" \
  --template "project-plan" \
  --title "Q1 캠페인" \
  --vars '{"project_name": "Q1 캠페인", "owner": "{이름}"}'
```

### 경쟁사 분석 검색
```bash
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py search \
  --query 'space=MKT AND label="경쟁사" ORDER BY lastmodified DESC' \
  --limit 10
```

## 📂 파일 구조

```
confluence-handler/
├── SKILL.md                    # 메인 스킬 정의
├── README.md                   # 이 파일
├── scripts/
│   └── confluence_api.py       # Confluence API CLI
├── references/
│   └── setup-guide.md          # 설정 가이드
└── examples/
    └── example-usage.md        # 실전 예시
```

## 🔧 지원 명령어

| 명령어 | 설명 |
|--------|------|
| `list-spaces` | 스페이스 목록 |
| `create-space` | 스페이스 생성 |
| `get-space` | 스페이스 조회 |
| `create-page` | 페이지 생성 |
| `get-page` | 페이지 조회 |
| `update-page` | 페이지 수정 |
| `delete-page` | 페이지 삭제 |
| `create-page-from-md` | 마크다운→페이지 |
| `convert-md-to-storage` | 마크다운 변환 |
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
| `get-page-tree` | 페이지 트리 |
| `create-from-template` | 템플릿 페이지 생성 |

## 🎯 {브랜드명}팀 활용 시나리오

### 마케팅팀
- 주간 회의록 자동 업로드
- 캠페인 기획서 체계화
- 경쟁사 분석 리포트 관리

### 고문정팀
- 소비자 조사 결과 공유
- 리뷰 분석 리포트 저장

### 브경디팀
- 크리에이티브 브리프 관리
- 이미지 소스 가이드 문서화

### HQ 협업
- 대만 지사와 실시간 문서 공유
- 영문/한글 자료 동시 관리

## 🔒 보안

- ⚠️ API 토큰은 환경변수로만 관리
- ⚠️ 절대 Git에 커밋하지 마세요
- ⚠️ 중요 페이지 삭제 전 백업 필수

## 📚 참고 문서

- [SKILL.md](SKILL.md) - 전체 기능 레퍼런스
- [references/setup-guide.md](references/setup-guide.md) - 상세 설정 가이드
- [examples/example-usage.md](examples/example-usage.md) - 실전 예시 모음
- [Confluence REST API 공식 문서](https://developer.atlassian.com/cloud/confluence/rest/v1/intro/)

## 📝 Version History

- **v1.0.0 (2026-02-12)**: 초기 버전
  - Space/Page/Search/Attachment/Comment/Label/Template 지원
  - 마크다운 자동 변환
  - 템플릿 기능 (회의록, 프로젝트 계획서)
  - CQL 검색 지원

## 🤝 문의

- 버그 제보: workspace GitHub Issues
- AX 컨설팅: 이림 (Do Better Things)
