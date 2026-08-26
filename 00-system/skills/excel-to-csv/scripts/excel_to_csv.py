#!/usr/bin/env python3
"""Excel(.xlsx) → CSV 변환 스크립트

사용법:
  python3 excel_to_csv.py list-sheets --file <파일경로>
  python3 excel_to_csv.py convert --file <파일경로>
  python3 excel_to_csv.py convert --file <파일경로> --sheet <시트명>
"""

import sys
import os
import csv
import argparse
import re

# Windows 터미널 인코딩 강제 UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def check_openpyxl():
    try:
        import openpyxl
        return openpyxl
    except ImportError:
        print("[ERROR] openpyxl이 설치되지 않았습니다.")
        print("   다음 명령어로 설치하세요:")
        print("   pip install openpyxl")
        sys.exit(1)


def safe_filename(name):
    """시트명에서 파일명으로 사용할 수 없는 문자 제거"""
    return re.sub(r'[\\/:*?"<>|]', '_', name)


def list_sheets(file_path):
    """시트 목록과 행/열 수 출력"""
    openpyxl = check_openpyxl()

    if not os.path.exists(file_path):
        print(f"[ERROR] 파일을 찾을 수 없습니다: {file_path}")
        sys.exit(1)

    if not file_path.lower().endswith('.xlsx'):
        print(f"[ERROR] .xlsx 파일만 지원합니다. (받은 파일: {file_path})")
        sys.exit(1)

    try:
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    except Exception as e:
        print(f"[ERROR] 파일을 열 수 없습니다: {e}")
        print("   파일이 다른 프로그램에서 열려 있지 않은지 확인하세요.")
        sys.exit(1)

    sheets = wb.sheetnames
    print(f"[시트 목록] 총 {len(sheets)}개")
    print(f"{'시트명':<25} {'행 수':>6} {'열 수':>6}")
    print("-" * 40)

    for name in sheets:
        ws = wb[name]
        rows = ws.max_row or 0
        cols = ws.max_column or 0
        # 빈 셀로만 된 행/열 제외한 실제 데이터 범위
        print(f"{name:<25} {rows:>6} {cols:>6}")

    wb.close()
    return sheets


def convert(file_path, sheet_name=None):
    """Excel 시트를 CSV로 변환"""
    openpyxl = check_openpyxl()

    if not os.path.exists(file_path):
        print(f"[ERROR] 파일을 찾을 수 없습니다: {file_path}")
        sys.exit(1)

    if not file_path.lower().endswith('.xlsx'):
        print(f"[ERROR] .xlsx 파일만 지원합니다. (받은 파일: {file_path})")
        sys.exit(1)

    try:
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    except Exception as e:
        print(f"[ERROR] 파일을 열 수 없습니다: {e}")
        print("   파일이 다른 프로그램에서 열려 있지 않은지 확인하세요.")
        sys.exit(1)

    # 변환할 시트 결정
    if sheet_name:
        if sheet_name not in wb.sheetnames:
            print(f"[ERROR] 시트를 찾을 수 없습니다: '{sheet_name}'")
            print(f"   사용 가능한 시트: {', '.join(wb.sheetnames)}")
            sys.exit(1)
        target_sheets = [sheet_name]
    else:
        target_sheets = wb.sheetnames

    # 출력 디렉토리 (원본 파일과 같은 폴더)
    out_dir = os.path.dirname(os.path.abspath(file_path))
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    multi_sheet = len(target_sheets) > 1

    saved_files = []

    for name in target_sheets:
        ws = wb[name]

        # 출력 파일명 결정
        if multi_sheet:
            out_filename = f"{base_name}_{safe_filename(name)}.csv"
        else:
            out_filename = f"{base_name}.csv"

        out_path = os.path.join(out_dir, out_filename)

        # CSV 저장 (utf-8-sig: BOM 포함 → Excel 한글 호환)
        try:
            with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                for row in ws.iter_rows(values_only=True):
                    # None 값을 빈 문자열로 변환
                    writer.writerow(['' if v is None else v for v in row])
        except PermissionError:
            print(f"[ERROR] 파일을 저장할 수 없습니다: {out_path}")
            print("   대상 CSV 파일이 다른 프로그램에서 열려 있는지 확인하세요.")
            sys.exit(1)

        saved_files.append(out_path)
        print(f"  [OK] {out_filename}")

    wb.close()

    print(f"\n[완료] {len(saved_files)}개 파일 변환됨")
    print(f"[저장위치] {out_dir}")

    return saved_files


def main():
    parser = argparse.ArgumentParser(
        description='Excel(.xlsx) 파일을 CSV로 변환합니다'
    )
    subparsers = parser.add_subparsers(dest='command')

    # list-sheets 커맨드
    ls_parser = subparsers.add_parser('list-sheets', help='시트 목록 조회')
    ls_parser.add_argument('--file', required=True, help='.xlsx 파일 경로')

    # convert 커맨드
    cv_parser = subparsers.add_parser('convert', help='CSV로 변환')
    cv_parser.add_argument('--file', required=True, help='.xlsx 파일 경로')
    cv_parser.add_argument('--sheet', help='특정 시트명 (생략 시 전체 시트)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'list-sheets':
        list_sheets(args.file)
    elif args.command == 'convert':
        convert(args.file, args.sheet)


if __name__ == '__main__':
    main()
