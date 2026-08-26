"""Google Calendar API CRUD 핸들러

사용법:
    py gcal_api.py list [--max N] [--q KEYWORD]
    py gcal_api.py get EVENT_ID
    py gcal_api.py insert --summary TITLE --start START --end END [--location LOC] [--desc DESC] [--tz TZ]
    py gcal_api.py quick-add TEXT
    py gcal_api.py update EVENT_ID --summary TITLE [--start START] [--end END] [--location LOC] [--desc DESC]
    py gcal_api.py delete EVENT_ID
    py gcal_api.py calendars
"""

import argparse
import json
import os
import sys
import datetime
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Windows 콘솔 UTF-8 설정
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

SCOPES = ["https://www.googleapis.com/auth/calendar"]
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
CREDENTIALS_FILE = os.path.join(WORKSPACE_ROOT, "credentials.json")
TOKEN_FILE = os.path.join(WORKSPACE_ROOT, "token.json")
DEFAULT_TZ = "Asia/Seoul"


def get_service():
    """Google Calendar API 서비스 객체 반환"""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)


def cmd_list(args):
    """일정 목록 조회"""
    service = get_service()
    now = datetime.datetime.now(tz=ZoneInfo(DEFAULT_TZ)).isoformat()
    params = {
        "calendarId": "primary",
        "timeMin": now,
        "maxResults": args.max,
        "singleEvents": True,
        "orderBy": "startTime",
    }
    if args.q:
        params["q"] = args.q
    result = service.events().list(**params).execute()
    events = result.get("items", [])
    if not events:
        print("일정 없음")
        return
    print(f"향후 일정 {len(events)}건:\n")
    for e in events:
        start = e["start"].get("dateTime", e["start"].get("date"))
        summary = e.get("summary", "(제목 없음)")
        eid = e["id"]
        location = e.get("location", "")
        loc_str = f" | {location}" if location else ""
        print(f"  [{eid[:12]}]  {start}  {summary}{loc_str}")


def cmd_get(args):
    """단일 일정 조회"""
    service = get_service()
    event = service.events().get(calendarId="primary", eventId=args.event_id).execute()
    print(json.dumps(event, indent=2, ensure_ascii=False))


def cmd_insert(args):
    """일정 생성"""
    service = get_service()
    tz = args.tz or DEFAULT_TZ
    body = {
        "summary": args.summary,
        "start": {"dateTime": args.start, "timeZone": tz},
        "end": {"dateTime": args.end, "timeZone": tz},
    }
    if args.location:
        body["location"] = args.location
    if args.desc:
        body["description"] = args.desc
    if args.attendees:
        body["attendees"] = [{"email": e.strip()} for e in args.attendees.split(",")]
    if args.recurrence:
        body["recurrence"] = [args.recurrence]
    event = service.events().insert(calendarId="primary", body=body).execute()
    print(f"생성 완료: {event['id']}")
    print(f"제목: {event.get('summary')}")
    print(f"링크: {event.get('htmlLink')}")


def cmd_quick_add(args):
    """자연어로 일정 빠르게 추가"""
    service = get_service()
    event = service.events().quickAdd(calendarId="primary", text=args.text).execute()
    print(f"생성 완료: {event['id']}")
    print(f"제목: {event.get('summary')}")
    start = event.get("start", {}).get("dateTime", event.get("start", {}).get("date", ""))
    print(f"시작: {start}")
    print(f"링크: {event.get('htmlLink')}")


def cmd_update(args):
    """일정 수정 (patch)"""
    service = get_service()
    body = {}
    if args.summary:
        body["summary"] = args.summary
    if args.start:
        tz = args.tz or DEFAULT_TZ
        body["start"] = {"dateTime": args.start, "timeZone": tz}
    if args.end:
        tz = args.tz or DEFAULT_TZ
        body["end"] = {"dateTime": args.end, "timeZone": tz}
    if args.location:
        body["location"] = args.location
    if args.desc:
        body["description"] = args.desc
    if not body:
        print("수정할 필드가 없습니다.")
        return
    event = service.events().patch(calendarId="primary", eventId=args.event_id, body=body).execute()
    print(f"수정 완료: {event['id']}")
    print(f"제목: {event.get('summary')}")
    print(f"시작: {event['start'].get('dateTime', event['start'].get('date'))}")


def cmd_delete(args):
    """일정 삭제"""
    service = get_service()
    service.events().delete(calendarId="primary", eventId=args.event_id).execute()
    print(f"삭제 완료: {args.event_id}")


def cmd_calendars(args):
    """캘린더 목록 조회"""
    service = get_service()
    result = service.calendarList().list(maxResults=50).execute()
    calendars = result.get("items", [])
    print(f"캘린더 {len(calendars)}개:\n")
    for cal in calendars:
        primary = " (기본)" if cal.get("primary") else ""
        role = cal.get("accessRole", "")
        print(f"  [{role:6s}] {cal['summary']}{primary}")
        print(f"           ID: {cal['id']}")


def main():
    parser = argparse.ArgumentParser(description="Google Calendar API CRUD")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = sub.add_parser("list", help="일정 목록 조회")
    p_list.add_argument("--max", type=int, default=10)
    p_list.add_argument("--q", help="검색 키워드")

    # get
    p_get = sub.add_parser("get", help="단일 일정 조회")
    p_get.add_argument("event_id")

    # insert
    p_ins = sub.add_parser("insert", help="일정 생성")
    p_ins.add_argument("--summary", required=True)
    p_ins.add_argument("--start", required=True, help="RFC3339 예: 2026-03-01T10:00:00+09:00")
    p_ins.add_argument("--end", required=True, help="RFC3339 예: 2026-03-01T11:00:00+09:00")
    p_ins.add_argument("--location")
    p_ins.add_argument("--desc")
    p_ins.add_argument("--tz", default=DEFAULT_TZ)
    p_ins.add_argument("--attendees", help="쉼표 구분 이메일")
    p_ins.add_argument("--recurrence", help="RRULE 예: RRULE:FREQ=WEEKLY;BYDAY=FR")

    # quick-add
    p_qa = sub.add_parser("quick-add", help="자연어로 일정 추가")
    p_qa.add_argument("text")

    # update
    p_upd = sub.add_parser("update", help="일정 수정")
    p_upd.add_argument("event_id")
    p_upd.add_argument("--summary")
    p_upd.add_argument("--start")
    p_upd.add_argument("--end")
    p_upd.add_argument("--location")
    p_upd.add_argument("--desc")
    p_upd.add_argument("--tz", default=DEFAULT_TZ)

    # delete
    p_del = sub.add_parser("delete", help="일정 삭제")
    p_del.add_argument("event_id")

    # calendars
    sub.add_parser("calendars", help="캘린더 목록 조회")

    args = parser.parse_args()

    try:
        {
            "list": cmd_list,
            "get": cmd_get,
            "insert": cmd_insert,
            "quick-add": cmd_quick_add,
            "update": cmd_update,
            "delete": cmd_delete,
            "calendars": cmd_calendars,
        }[args.command](args)
    except HttpError as e:
        print(f"API 오류 [{e.resp.status}]: {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
