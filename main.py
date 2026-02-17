#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Intent: Provide the CLI entry point for tennis reservation monitoring.
Used by: Operators and schedulers executing this script directly.
Flow: Parse CLI options, resolve target courts, crawl weekly data, summarize results, and send Telegram alerts."""

import argparse
import sys

from src.config import COURT_NAME_MAP, DEFAULT_CHECK_DAYS, DEFAULT_TARGET_COURTS
from src.crawler import WeeklyReservationChecker
from src.notifier import send_telegram_message
from src.utils import format_matrix_summary, parse_court_ids

# Keep UTF-8 output on Windows consoles that default to legacy encodings.
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    """Caller: Invoked when this module runs as a script.
    Purpose: Execute reservation checks for selected courts and notify summarized results.
    Returns: None.
    Deps: argparse; src.config; src.crawler; src.utils; src.notifier.
    Args: None.
    Note: Uses configured default courts when no CLI court list is provided."""
    parser = argparse.ArgumentParser(description="Tennis Court Reservation Monitor")
    parser.add_argument("courts", nargs="*", help="Target court names (e.g., 자유 호계)")
    parser.add_argument("--days", type=int, default=DEFAULT_CHECK_DAYS, help="Days to check")
    args = parser.parse_args()

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

    if all_results:
        summary_text = format_matrix_summary(all_results)
        print("\n" + summary_text)

        print("🚀 텔레그램 전송 중...")
        if send_telegram_message(summary_text):
            print("✅ 전송 완료")
        else:
            print("ℹ 전송 실패 또는 설정 없음")
    else:
        print("\n❌ 조회된 데이터가 없습니다.")


if __name__ == "__main__":
    main()
