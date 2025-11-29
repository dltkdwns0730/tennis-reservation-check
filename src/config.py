import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Court Settings
DEFAULT_TARGET_COURTS = os.getenv("TARGET_COURTS", "3,5")  # Default: 자유, 호계
DEFAULT_CHECK_DAYS = int(os.getenv("CHECK_DAYS", "7"))

# Court ID Mapping
COURT_NAME_MAP = {
    1: "안양시청",
    2: "안양종합운동장",
    3: "자유공원",
    4: "중앙공원",
    5: "호계공원"
}

# URL Settings
HOME_URL = "https://www.aytennis.or.kr/"
