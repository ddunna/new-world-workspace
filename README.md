# Claude Code Workspace Template

Claude Code로 마케팅/기획 업무를 하기 좋게 정리한 개인 워크스페이스 템플릿입니다. 폴더 구조(Johnny Decimal 방식)와 함께 바로 쓸 수 있는 슬래시 커맨드, 스킬, 서브에이전트가 포함되어 있습니다.

## 시작하기

1. 이 저장소를 clone 하세요.
2. `/setup-workspace` 커맨드를 실행하거나 `CLAUDE.md`를 직접 열어 사용자 프로필을 자신의 정보로 채우세요.
3. 브랜드/회사 관련 커맨드와 스킬에는 `{브랜드명}`, `{경쟁사1}`, `{이름}` 같은 플레이스홀더가 들어있습니다. 실제 값으로 바꿔서 사용하세요.
   - `.claude/commands/monitoring.md`, `sns-draft.md`
   - `.claude/skills/press-release/`, `confluence-handler/`, `naver-keyword-trend/`
4. API 키가 필요한 스킬(`confluence-handler`, `google-calender-handler`, `notion-handler`, `naver-keyword-trend` 등)은 각 스킬의 `SKILL.md` Prerequisites 섹션을 참고해 본인의 `.env`/`credentials.json`/`token.json`을 준비하세요. 이 파일들은 `.gitignore`에 포함되어 있어 커밋되지 않습니다.

## 폴더 구조

```
workspace/
├── 00-inbox/          # 임시 저장, 미분류
├── 00-system/         # 템플릿, 가이드, .claude 미러
├── 10-projects/       # 진행 중인 프로젝트
├── 20-operations/     # 운영 업무
├── 30-knowledge/      # 축적된 지식, Claude Code 활용 가이드
├── 40-personal/       # 개인 기록 (daily, weekly, ideas)
├── 50-resources/      # 참고 자료, 샘플 데이터
└── 90-archive/        # 완료/보관 자료
```

## 포함된 슬래시 커맨드

| 커맨드 | 설명 |
|---|---|
| `/setup-workspace` | 초기 설정 마법사, CLAUDE.md 자동 생성 |
| `/daily-note`, `/daily-review` | 데일리 노트/리뷰 |
| `/thinking-partner`, `/gather`, `/reframe`, `/truth` | 생각 정리/정보 수집 모드 |
| `/todo`, `/todos` | 할 일 관리 |
| `/monitoring` | 브랜드/경쟁사 모니터링 리포트 (플레이스홀더 채워서 사용) |
| `/sns-draft` | SNS 콘텐츠 초안 생성 (플레이스홀더 채워서 사용) |
| `/motion-update` | 캠페인 대시보드 데이터 업데이트 예시 |

## 포함된 스킬

`excel-to-csv`, `google-calender-handler`, `notion-handler`, `transcript-organizer`, `youtube-summarizer`는 바로 쓸 수 있는 범용 스킬입니다. `confluence-handler`, `press-release`, `naver-keyword-trend`, `dashboard-prd`는 예시 값이 플레이스홀더로 되어 있어 자신의 브랜드/조직 정보로 채워야 합니다.

## 포함되지 않은 것

개인 프로젝트 데이터, 실제 회사 정보, 특정 캠페인 데이터 등은 이 템플릿에서 제외했습니다. 각자의 워크스페이스에 맞게 `10-projects/`, `40-personal/`, `50-resources/`를 채워 나가세요.

## 라이선스

[MIT](LICENSE)