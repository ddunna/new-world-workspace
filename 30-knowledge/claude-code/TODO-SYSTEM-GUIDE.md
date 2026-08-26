# Todo Management System - Quick Start Guide

> Claude Code 기반 Todo 관리 시스템

---

## 빠른 시작

### 1. Todo 추가하기
```bash
/todo 신제품 출시 콘텐츠 기획
/todo [urgent] 경쟁사 캠페인 분석 마감
/todo [marketing] SNS 콘텐츠 일정 확인
```

### 2. Todo 확인하기
```bash
/todos              # 전체 보기
/todos today        # 오늘 할 일만
/todos project      # 프로젝트별
/todos overdue      # 오래된 것들
```

### 3. 매일 아침 루틴
```bash
/daily-review       # Todo 상태 + 프로젝트 분석
```

---

## 시스템 구조

```
workspace/
├── .claude/commands/
│   ├── /todo          -> 빠른 Todo 추가 (2초)
│   ├── /todos         -> Todo 조회 (다양한 뷰)
│   └── /daily-review  -> 매일 아침 Todo 체크 + 제안
│
└── 40-personal/46-todos/
    ├── active-todos.md        # 중앙 저장소
    └── completed-todos.md     # 완료 아카이브
```

---

## 핵심 기능

### 해결된 문제
1. **"어디에 뒀는지 기억 못함"**
   -> 단일 저장소 (`active-todos.md`)

2. **"장기 프로젝트 생각없이 넘어감"**
   -> `/todos overdue`로 자동 감지

3. **"주기적인 알림 없음"**
   -> `/daily-review`에서 매일 체크

### 자동 저장되는 정보
- **추가 시각**: 언제 추가했는지
- **우선순위**: urgent/high/normal/low
- **프로젝트**: 어떤 프로젝트와 연결됐는지

---

## 실전 시나리오

### 시나리오 1: 작업 중 Todo 생각남
```
SNS 콘텐츠 작업 중
-> "아 신제품 촬영 일정 잡아야지"
-> /todo 신제품 촬영 일정 조율
-> 2초 만에 저장 완료
-> 계속 작업
```

### 시나리오 2: 매일 아침 체크
```
9:00 AM - VS Code 열고
-> /daily-review 실행
-> Todo 상태:
   - 미처리: 5개
   - 오늘 할 일: 2개
   - 지연: 1개
-> 오늘 할 것 선택
-> 실행
```

### 시나리오 3: 프로젝트별 정리
```
/todos project
-> product-launch 관련 3개 발견
-> 미팅 때 한 번에 논의 계획
```

---

## 사용 예시

### Todo 추가 (다양한 방식)

```bash
# 기본
/todo 브랜드 가이드라인 확인

# 우선순위 지정
/todo [urgent] 캠페인 마감 자료 제출
/todo [high] 경쟁사 분석 리포트 작성
/todo [low] 레퍼런스 이미지 수집

# 프로젝트 지정
/todo [marketing] 인스타그램 릴스 기획
/todo [branding] 시즌 비주얼 컨셉 정리
/todo [research] 소비자 인터뷰 정리

# 복합
/todo [urgent] [marketing] SNS 이벤트 공지 마감
```

### Todo 조회 (다양한 뷰)

```bash
# 전체 보기 (섹션별)
/todos
-> Inbox (5개)
-> Today (2개)
-> Overdue (1개)

# 오늘 할 일만
/todos today
-> 우선순위별로 정렬된 오늘 할 일

# 프로젝트별 그룹화
/todos project
-> marketing (3개)
-> branding (2개)
-> research (2개)

# 오래된 것들
/todos overdue
-> 10일 지남: 경쟁사 리뷰 분석

# 통계
/todos stats
-> 총 12개
-> High: 2개, Normal: 8개, Low: 2개
```

---

## Daily Review 통합

`/daily-review` 실행 시 자동으로 포함되는 내용:

```markdown
### 어제 진행 상황
- marketing: SNS 콘텐츠 업로드 완료
- branding: 시즌 비주얼 시안 검토 완료

### Todo 상태 체크
- **미처리 Todo**: 5개
- **오늘 할 일**: 2개
- **지연 중**: 1개 (1주일 이상)

**오늘 처리 제안:**
1. 신제품 출시 콘텐츠 기획 (high priority)
2. 경쟁사 캠페인 분석 (10일 지남)

### 오늘 우선순위 제안
1. Todo 처리 (2개 제안됨)
2. 프로젝트 연속성 유지
```

---

## 커스터마이징

### active-todos.md 직접 편집

파일 위치: `./40-personal/46-todos/active-todos.md`

```markdown
## Inbox (처리 안 한 것들)
- [ ] 신제품 출시 콘텐츠 기획
  - added: 2026-02-04 15:23
  - priority: high
  - project: marketing

## Today (오늘 할 일)
<- 매일 아침 여기로 이동

## Overdue (오래된 것들)
<- 자동 감지 (1주일 이상)
```

### 체크박스 사용

```markdown
- [x] 완료된 Todo  <- 완료 시 x 입력
  -> 자동으로 completed-todos.md로 아카이빙 (향후 기능)
```

---

## 활용 팁

### 1. 프로젝트 묶음 처리
```
/todos project
-> marketing 관련 3개 발견
-> 팀 미팅에서 한 번에 공유하면 효율적
```

### 2. 우선순위 관리
```
/todos today
-> High priority 먼저
-> Normal priority 그 다음
-> Low priority는 시간 나면
```

### 3. Overdue 주기적 체크
```
주 1회 금요일:
/todos overdue
-> 방치된 Todo 확인
-> 삭제 또는 재우선순위화
```

---

## 학습 곡선

### Day 1: 기본 사용
```bash
/todo [내용]        # 추가만 해도 충분
/todos              # 확인
```

### Week 1: 우선순위 추가
```bash
/todo [urgent] [내용]
/todo [marketing] [내용]
```

### Week 2: Daily Review 습관화
```bash
매일 아침: /daily-review
-> Todo 체크 + 오늘 할 일 선택
```

---

## 성공 체크리스트

**시스템이 잘 작동하는 신호:**
- [ ] Todo를 추가할 때 2초 이내에 완료
- [ ] 매일 아침 `/daily-review` 실행
- [ ] "어디에 뒀더라?" 생각 안 남
- [ ] 장기 프로젝트를 놓치지 않음
- [ ] Overdue가 5개 이하 유지

**개선이 필요한 신호:**
- [ ] Todo가 여러 곳에 분산됨
- [ ] 1주일 이상 `/todos` 안 봄
- [ ] Overdue가 10개 이상
- [ ] Todo 추가가 귀찮음

---

## 시작하기

```bash
/todo Todo 시스템 테스트해보기
/todos
```

---

*workspace Todo System v1.0*
