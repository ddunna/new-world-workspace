---
name: google-calender-handler
description: >
  Google Calendar 일정 관리. "캘린더", "일정", "구글 캘린더", "Google Calendar",
  "일정 추가", "일정 삭제", "일정 수정", "오늘 일정", "이번 주 일정", "미팅 잡아",
  "회의 일정", "스케줄", "schedule", "calendar" 등을 언급하면 자동 실행.
allowed-tools: Bash, Read, Write, Edit
---

# Google Calendar Handler

Google Calendar API를 통한 일정 CRUD 관리 스킬.

## 전제조건

- `credentials.json` — 워크스페이스 루트에 존재 (Google Cloud Console에서 발급)
- `token.json` — 최초 실행 시 브라우저 OAuth 인증 후 자동 생성
- Python 패키지: `google-api-python-client`, `google-auth-oauthlib`, `tzdata`
- Windows에서 Python 실행: `py` 명령 사용 (`python` 아님)

## 스크립트 위치

```
.claude/skills/google-calender-handler/scripts/gcal_api.py
```

---

## Step 1: 사용자 의도 파악

사용자 요청을 분석하여 아래 명령 중 하나로 매핑:

| 의도 | 명령 | 예시 |
|------|------|------|
| 일정 조회 | `list` | "오늘 일정 알려줘", "이번 주 스케줄" |
| 특정 일정 상세 | `get` | "그 미팅 상세 보여줘" |
| 일정 생성 | `insert` | "내일 3시에 미팅 잡아줘" |
| 빠른 추가 | `quick-add` | "금요일 오후 2시 팀 회의 1시간" |
| 일정 수정 | `update` | "그 미팅 시간 변경해줘" |
| 일정 삭제 | `delete` | "그 일정 취소해줘" |
| 캘린더 목록 | `calendars` | "내 캘린더 목록 보여줘" |

---

## Step 2: 명령 실행

### 일정 조회 (Read)

```bash
py .claude/skills/google-calender-handler/scripts/gcal_api.py list --max 10
py .claude/skills/google-calender-handler/scripts/gcal_api.py list --q "미팅"
```

### 단일 일정 조회 (Read)

```bash
py .claude/skills/google-calender-handler/scripts/gcal_api.py get EVENT_ID
```

### 일정 생성 (Create)

```bash
py .claude/skills/google-calender-handler/scripts/gcal_api.py insert \
  --summary "팀 주간회의" \
  --start "2026-03-01T10:00:00+09:00" \
  --end "2026-03-01T11:00:00+09:00" \
  --location "회의실 A" \
  --desc "주간 업무 리뷰"
```

선택 옵션:
- `--attendees "a@co.kr,b@co.kr"` — 참석자 초대
- `--recurrence "RRULE:FREQ=WEEKLY;BYDAY=FR"` — 반복 설정
- `--tz "Asia/Seoul"` — 시간대 (기본값: Asia/Seoul)

### 빠른 추가 (Create)

```bash
py .claude/skills/google-calender-handler/scripts/gcal_api.py quick-add "내일 오전 10시 팀장 보고 1시간"
```

### 일정 수정 (Update)

```bash
py .claude/skills/google-calender-handler/scripts/gcal_api.py update EVENT_ID \
  --summary "수정된 제목" \
  --start "2026-03-01T14:00:00+09:00" \
  --end "2026-03-01T15:00:00+09:00"
```

변경할 필드만 전달하면 나머지는 유지됨 (PATCH 방식).

### 일정 삭제 (Delete)

```bash
py .claude/skills/google-calender-handler/scripts/gcal_api.py delete EVENT_ID
```

### 캘린더 목록 조회

```bash
py .claude/skills/google-calender-handler/scripts/gcal_api.py calendars
```

---

## Step 3: 결과 정리

API 응답을 사용자 친화적으로 정리하여 보여줌:

- **조회**: 날짜, 시간, 제목, 장소를 테이블 형태로
- **생성/수정**: 생성된 이벤트 ID, 제목, Google Calendar 링크 제공
- **삭제**: 삭제 확인 메시지

---

## 날짜/시간 변환 규칙

사용자가 자연어로 시간을 말하면 RFC3339 형식으로 변환:

| 사용자 입력 | 변환 결과 |
|-------------|-----------|
| "내일 오전 10시" | 내일 날짜 + T10:00:00+09:00 |
| "3월 1일 오후 3시" | 2026-03-01T15:00:00+09:00 |
| "다음 주 월요일 2시" | 해당 날짜 + T14:00:00+09:00 |
| "1시간" (duration) | start + 1시간 = end |

기본 시간대: `Asia/Seoul` (+09:00)
기본 duration: 1시간 (end 미지정 시)

---

## RRULE 반복 패턴 참고

| 패턴 | RRULE |
|------|-------|
| 매주 금요일 | `RRULE:FREQ=WEEKLY;BYDAY=FR` |
| 매일 10회 | `RRULE:FREQ=DAILY;COUNT=10` |
| 격주 화요일 | `RRULE:FREQ=WEEKLY;INTERVAL=2;BYDAY=TU` |
| 매월 15일 | `RRULE:FREQ=MONTHLY;BYMONTHDAY=15` |
| 연말까지 매주 | `RRULE:FREQ=WEEKLY;UNTIL=20261231T000000Z` |

---

## 에러 대응

| 에러 | 원인 | 대응 |
|------|------|------|
| 401 | 토큰 만료 | `token.json` 삭제 후 재실행 (브라우저 재인증) |
| 403 | 권한 부족 | OAuth 스코프 확인 (`calendar` 읽기/쓰기) |
| 404 | 이벤트 없음 | event_id 재확인 |
| 400 | 잘못된 파라미터 | 날짜 형식 RFC3339 확인 |

토큰 재발급:
```bash
del token.json
py .claude/skills/google-calender-handler/scripts/gcal_api.py list
```

---

## 주의사항

- `credentials.json`, `token.json`은 `.gitignore`에 등록됨 — 절대 커밋하지 말 것
- 테스트 앱 상태에서 토큰 유효기간 7일 — 만료 시 자동 갱신 또는 재인증
- 삭제는 되돌릴 수 없음 — 삭제 전 사용자에게 반드시 확인
