"""Intent: Define environment-backed configuration for reservation monitoring.
Used by: CLI, crawler, notifier, and utility modules that import shared constants.
Flow: Load .env variables, derive defaults, and expose constant settings."""

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
