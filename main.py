#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tennis Reservation Checker Entry Point
"""
import sys
import argparse
from src.config import DEFAULT_TARGET_COURTS, DEFAULT_CHECK_DAYS, COURT_NAME_MAP
from src.utils import parse_court_ids, format_matrix_summary
from src.crawler import WeeklyReservationChecker
from src.notifier import send_telegram_message

# Windows Encoding Fix
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description="Tennis Court Reservation Monitor")
    parser.add_argument("courts", nargs="*", help="Target court names (e.g., 자유 호계)")
    parser.add_argument("--days", type=int, default=DEFAULT_CHECK_DAYS, help="Days to check")
    args = parser.parse_args()

    # 1. Determine Target Courts
    if args.courts:
        print(f"📥 CLI 입력 감지: {args.courts}")
        target_court_ids = parse_court_ids(args.courts)
    else:
        print(f"⚙️ 기본 설정 사용: {DEFAULT_TARGET_COURTS}")
        target_court_ids = parse_court_ids(DEFAULT_TARGET_COURTS)

    if not target_court_ids:
        print("❌ 조회할 코트가 없습니다.")
        return

    print(f"🔍 모니터링 시작 (대상 ID: {target_court_ids}, 기간: {args.days}일)")

    # 2. Run Crawler
    all_results = {}
    for cid in target_court_ids:
        c_name = COURT_NAME_MAP.get(cid, "Unknown")
        print(f"🚀 [{c_name}] 조회 중...", end="", flush=True)
        
        checker = WeeklyReservationChecker(court_id=cid, days=args.days)
        result = checker.check_weekly()
        
        if result:
            all_results[c_name] = result
            print(f"\r✅ [{c_name}] 조회 완료      ")
        else:
            print(f"\r❌ [{c_name}] 조회 실패      ")

    # 3. Process Results
    if all_results:
        summary_text = format_matrix_summary(all_results)
        print("\n" + summary_text)
        
        # 4. Send Notification
        print(f"🚀 텔레그램 전송 중...")
        if send_telegram_message(summary_text):
            print("✅ 전송 완료")
        else:
            print("ℹ 전송 실패 또는 설정 없음")
    else:
        print("\n❌ 조회된 데이터가 없습니다.")

if __name__ == "__main__":
    main()
