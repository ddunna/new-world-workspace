---
description: 빠르게 Todo를 추가하는 커맨드 (컨텍스트 자동 수집, 우선순위 감지)
argument-hint: [urgent] Todo 내용
allowed-tools: Read, Write, Edit, Bash
---

빠르게 Todo를 추가해주세요.

**사용 예시:**
```
/todo 신제품 출시 콘텐츠 기획
/todo [urgent] 경쟁사 캠페인 분석 마감
/todo [marketing] SNS 콘텐츠 일정 확인
```

**수행할 작업:**

1. **컨텍스트 수집**
   - 현재 작업 디렉토리 확인 (`pwd`)
   - 추가 시각 (timestamp)

2. **우선순위 자동 감지**
   - `[urgent]` 또는 `[high]` -> high priority
   - `[low]` -> low priority
   - 없으면 -> normal priority

3. **프로젝트 자동 연결**
   - `[프로젝트명]` -> 해당 프로젝트에 연결
   - 현재 디렉토리가 프로젝트면 자동 연결

4. **저장**
   - 경로: `./40-personal/46-todos/active-todos.md`
   - 섹션: "Inbox"
   - 형식:
     ```markdown
     - [ ] [Todo 내용]
       - added: YYYY-MM-DD HH:mm
       - priority: [high/normal/low]
       - project: [프로젝트명 (있으면)]
     ```

5. **확인 메시지 출력**
   ```
   Todo 추가됨: [내용]
   Priority: normal

   /todos 로 전체 목록을 확인하세요.
   ```
