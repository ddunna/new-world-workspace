"""
네이버 검색광고 키워드도구 API → 구글시트 검색트렌드 + data.json 연동
- 16개 MOTION 캠페인 키워드의 월간 검색량(PC+모바일) 수집
- 구글시트 '검색트렌드' 시트에 오늘 날짜 행 append/update
- 대시보드 data.json의 searchTrendData 업데이트
"""

import os
import json
import time
import hashlib
import hmac
import base64
import urllib.request
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv

WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
load_dotenv(os.path.join(WORKSPACE, '.env'))

# 네이버 검색광고 API
CUSTOMER_ID = os.getenv('NAVER_AD_CUSTOMER_ID')
API_KEY = os.getenv('NAVER_AD_ACCESS_LICENSE')
SECRET_KEY = os.getenv('NAVER_AD_SECRET_KEY')
BASE_URL = 'https://api.searchad.naver.com'

# 구글시트
SPREADSHEET_ID = '14CkPEbaIZ1P9goS0n8b5fXfou9wib9O0mbK8l61TsdM'
TOKEN_PATH = os.path.join(WORKSPACE, 'token.json')
SHEET_NAME = '검색트렌드'

# 대시보드 data.json
DATA_JSON_PATH = os.path.join(
    WORKSPACE, '10-projects', '13-motion dashboard',
    '2026-motion-campaign-dashboard', 'src', 'data.json'
)

# 16개 타겟 키워드 (구글시트 컬럼 순서와 동일)
TARGET_KEYWORDS = [
    '{브랜드명}', '{브랜드명}모션', '{브랜드명}{모델명}', '{모델명}{브랜드명}',
    '{브랜드명}모션베드', '{브랜드명}바젤모션베드', '{브랜드명}바젤', '바젤침대',
    '{브랜드명}업모션', '{브랜드명}모션테이블', '업모션테이블', '{브랜드명}업모션테이블',
    '{브랜드명}모션데스크', '{브랜드명}뉴트', '{브랜드명}뉴트모션데스크', '뉴트모션데스크',
]

# API hintKeywords 최대 5개 → 4회 호출
KEYWORD_BATCHES = [
    TARGET_KEYWORDS[0:5],
    TARGET_KEYWORDS[5:10],
    TARGET_KEYWORDS[10:15],
    TARGET_KEYWORDS[15:16],
]


def generate_signature(timestamp, method, uri):
    message = f'{timestamp}.{method}.{uri}'
    hashed = hmac.HMAC(
        SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    )
    return base64.b64encode(hashed.digest()).decode('utf-8')


def call_keyword_tool(keywords):
    """키워드도구 API 호출 — 최대 5개 키워드"""
    uri = '/keywordstool'
    method = 'GET'
    timestamp = str(round(time.time() * 1000))

    params = {
        'hintKeywords': ','.join(keywords),
        'showDetail': '1',
    }
    query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    url = f'{BASE_URL}{uri}?{query_string}'

    signature = generate_signature(timestamp, method, uri)

    req = urllib.request.Request(url)
    req.add_header('X-API-KEY', API_KEY)
    req.add_header('X-Customer', CUSTOMER_ID)
    req.add_header('X-Timestamp', timestamp)
    req.add_header('X-Signature', signature)

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))


def parse_search_volume(value):
    """검색수 파싱 ('< 10' 등 문자열 처리)"""
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        value = value.strip().replace(',', '')
        if value.startswith('<') or value == '< 10':
            return 5
        try:
            return int(value)
        except ValueError:
            return 0
    return 0


def fetch_all_keywords():
    """14개 키워드의 월간 검색량 수집"""
    print('[1/3] 네이버 검색광고 키워드도구 API 호출...')

    results = {}
    for i, batch in enumerate(KEYWORD_BATCHES):
        print(f'  batch {i+1}/{len(KEYWORD_BATCHES)}: {", ".join(batch)}')
        try:
            resp = call_keyword_tool(batch)
            for kw_data in resp.get('keywordList', []):
                rel = kw_data.get('relKeyword', '')
                if rel in TARGET_KEYWORDS:
                    pc = parse_search_volume(kw_data.get('monthlyPcQcCnt', 0))
                    mobile = parse_search_volume(kw_data.get('monthlyMobileQcCnt', 0))
                    results[rel] = pc + mobile
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f'  [API ERROR] {e.code}: {error_body}')
        time.sleep(0.5)

    # 누락된 키워드는 0으로 채우기
    for kw in TARGET_KEYWORDS:
        if kw not in results:
            results[kw] = 0
            print(f'  [WARN] "{kw}" 데이터 없음 (0 처리)')

    return results


def update_google_sheet(today_str, keyword_data):
    """구글시트 검색트렌드 시트에 오늘 행 추가/갱신"""
    print('[2/3] 구글시트 업데이트...')
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        if not os.path.exists(TOKEN_PATH):
            print('  [SKIP] token.json 없음')
            return False

        creds = Credentials.from_authorized_user_file(
            TOKEN_PATH,
            ['https://www.googleapis.com/auth/spreadsheets']
        )
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        service = build('sheets', 'v4', credentials=creds)
        sheets = service.spreadsheets()

        # 기존 date 컬럼 읽기 (중복 체크)
        existing = sheets.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{SHEET_NAME}'!A:A",
        ).execute()
        existing_dates = [row[0] for row in existing.get('values', []) if row]

        # 오늘 행 데이터
        row = [today_str] + [keyword_data.get(kw, 0) for kw in TARGET_KEYWORDS]

        if today_str in existing_dates:
            # 이미 오늘 데이터가 있으면 해당 행 덮어쓰기
            row_idx = existing_dates.index(today_str) + 1  # 1-based
            range_str = f"'{SHEET_NAME}'!A{row_idx}:Q{row_idx}"
            sheets.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=range_str,
                valueInputOption='USER_ENTERED',
                body={'values': [row]},
            ).execute()
            print(f'  기존 행 갱신 (row {row_idx})')
        else:
            # 새 행 append
            sheets.values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=f"'{SHEET_NAME}'!A1",
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body={'values': [row]},
            ).execute()
            print(f'  새 행 추가')

        return True
    except Exception as e:
        print(f'  [ERROR] 구글시트 업데이트 실패: {e}')
        return False


def update_data_json(today_str, keyword_data):
    """대시보드 data.json의 searchTrendData 업데이트"""
    print('[3/3] data.json 업데이트...')
    try:
        with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        entry = {'date': today_str}
        for kw in TARGET_KEYWORDS:
            entry[kw] = keyword_data.get(kw, 0)

        # 기존에 같은 날짜가 있으면 갱신, 없으면 추가
        trend_data = data.get('searchTrendData', [])
        found = False
        for i, item in enumerate(trend_data):
            if item.get('date') == today_str:
                trend_data[i] = entry
                found = True
                break
        if not found:
            trend_data.append(entry)

        data['searchTrendData'] = trend_data
        data['_meta']['syncedAt'] = datetime.now().isoformat()

        with open(DATA_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f'  searchTrendData 업데이트 완료 (총 {len(trend_data)}일)')
        return True
    except Exception as e:
        print(f'  [ERROR] data.json 업데이트 실패: {e}')
        return False


def main():
    print('=== MOTION 키워드 검색량 수집 ===\n')

    if not all([CUSTOMER_ID, API_KEY, SECRET_KEY]):
        print('[ERROR] .env에 NAVER_AD_CUSTOMER_ID / NAVER_AD_ACCESS_LICENSE / NAVER_AD_SECRET_KEY 필요')
        return

    today_str = datetime.now().strftime('%Y-%m-%d')
    print(f'날짜: {today_str}\n')

    # 1. API 호출
    keyword_data = fetch_all_keywords()

    # 결과 출력
    print(f'\n  === 월간 검색량 (PC + 모바일) ===')
    for kw in TARGET_KEYWORDS:
        vol = keyword_data.get(kw, 0)
        print(f'  {kw:20s} | {vol:>8,}')

    # 2. 구글시트 업데이트
    print()
    update_google_sheet(today_str, keyword_data)

    # 3. data.json 업데이트
    update_data_json(today_str, keyword_data)

    print(f'\n[OK] 완료!')


if __name__ == '__main__':
    main()
