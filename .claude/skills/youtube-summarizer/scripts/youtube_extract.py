#!/usr/bin/env python3
"""
YouTube 영상 정보 추출 스크립트
- 메타데이터 (제목, 채널, 조회수, 업로드일, 설명 등)
- 자막/트랜스크립트 추출 (한국어 우선)
"""

import sys
import os
import json
import re
import argparse
from datetime import datetime

# Windows 콘솔 UTF-8 출력 강제
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter


def extract_video_id(url: str) -> str:
    """YouTube URL에서 video ID 추출."""
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:embed/)([a-zA-Z0-9_-]{11})',
        r'(?:shorts/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    # 이미 video ID일 수 있음
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url
    raise ValueError(f"YouTube video ID를 찾을 수 없습니다: {url}")


def get_metadata(url: str) -> dict:
    """yt-dlp로 영상 메타데이터 추출."""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    upload_date = info.get('upload_date', '')
    if upload_date and len(upload_date) == 8:
        upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"

    duration_sec = info.get('duration', 0)
    hours = duration_sec // 3600
    minutes = (duration_sec % 3600) // 60
    seconds = duration_sec % 60
    if hours > 0:
        duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        duration_str = f"{minutes}:{seconds:02d}"

    return {
        'video_id': info.get('id', ''),
        'title': info.get('title', ''),
        'channel': info.get('channel', '') or info.get('uploader', ''),
        'channel_url': info.get('channel_url', '') or info.get('uploader_url', ''),
        'upload_date': upload_date,
        'duration': duration_str,
        'duration_seconds': duration_sec,
        'view_count': info.get('view_count', 0),
        'like_count': info.get('like_count', 0),
        'description': info.get('description', ''),
        'tags': info.get('tags', []) or [],
        'categories': info.get('categories', []) or [],
        'thumbnail': info.get('thumbnail', ''),
        'url': info.get('webpage_url', url),
    }


def get_transcript(video_id: str) -> dict:
    """YouTube 자막/트랜스크립트 추출. 한국어 우선."""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # 한국어 자막 우선 시도
        transcript = None
        lang_used = ''

        # 1) 수동 자막 (한국어)
        try:
            transcript = transcript_list.find_manually_created_transcript(['ko'])
            lang_used = 'ko (수동)'
        except Exception:
            pass

        # 2) 자동 생성 자막 (한국어)
        if not transcript:
            try:
                transcript = transcript_list.find_generated_transcript(['ko'])
                lang_used = 'ko (자동생성)'
            except Exception:
                pass

        # 3) 영어 자막
        if not transcript:
            try:
                transcript = transcript_list.find_manually_created_transcript(['en'])
                lang_used = 'en (수동)'
            except Exception:
                pass

        if not transcript:
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
                lang_used = 'en (자동생성)'
            except Exception:
                pass

        # 4) 아무 자막이라도
        if not transcript:
            for t in transcript_list:
                transcript = t
                lang_used = f'{t.language_code} ({"수동" if not t.is_generated else "자동생성"})'
                break

        if not transcript:
            return {'available': False, 'language': '', 'text': '', 'segments': []}

        fetched = transcript.fetch()
        formatter = TextFormatter()
        full_text = formatter.format_transcript(fetched)

        segments = []
        for entry in fetched:
            segments.append({
                'start': round(entry.start, 1),
                'duration': round(entry.duration, 1),
                'text': entry.text,
            })

        return {
            'available': True,
            'language': lang_used,
            'text': full_text,
            'segments': segments,
        }

    except Exception as e:
        return {
            'available': False,
            'language': '',
            'text': '',
            'segments': [],
            'error': str(e),
        }


def main():
    parser = argparse.ArgumentParser(description='YouTube 영상 정보 추출')
    parser.add_argument('url', help='YouTube URL 또는 Video ID')
    parser.add_argument('--no-transcript', action='store_true', help='자막 추출 건너뛰기')
    parser.add_argument('--output', '-o', help='결과 저장 파일 경로 (JSON)')

    args = parser.parse_args()

    video_id = extract_video_id(args.url)
    url = f"https://www.youtube.com/watch?v={video_id}"

    # 메타데이터 추출
    print(f"메타데이터 추출 중... ({video_id})", file=sys.stderr)
    metadata = get_metadata(url)

    # 자막 추출
    transcript = {'available': False}
    if not args.no_transcript:
        print("자막 추출 중...", file=sys.stderr)
        transcript = get_transcript(video_id)

    result = {
        'extracted_at': datetime.now().isoformat(),
        'metadata': metadata,
        'transcript': transcript,
    }

    output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"저장 완료: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
