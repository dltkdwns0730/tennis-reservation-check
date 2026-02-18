#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Intent: 테니스 예약 모니터링을 위한 CLI 진입점을 제공합니다.
Used by: 스크립트를 직접 실행하는 운영자 및 스케줄러.
Flow: CLI 옵션 파싱, 타겟 코트 해결, 주간 데이터 크롤링, 결과 요약, 텔레그램 알림 전송."""

import argparse
import sys

from src.config import COURT_NAME_MAP, DEFAULT_CHECK_DAYS, DEFAULT_TARGET_COURTS
from src.crawler import WeeklyReservationChecker
from src.formatter import format_matrix_summary
from src.notifier import send_telegram_message
from src.utils import parse_court_ids

# Keep UTF-8 output on Windows consoles that default to legacy encodings.
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    """Caller: 모듈이 스크립트로 실행될 때 호출됨.
    Purpose: 선택된 코트에 대한 예약 확인을 실행하고 요약 결과를 알림.
    Returns: None.
    Deps: argparse; src.config; src.crawler; src.formatter; src.notifier; src.utils.
    Args: None.
    Note: CLI 코트 목록이 제공되지 않은 경우 구성된 기본 코트를 사용함."""
    parser = argparse.ArgumentParser(description="Tennis Court Reservation Monitor")
    parser.add_argument("courts", nargs="*", help="Target court names (e.g., 자유 호계)")
    parser.add_argument("--days", type=int, default=DEFAULT_CHECK_DAYS, help="Days to check")
    args = parser.parse_args()

    if args.courts:
        print(f"CLI 입력 감지: {args.courts}")
        target_court_ids = parse_court_ids(args.courts)
    else:
        print(f"기본 설정 사용: {DEFAULT_TARGET_COURTS}")
        target_court_ids = parse_court_ids(DEFAULT_TARGET_COURTS)

    if not target_court_ids:
        print("조회할 코트가 없습니다.")
        return

    print(f"모니터링 시작 (대상 ID: {target_court_ids}, 기간: {args.days}일)")

    all_results = {}
    for cid in target_court_ids:
        c_name = COURT_NAME_MAP.get(cid, "Unknown")
        print(f"[{c_name}] 조회 중...", end="", flush=True)

        checker = WeeklyReservationChecker(court_id=cid, days=args.days)
        result = checker.check_weekly()

        if result:
            all_results[c_name] = result
            print(f"\r[{c_name}] 조회 완료      ")
        else:
            print(f"\r[{c_name}] 조회 실패      ")

    if all_results:
        summary_text = format_matrix_summary(all_results)
        print("\n" + summary_text)

        print("텔레그램 전송 중...")
        if send_telegram_message(summary_text):
            print("전송 완료")
        else:
            print("전송 실패 또는 설정 없음")
    else:
        print("\n조회된 데이터가 없습니다.")


if __name__ == "__main__":
    main()
