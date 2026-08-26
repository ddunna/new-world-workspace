# Claude Code Skills (커스텀 슬래시 커맨드) 종합 가이드

> 조사일: 2026-02-12
> 출처: Anthropic 공식 문서 + 커뮤니티 리소스

---

## 1. Skills란?

Claude Code의 **Skills**는 재사용 가능한 워크플로우/지식을 마크다운 파일로 정의하여, `/커맨드명`으로 호출하거나 Claude가 자동으로 적용할 수 있게 하는 확장 시스템입니다.

**핵심 변경사항**: 기존의 "커스텀 슬래시 커맨드"(`.claude/commands/`)와 "스킬"(`.claude/skills/`)이 **하나의 시스템으로 통합**되었습니다. 기존 `.claude/commands/` 파일도 계속 동작하며, 동일한 이름이 있으면 skills가 우선합니다.

---

## 2. 파일 구조와 저장 위치

### 저장 위치별 적용 범위

| 위치 | 경로 | 적용 범위 |
|------|------|----------|
| **Enterprise** | 관리자 설정 | 조직 전체 |
| **Personal** | `~/.claude/skills/<스킬명>/SKILL.md` | 모든 프로젝트 |
| **Project** | `.claude/skills/<스킬명>/SKILL.md` | 해당 프로젝트만 |
| **Plugin** | `<plugin>/skills/<스킬명>/SKILL.md` | 플러그인 활성화된 곳 |

### 스킬 디렉토리 구조

```
my-skill/
├── SKILL.md           # 메인 지침 (필수)
├── template.md        # Claude가 채울 템플릿 (선택)
├── examples/
│   └── sample.md      # 예시 출력물 (선택)
├── references/
│   └── api-docs.md    # 참고 문서 (선택)
└── scripts/
    └── validate.sh    # 실행 가능한 스크립트 (선택)
```

---

## 3. SKILL.md 작성법

### 기본 구조

모든 SKILL.md는 **YAML 프론트매터** + **마크다운 본문** 두 부분으로 구성됩니다.

```yaml
---
name: sns-draft
description: {브랜드명} 톤앤매너에 맞는 SNS 콘텐츠 초안을 생성합니다. 인스타그램 포스트, 해시태그 생성, 캠페인 카피 작성 시 사용합니다.
---

# SNS 콘텐츠 초안 생성

## 작업 순서
1. 제품/캠페인 정보 확인
2. {브랜드명} 톤앤매너 적용 (모던, 세련, 실용+감성)
3. 채널별 초안 작성
4. 해시태그 생성

## 톤앤매너 가이드
- "Life is Rooms" 슬로건 반영
- 가족 중심, 라이프스타일 강조
- $ARGUMENTS 에 대한 콘텐츠를 작성하세요
```

### 프론트매터 필드 레퍼런스

| 필드 | 필수 | 설명 |
|------|------|------|
| `name` | 권장 | 슬래시 커맨드 이름. 소문자+숫자+하이픈만. 최대 64자. 생략 시 디렉토리명 사용 |
| `description` | 권장 | 스킬 설명. Claude가 자동 호출 여부를 판단하는 데 사용. 최대 1024자 |
| `argument-hint` | 선택 | 자동완성 시 표시될 인자 힌트. 예: `[issue-number]` |
| `disable-model-invocation` | 선택 | `true` → Claude 자동 호출 차단. 수동 호출만 가능 |
| `user-invocable` | 선택 | `false` → `/` 메뉴에서 숨김. 배경 지식용 |
| `allowed-tools` | 선택 | 스킬 실행 시 허용할 도구 목록. 예: `Read, Grep, Glob` |
| `model` | 선택 | 스킬 실행 시 사용할 모델 |
| `context` | 선택 | `fork` → 별도 서브에이전트에서 실행 |
| `agent` | 선택 | `context: fork` 시 에이전트 유형 (`Explore`, `Plan`, `general-purpose`) |
| `hooks` | 선택 | 스킬 라이프사이클에 연결할 훅 |

### 문자열 치환 변수

| 변수 | 설명 |
|------|------|
| `$ARGUMENTS` | 슬래시 커맨드 뒤에 전달된 모든 인자 |
| `$ARGUMENTS[N]` 또는 `$N` | N번째 인자 (0-based) |
| `${CLAUDE_SESSION_ID}` | 현재 세션 ID |

---

## 4. 호출 제어

| 설정 | 사용자 호출 | Claude 자동 호출 | 비고 |
|------|-----------|-----------------|------|
| 기본값 | O | O | description 항상 로드, 전체 내용은 호출 시 로드 |
| `disable-model-invocation: true` | O | X | 부작용 있는 작업에 적합 (`/deploy`, `/commit`) |
| `user-invocable: false` | X | O | 배경 지식 제공용 (레거시 시스템 정보 등) |

---

## 5. 실전 예시

### 예시 1: 모니터링 리포트

```yaml
---
name: monitoring
description: {브랜드명} 브랜드 모니터링 리포트를 생성합니다. 경쟁사 동향 체크, 키워드 검색, 주간 리포트 작성 시 사용합니다.
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, WebSearch, WebFetch
---

# {브랜드명} 브랜드 모니터링

## 작업 순서
1. "{브랜드명}" 키워드로 최근 1주일 웹 검색
2. 경쟁사(한샘, 리바트, 에몬스, 에이스) 동향 체크
3. 주간 리포트 형식으로 정리

## 출력 위치
20-operations/ 폴더에 YYYY-MM-DD_주간모니터링.md 형식으로 저장
```

사용법: `/monitoring 2026-02-12`

### 예시 2: 동적 컨텍스트 주입 (셸 명령어)

```yaml
---
name: pr-summary
description: PR 변경사항을 요약합니다
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## PR 컨텍스트
- PR diff: !`gh pr diff`
- PR 코멘트: !`gh pr view --comments`
- 변경 파일: !`gh pr diff --name-only`

## 작업
이 PR의 변경사항을 요약해주세요.
```

> `!`명령어`` 구문은 스킬이 로드되기 **전에** 셸에서 실행되어 출력이 삽입됩니다.

### 예시 3: 인자 분리 활용

```yaml
---
name: migrate-component
description: 컴포넌트를 한 프레임워크에서 다른 프레임워크로 마이그레이션합니다
---

$0 컴포넌트를 $1에서 $2로 마이그레이션하세요.
기존 동작과 테스트를 모두 유지하세요.
```

사용법: `/migrate-component SearchBar React Vue`

### 예시 4: 서브에이전트 리서치

```yaml
---
name: deep-research
description: 주제를 심층 조사합니다
context: fork
agent: Explore
---

$ARGUMENTS 에 대해 심층 조사하세요:

1. Glob과 Grep으로 관련 파일 탐색
2. 코드 분석
3. 구체적 파일 참조와 함께 결과 요약
```

> `context: fork`는 별도 격리된 컨텍스트에서 실행 → 메인 대화 컨텍스트를 오염시키지 않음

---

## 6. Best Practices

### 작성 원칙

1. **간결하게 작성**: Claude가 모르는 정보만 포함. "이 문단이 토큰 비용을 정당화하는가?" 자문
2. **SKILL.md 본문은 500줄 이하**: 초과하면 별도 참조 파일로 분리
3. **설명(description)은 3인칭으로**: "SNS 콘텐츠 초안을 생성합니다" (O) / "저는 도와드립니다" (X)
4. **구체적 키워드를 description에 포함**: Claude가 100개+ 스킬 중에서 선택할 때 기준
5. **네이밍은 kebab-case**: `sns-draft`, `brand-monitoring`, `meeting-summary`
6. **참조 파일은 1단계 깊이까지만**: 중첩 참조(파일→파일→파일) 피하기

### 자유도 설정 가이드

| 상황 | 자유도 | 예시 |
|------|--------|------|
| 여러 접근법이 유효 | 높음 (텍스트 지침) | 코드 리뷰, 브레인스토밍 |
| 선호 패턴이 존재 | 중간 (의사코드/매개변수) | 리포트 생성, API 호출 |
| 일관성 중요/실패 위험 | 낮음 (구체적 스크립트) | 배포, DB 마이그레이션 |

### 흔한 안티패턴

- Windows 경로 사용 금지 (`scripts\helper.py` → `scripts/helper.py`)
- 선택지를 너무 많이 나열하지 말 것 (기본 도구 하나를 명확히 제시)
- 시간에 민감한 정보 포함 금지 (날짜 기반 분기 대신 "현재 방식/레거시" 구분)
- 모호한 이름 금지 (`helper`, `utils` 대신 `pdf-processing`, `sns-draft`)

---

## 7. 컨텍스트 버짓과 제한사항

### 컨텍스트 버짓
- 스킬 description은 Claude가 사용 가능한 스킬을 파악하도록 컨텍스트에 로드
- 버짓: **컨텍스트 윈도우의 2%** (동적 조정), 폴백 16,000자
- 스킬이 많으면 일부가 제외될 수 있음 → `/context` 명령으로 확인
- 환경 변수 `SLASH_COMMAND_TOOL_CHAR_BUDGET`으로 한도 재설정 가능

### 주요 제한사항

1. **동명 충돌 우선순위**: enterprise > personal > project. 같은 이름의 skill과 command가 있으면 skill 우선
2. **context: fork 주의**: 명확한 작업 지시가 없는 스킬에 사용하면 서브에이전트가 의미 있는 결과를 반환하지 못함
3. **빌트인 커맨드**: `/help`, `/compact` 같은 빌트인은 Skill 도구로 호출 불가
4. **description 미작성 시**: 마크다운 본문의 첫 문단이 description으로 사용 → 자동 호출 정확도 저하
5. **서브에이전트 실행 시**: 대화 히스토리에 접근 불가. 스킬 내용 자체가 프롬프트

---

## 8. {브랜드명} 프로젝트 적용 제안

현재 워크스페이스의 슬래시 커맨드를 skills 구조로 마이그레이션 시 권장 구조:

```
.claude/skills/
├── sns-draft/
│   ├── SKILL.md          # SNS 콘텐츠 초안 생성
│   └── references/
│       └── tone-guide.md  # {브랜드명} 톤앤매너 상세
├── monitoring/
│   ├── SKILL.md          # 브랜드 모니터링 리포트
│   └── references/
│       └── competitors.md # 경쟁사 목록/키워드
├── image-prompt/
│   └── SKILL.md          # 이미지 소스 생성 프롬프트
├── daily-note/
│   └── SKILL.md          # 데일리 노트 생성
└── thinking-partner/
    └── SKILL.md          # 브레인스토밍 파트너
```

---

## 참고 소스

- [Extend Claude with skills - 공식 문서](https://code.claude.com/docs/en/skills)
- [Skill authoring best practices - Anthropic](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Claude Code Merges Slash Commands Into Skills - Medium](https://medium.com/@joe.njenga/claude-code-merges-slash-commands-into-skills-dont-miss-your-update-8296f3989697)
- [Claude Code Customization Guide - alexop.dev](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/)
- [awesome-claude-code - GitHub](https://github.com/hesreallyhim/awesome-claude-code)
- [Anthropic 공식 Skills 저장소](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)
