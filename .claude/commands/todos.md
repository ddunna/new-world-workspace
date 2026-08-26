---
description: 저장된 모든 Todo를 다양한 방식으로 조회하고 관리
argument-hint: [today|project|overdue|stats]
allowed-tools: Read, Write, Edit, Bash
---

저장된 모든 Todo를 조회하고 관리해주세요.

**사용 예시:**
```
/todos              # 전체 Todo 보기
/todos today        # 오늘 할 일만
/todos project      # 프로젝트별 그룹화
/todos overdue      # 1주일 이상 된 것들
/todos stats        # Todo 통계
```

**파일 경로:**
- 읽기: `./40-personal/46-todos/active-todos.md`
- 아카이브: `./40-personal/46-todos/completed-todos.md`

**수행할 작업:**

## 1. `/todos` (기본 - 전체 보기)

active-todos.md 파일을 읽어서 전체 Todo 표시

## 2. `/todos today` (오늘 할 일)

1. active-todos.md 읽기
2. "Today" 섹션 추출
3. 우선순위별로 정렬 (high -> normal -> low)
4. 깔끔하게 표시

## 3. `/todos project` (프로젝트별)

1. active-todos.md의 모든 Todo 읽기
2. `project:` 필드로 그룹화
3. 프로젝트별로 표시

## 4. `/todos overdue` (오래된 것들)

1. 모든 Todo의 `added:` 필드 체크
2. 현재 시간 - 추가 시간 > 7일인 것 필터링
3. 오래된 순으로 정렬

## 5. `/todos stats` (통계)

1. 전체 Todo 개수 집계
2. 우선순위별, 프로젝트별, 상태별 통계

**추가 기능:**

### Auto-cleanup (자동 정리)
- 완료된 Todo (`[x]`)를 자동 감지
- `completed-todos.md`로 이동
- 월별로 아카이빙

### Smart Suggestions (제안)
- 오래된 Todo 처리 제안
- 같은 프로젝트 Todo 묶어서 처리 제안
- 프로젝트 미지정 Todo 분류 제안
