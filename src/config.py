"""Intent: 예약 모니터링을 위한 환경 변수 기반 구성을 정의합니다.
Used by: 공통 상수를 임포트하는 CLI, 크롤러, 알림, 유틸리티 모듈.
Flow: .env 변수 로드, 기본값 도출, 상수 설정 노출."""

import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

DEFAULT_TARGET_COURTS = os.getenv("TARGET_COURTS", "3,5")
DEFAULT_CHECK_DAYS = int(os.getenv("CHECK_DAYS", "7"))

COURT_NAME_MAP = {
    1: "안양시청",
    2: "안양종합운동장",
    3: "자유공원",
    4: "중앙공원",
    5: "호계공원",
}

HOME_URL = "https://www.aytennis.or.kr/"
