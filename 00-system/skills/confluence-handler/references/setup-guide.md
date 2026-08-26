# Confluence 스킬 설정 가이드

## 1. API 토큰 발급

### Atlassian Cloud
1. [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens) 접속
2. "Create API token" 클릭
3. 토큰 이름 입력 (예: "Claude Code Integration")
4. 생성된 토큰 복사 (⚠️ 다시 볼 수 없으니 안전한 곳에 저장)

## 2. 환경변수 설정

### Windows (PowerShell)
```powershell
# 현재 세션에만 적용
$env:CONFLUENCE_URL = "https://your-domain.atlassian.net"
$env:CONFLUENCE_EMAIL = "your-email@company.com"
$env:CONFLUENCE_API_TOKEN = "your_api_token_here"

# 영구 적용 (사용자 환경변수)
[System.Environment]::SetEnvironmentVariable('CONFLUENCE_URL', 'https://your-domain.atlassian.net', 'User')
[System.Environment]::SetEnvironmentVariable('CONFLUENCE_EMAIL', 'your-email@company.com', 'User')
[System.Environment]::SetEnvironmentVariable('CONFLUENCE_API_TOKEN', 'your_api_token_here', 'User')
```

### macOS/Linux (Bash/Zsh)
```bash
# ~/.bashrc 또는 ~/.zshrc 에 추가
export CONFLUENCE_URL="https://your-domain.atlassian.net"
export CONFLUENCE_EMAIL="your-email@company.com"
export CONFLUENCE_API_TOKEN="your_api_token_here"

# 적용
source ~/.bashrc  # or source ~/.zshrc
```

## 3. Python 패키지 설치

```bash
pip install requests
```

## 4. 테스트

```bash
# 스페이스 목록 조회
python3 ~/.claude/skills/confluence-handler/scripts/confluence_api.py list-spaces

# 정상 작동하면 스페이스 목록이 출력됩니다
```

## 5. 자주 묻는 질문

### Q: "401 Unauthorized" 에러가 발생해요
A: API 토큰이나 이메일이 잘못 설정되었을 수 있습니다. 환경변수를 다시 확인하세요.

### Q: "403 Forbidden" 에러가 발생해요
A: Confluence 스페이스/페이지에 대한 권한이 없을 수 있습니다. 관리자에게 권한 요청하세요.

### Q: "404 Not Found" 에러가 발생해요
A: 페이지 ID나 스페이스 키가 잘못되었을 수 있습니다. ID를 다시 확인하세요.

### Q: 마크다운 변환이 완벽하지 않아요
A: 현재 기본적인 마크다운만 지원합니다. 복잡한 형식은 Confluence Storage Format으로 직접 작성하세요.

## 6. 보안 주의사항

- ⚠️ API 토큰은 **절대 Git에 커밋하지 마세요**
- ⚠️ 환경변수 파일(.env)은 `.gitignore`에 추가하세요
- ⚠️ 토큰이 노출되면 즉시 재발급하세요
- ⚠️ 중요한 페이지 삭제 전 백업하세요

## 7. 유용한 링크

- [Confluence REST API 공식 문서](https://developer.atlassian.com/cloud/confluence/rest/v1/intro/)
- [Confluence Storage Format 가이드](https://confluence.atlassian.com/doc/confluence-storage-format-790796544.html)
- [CQL (Confluence Query Language)](https://developer.atlassian.com/cloud/confluence/advanced-searching-using-cql/)
