#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Confluence API Handler
Confluence REST API와 상호작용하는 CLI 도구
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
import base64
import mimetypes
import re
from typing import Optional, Dict, List, Any

# Windows 콘솔 UTF-8 출력 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 환경변수 로드
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

if not all([CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN]):
    print("❌ Error: 환경변수가 설정되지 않았습니다.")
    print("다음 환경변수를 설정하세요:")
    print("  - CONFLUENCE_URL")
    print("  - CONFLUENCE_EMAIL")
    print("  - CONFLUENCE_API_TOKEN")
    sys.exit(1)

# API 기본 설정
BASE_URL = f"{CONFLUENCE_URL.rstrip('/')}/wiki/rest/api"
AUTH = (CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)
HEADERS = {"Content-Type": "application/json"}


# ==================== Helper Functions ====================

def make_request(method: str, endpoint: str, **kwargs) -> requests.Response:
    """API 요청 헬퍼 함수"""
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    kwargs.setdefault("auth", AUTH)

    if method.upper() in ["POST", "PUT"]:
        kwargs.setdefault("headers", HEADERS)

    response = requests.request(method, url, **kwargs)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e}")
        try:
            error_detail = response.json()
            print(f"상세: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
        except:
            print(f"응답: {response.text}")
        sys.exit(1)

    return response


def pretty_print(data: Any):
    """JSON 데이터 예쁘게 출력"""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def markdown_to_storage(md_text: str) -> str:
    """마크다운을 Confluence Storage Format으로 변환"""
    # 기본 변환 (간단한 패턴만 지원)
    html = md_text

    # 헤딩
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)

    # 강조
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    html = re.sub(r'__(.+?)__', r'<strong>\1</strong>', html)
    html = re.sub(r'_(.+?)_', r'<em>\1</em>', html)

    # 코드 블록
    def code_block_replace(match):
        lang = match.group(1) or 'text'
        code = match.group(2)
        return f'''<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">{lang}</ac:parameter>
  <ac:plain-text-body><![CDATA[{code}]]></ac:plain-text-body>
</ac:structured-macro>'''

    html = re.sub(r'```(\w+)?\n(.*?)```', code_block_replace, html, flags=re.DOTALL)

    # 인라인 코드
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

    # 링크
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

    # 목록 (간단한 변환)
    html = re.sub(r'^\- (.+)$', r'<ul><li>\1</li></ul>', html, flags=re.MULTILINE)
    html = re.sub(r'^\d+\. (.+)$', r'<ol><li>\1</li></ol>', html, flags=re.MULTILINE)

    # 연속된 ul/ol 태그 병합
    html = re.sub(r'</ul>\n<ul>', '\n', html)
    html = re.sub(r'</ol>\n<ol>', '\n', html)

    # 일반 텍스트 줄은 <p>로 감싸기
    lines = html.split('\n')
    result_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('<'):
            result_lines.append(f'<p>{line}</p>')
        else:
            result_lines.append(line)

    return '\n'.join(result_lines)


# ==================== Space Commands ====================

def list_spaces(args):
    """스페이스 목록 조회"""
    params = {"limit": args.limit or 25}
    response = make_request("GET", "space", params=params)
    data = response.json()

    if args.json:
        pretty_print(data)
    else:
        print(f"📁 총 {len(data['results'])}개의 스페이스:")
        for space in data["results"]:
            print(f"  - {space['key']}: {space['name']}")


def create_space(args):
    """스페이스 생성"""
    payload = {
        "key": args.key,
        "name": args.name,
        "description": {"plain": {"value": args.description or "", "representation": "plain"}}
    }

    response = make_request("POST", "space", json=payload)
    data = response.json()

    print(f"✅ 스페이스 생성 완료: {data['key']} ({data['name']})")
    if args.json:
        pretty_print(data)


def get_space(args):
    """스페이스 정보 조회"""
    response = make_request("GET", f"space/{args.key}")
    data = response.json()

    if args.json:
        pretty_print(data)
    else:
        print(f"📁 스페이스: {data['name']}")
        print(f"  Key: {data['key']}")
        print(f"  ID: {data['id']}")
        print(f"  Type: {data['type']}")


# ==================== Page Commands ====================

def create_page(args):
    """페이지 생성"""
    payload = {
        "type": "page",
        "title": args.title,
        "space": {"key": args.space},
        "body": {
            "storage": {
                "value": args.body,
                "representation": "storage"
            }
        }
    }

    if args.parent:
        payload["ancestors"] = [{"id": args.parent}]

    response = make_request("POST", "content", json=payload)
    data = response.json()

    page_url = f"{CONFLUENCE_URL}/wiki/spaces/{args.space}/pages/{data['id']}"
    print(f"✅ 페이지 생성 완료: {data['title']}")
    print(f"   URL: {page_url}")

    if args.return_id:
        print(data['id'])
    elif args.json:
        pretty_print(data)


def get_page(args):
    """페이지 조회"""
    params = {}
    if args.expand:
        params["expand"] = args.expand

    response = make_request("GET", f"content/{args.id}", params=params)
    data = response.json()

    if args.json:
        pretty_print(data)
    else:
        print(f"📄 페이지: {data['title']}")
        print(f"   ID: {data['id']}")
        print(f"   Space: {data['space']['key']}")
        print(f"   Version: {data['version']['number']}")
        if 'body' in data and 'storage' in data['body']:
            print(f"\n--- 본문 ---")
            print(data['body']['storage']['value'])


def update_page(args):
    """페이지 수정"""
    # 현재 버전 가져오기
    current = make_request("GET", f"content/{args.id}").json()
    current_version = current["version"]["number"]

    payload = {
        "version": {"number": current_version + 1},
        "title": args.title or current["title"],
        "type": "page",
        "body": {
            "storage": {
                "value": args.body or current["body"]["storage"]["value"],
                "representation": "storage"
            }
        }
    }

    response = make_request("PUT", f"content/{args.id}", json=payload)
    data = response.json()

    print(f"✅ 페이지 수정 완료: {data['title']}")
    if args.json:
        pretty_print(data)


def delete_page(args):
    """페이지 삭제"""
    response = make_request("DELETE", f"content/{args.id}")
    print(f"✅ 페이지 삭제 완료 (ID: {args.id})")


def create_page_from_md(args):
    """마크다운 파일로 페이지 생성"""
    md_path = Path(args.file)
    if not md_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {args.file}")
        sys.exit(1)

    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    storage_html = markdown_to_storage(md_content)

    # create_page와 동일한 로직
    payload = {
        "type": "page",
        "title": args.title,
        "space": {"key": args.space},
        "body": {
            "storage": {
                "value": storage_html,
                "representation": "storage"
            }
        }
    }

    if args.parent:
        payload["ancestors"] = [{"id": args.parent}]

    response = make_request("POST", "content", json=payload)
    data = response.json()

    # 레이블 추가 (옵션)
    if args.labels:
        labels = [{"name": label.strip()} for label in args.labels.split(',')]
        make_request("POST", f"content/{data['id']}/label", json=labels)

    page_url = f"{CONFLUENCE_URL}/wiki/spaces/{args.space}/pages/{data['id']}"
    print(f"✅ 마크다운 페이지 생성 완료: {data['title']}")
    print(f"   URL: {page_url}")


def convert_md_to_storage(args):
    """마크다운을 Storage Format으로 변환만"""
    md_path = Path(args.file)
    if not md_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {args.file}")
        sys.exit(1)

    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    storage_html = markdown_to_storage(md_content)
    print(storage_html)


# ==================== Search Commands ====================

def search(args):
    """CQL 검색"""
    params = {
        "cql": args.query,
        "limit": args.limit or 25
    }

    response = make_request("GET", "content/search", params=params)
    data = response.json()

    if args.json:
        pretty_print(data)
    else:
        print(f"🔍 검색 결과: {data['size']}개")
        for item in data["results"]:
            print(f"  - [{item['type']}] {item['title']} (ID: {item['id']})")


# ==================== Attachment Commands ====================

def upload_attachment(args):
    """첨부파일 업로드"""
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {args.file}")
        sys.exit(1)

    # Content-Type 추정
    content_type, _ = mimetypes.guess_type(str(file_path))
    content_type = content_type or "application/octet-stream"

    url = f"{BASE_URL}/content/{args.page_id}/child/attachment"
    headers = {"X-Atlassian-Token": "no-check"}

    with open(file_path, 'rb') as f:
        files = {'file': (file_path.name, f, content_type)}
        response = requests.post(url, auth=AUTH, headers=headers, files=files)

    response.raise_for_status()
    data = response.json()

    print(f"✅ 파일 업로드 완료: {file_path.name}")
    if args.json:
        pretty_print(data)


def list_attachments(args):
    """첨부파일 목록 조회"""
    response = make_request("GET", f"content/{args.page_id}/child/attachment")
    data = response.json()

    if args.json:
        pretty_print(data)
    else:
        print(f"📎 첨부파일 {len(data['results'])}개:")
        for att in data["results"]:
            print(f"  - {att['title']} (ID: {att['id']})")


def download_attachment(args):
    """첨부파일 다운로드"""
    # 첨부파일 정보 가져오기
    response = make_request("GET", f"content/{args.attachment_id}")
    data = response.json()

    download_url = f"{CONFLUENCE_URL}/wiki{data['_links']['download']}"

    # 다운로드
    response = requests.get(download_url, auth=AUTH)
    response.raise_for_status()

    output_path = Path(args.output)
    with open(output_path, 'wb') as f:
        f.write(response.content)

    print(f"✅ 다운로드 완료: {output_path}")


# ==================== Comment Commands ====================

def add_comment(args):
    """코멘트 추가"""
    payload = {
        "type": "comment",
        "container": {"id": args.page_id, "type": "page"},
        "body": {
            "storage": {
                "value": args.body,
                "representation": "storage"
            }
        }
    }

    response = make_request("POST", "content", json=payload)
    data = response.json()

    print(f"✅ 코멘트 추가 완료")
    if args.json:
        pretty_print(data)


def get_comments(args):
    """코멘트 조회"""
    response = make_request("GET", f"content/{args.page_id}/child/comment")
    data = response.json()

    if args.json:
        pretty_print(data)
    else:
        print(f"💬 코멘트 {len(data['results'])}개:")
        for comment in data["results"]:
            print(f"  - {comment['title']}")


# ==================== Label Commands ====================

def add_labels(args):
    """레이블 추가"""
    labels = [{"name": label.strip()} for label in args.labels.split(',')]

    response = make_request("POST", f"content/{args.page_id}/label", json=labels)
    data = response.json()

    print(f"✅ 레이블 추가 완료: {args.labels}")
    if args.json:
        pretty_print(data)


def get_labels(args):
    """레이블 조회"""
    response = make_request("GET", f"content/{args.page_id}/label")
    data = response.json()

    if args.json:
        pretty_print(data)
    else:
        print(f"🏷️  레이블 {len(data['results'])}개:")
        for label in data["results"]:
            print(f"  - {label['name']}")


def remove_label(args):
    """레이블 삭제"""
    response = make_request("DELETE", f"content/{args.page_id}/label/{args.label}")
    print(f"✅ 레이블 삭제 완료: {args.label}")


# ==================== Page Tree Commands ====================

def get_child_pages(args):
    """자식 페이지 조회"""
    response = make_request("GET", f"content/{args.page_id}/child/page")
    data = response.json()

    if args.json:
        pretty_print(data)
    else:
        print(f"📂 자식 페이지 {len(data['results'])}개:")
        for page in data["results"]:
            print(f"  - {page['title']} (ID: {page['id']})")


def get_page_tree(args):
    """페이지 트리 조회 (재귀적)"""
    def fetch_tree(page_id, depth=0, max_depth=3):
        if depth > max_depth:
            return

        response = make_request("GET", f"content/{page_id}")
        page = response.json()

        indent = "  " * depth
        print(f"{indent}- {page['title']} (ID: {page['id']})")

        children_response = make_request("GET", f"content/{page_id}/child/page")
        children = children_response.json()

        for child in children["results"]:
            fetch_tree(child["id"], depth + 1, max_depth)

    print(f"🌳 페이지 트리 (depth={args.depth}):")
    fetch_tree(args.page_id, max_depth=args.depth)


# ==================== Template Commands ====================

TEMPLATES = {
    "meeting-notes": """
<h1>회의록: {title}</h1>
<p><strong>날짜:</strong> {date}</p>
<p><strong>참석자:</strong> {attendees}</p>

<h2>안건</h2>
<ul>
  <li>항목 1</li>
  <li>항목 2</li>
</ul>

<h2>논의 내용</h2>
<p>내용을 입력하세요...</p>

<h2>결정 사항</h2>
<ul>
  <li>결정 1</li>
</ul>

<h2>액션 아이템</h2>
<table>
  <tbody>
    <tr>
      <th>작업</th>
      <th>담당자</th>
      <th>마감일</th>
    </tr>
    <tr>
      <td>작업 1</td>
      <td>이름</td>
      <td>날짜</td>
    </tr>
  </tbody>
</table>
""",
    "project-plan": """
<h1>{project_name} 프로젝트 계획서</h1>
<p><strong>프로젝트 오너:</strong> {owner}</p>

<h2>개요</h2>
<p>프로젝트 설명...</p>

<h2>목표</h2>
<ul>
  <li>목표 1</li>
  <li>목표 2</li>
</ul>

<h2>일정</h2>
<table>
  <tbody>
    <tr>
      <th>단계</th>
      <th>기간</th>
      <th>담당자</th>
    </tr>
  </tbody>
</table>

<h2>리소스</h2>
<p>필요 리소스...</p>

<h2>위험 요소</h2>
<p>잠재적 위험...</p>
"""
}


def create_from_template(args):
    """템플릿으로 페이지 생성"""
    if args.template not in TEMPLATES:
        print(f"❌ 템플릿을 찾을 수 없습니다: {args.template}")
        print(f"사용 가능한 템플릿: {', '.join(TEMPLATES.keys())}")
        sys.exit(1)

    template = TEMPLATES[args.template]

    # 변수 치환
    vars_dict = json.loads(args.vars) if args.vars else {}
    body = template.format(title=args.title, **vars_dict)

    # 페이지 생성
    payload = {
        "type": "page",
        "title": args.title,
        "space": {"key": args.space},
        "body": {
            "storage": {
                "value": body,
                "representation": "storage"
            }
        }
    }

    response = make_request("POST", "content", json=payload)
    data = response.json()

    page_url = f"{CONFLUENCE_URL}/wiki/spaces/{args.space}/pages/{data['id']}"
    print(f"✅ 템플릿 페이지 생성 완료: {data['title']}")
    print(f"   URL: {page_url}")


# ==================== Main ====================

def main():
    parser = argparse.ArgumentParser(description="Confluence API CLI")
    subparsers = parser.add_subparsers(dest="command", help="명령어")

    # Space
    sp_list = subparsers.add_parser("list-spaces", help="스페이스 목록")
    sp_list.add_argument("--limit", type=int)
    sp_list.add_argument("--json", action="store_true")
    sp_list.set_defaults(func=list_spaces)

    sp_create = subparsers.add_parser("create-space", help="스페이스 생성")
    sp_create.add_argument("--key", required=True)
    sp_create.add_argument("--name", required=True)
    sp_create.add_argument("--description")
    sp_create.add_argument("--json", action="store_true")
    sp_create.set_defaults(func=create_space)

    sp_get = subparsers.add_parser("get-space", help="스페이스 조회")
    sp_get.add_argument("--key", required=True)
    sp_get.add_argument("--json", action="store_true")
    sp_get.set_defaults(func=get_space)

    # Page
    pg_create = subparsers.add_parser("create-page", help="페이지 생성")
    pg_create.add_argument("--space", required=True)
    pg_create.add_argument("--title", required=True)
    pg_create.add_argument("--body", required=True)
    pg_create.add_argument("--parent")
    pg_create.add_argument("--json", action="store_true")
    pg_create.add_argument("--return-id", action="store_true")
    pg_create.set_defaults(func=create_page)

    pg_get = subparsers.add_parser("get-page", help="페이지 조회")
    pg_get.add_argument("--id", required=True)
    pg_get.add_argument("--expand")
    pg_get.add_argument("--json", action="store_true")
    pg_get.set_defaults(func=get_page)

    pg_update = subparsers.add_parser("update-page", help="페이지 수정")
    pg_update.add_argument("--id", required=True)
    pg_update.add_argument("--title")
    pg_update.add_argument("--body")
    pg_update.add_argument("--json", action="store_true")
    pg_update.set_defaults(func=update_page)

    pg_delete = subparsers.add_parser("delete-page", help="페이지 삭제")
    pg_delete.add_argument("--id", required=True)
    pg_delete.set_defaults(func=delete_page)

    pg_md = subparsers.add_parser("create-page-from-md", help="마크다운으로 페이지 생성")
    pg_md.add_argument("--space", required=True)
    pg_md.add_argument("--title", required=True)
    pg_md.add_argument("--file", required=True)
    pg_md.add_argument("--parent")
    pg_md.add_argument("--labels")
    pg_md.set_defaults(func=create_page_from_md)

    md_convert = subparsers.add_parser("convert-md-to-storage", help="마크다운 변환")
    md_convert.add_argument("--file", required=True)
    md_convert.set_defaults(func=convert_md_to_storage)

    # Search
    search_cmd = subparsers.add_parser("search", help="CQL 검색")
    search_cmd.add_argument("--query", required=True)
    search_cmd.add_argument("--limit", type=int)
    search_cmd.add_argument("--json", action="store_true")
    search_cmd.set_defaults(func=search)

    # Attachment
    att_upload = subparsers.add_parser("upload-attachment", help="첨부파일 업로드")
    att_upload.add_argument("--page-id", required=True)
    att_upload.add_argument("--file", required=True)
    att_upload.add_argument("--json", action="store_true")
    att_upload.set_defaults(func=upload_attachment)

    att_list = subparsers.add_parser("list-attachments", help="첨부파일 목록")
    att_list.add_argument("--page-id", required=True)
    att_list.add_argument("--json", action="store_true")
    att_list.set_defaults(func=list_attachments)

    att_dl = subparsers.add_parser("download-attachment", help="첨부파일 다운로드")
    att_dl.add_argument("--attachment-id", required=True)
    att_dl.add_argument("--output", required=True)
    att_dl.set_defaults(func=download_attachment)

    # Comment
    cmt_add = subparsers.add_parser("add-comment", help="코멘트 추가")
    cmt_add.add_argument("--page-id", required=True)
    cmt_add.add_argument("--body", required=True)
    cmt_add.add_argument("--json", action="store_true")
    cmt_add.set_defaults(func=add_comment)

    cmt_get = subparsers.add_parser("get-comments", help="코멘트 조회")
    cmt_get.add_argument("--page-id", required=True)
    cmt_get.add_argument("--json", action="store_true")
    cmt_get.set_defaults(func=get_comments)

    # Label
    lbl_add = subparsers.add_parser("add-labels", help="레이블 추가")
    lbl_add.add_argument("--page-id", required=True)
    lbl_add.add_argument("--labels", required=True, help="쉼표로 구분")
    lbl_add.add_argument("--json", action="store_true")
    lbl_add.set_defaults(func=add_labels)

    lbl_get = subparsers.add_parser("get-labels", help="레이블 조회")
    lbl_get.add_argument("--page-id", required=True)
    lbl_get.add_argument("--json", action="store_true")
    lbl_get.set_defaults(func=get_labels)

    lbl_rm = subparsers.add_parser("remove-label", help="레이블 삭제")
    lbl_rm.add_argument("--page-id", required=True)
    lbl_rm.add_argument("--label", required=True)
    lbl_rm.set_defaults(func=remove_label)

    # Page Tree
    tree_child = subparsers.add_parser("get-child-pages", help="자식 페이지 조회")
    tree_child.add_argument("--page-id", required=True)
    tree_child.add_argument("--json", action="store_true")
    tree_child.set_defaults(func=get_child_pages)

    tree_full = subparsers.add_parser("get-page-tree", help="페이지 트리 조회")
    tree_full.add_argument("--page-id", required=True)
    tree_full.add_argument("--depth", type=int, default=3)
    tree_full.set_defaults(func=get_page_tree)

    # Template
    tpl_create = subparsers.add_parser("create-from-template", help="템플릿으로 페이지 생성")
    tpl_create.add_argument("--space", required=True)
    tpl_create.add_argument("--template", required=True)
    tpl_create.add_argument("--title", required=True)
    tpl_create.add_argument("--vars", help="JSON 형식의 변수")
    tpl_create.set_defaults(func=create_from_template)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
