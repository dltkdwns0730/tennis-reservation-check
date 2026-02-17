"""Intent: Send reservation summaries through Telegram Bot API.
Used by: CLI entrypoint after formatting reservation results.
Flow: Resolve token/chat IDs, fan out message sends per recipient, and report send status."""

import requests

from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_telegram_message(message, token=None, chat_id=None):
    """Caller: Called from notification flow after summary generation.
    Purpose: Deliver a message to one or more Telegram chat recipients.
    Returns: bool indicating whether at least one send succeeded.
    Deps: requests; Telegram Bot API; src.config defaults.
    Args: message: message body to send; token: override bot token; chat_id: override chat ID list.
    Note: Accepts comma-separated chat IDs and sends the same payload to each."""
    token = token or TELEGRAM_BOT_TOKEN
    chat_id = chat_id or TELEGRAM_CHAT_ID

    if not token or not chat_id:
        print("⚠ 텔레그램 설정이 없습니다. (메시지 전송 건너뜀)")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    chat_ids = [cid.strip() for cid in str(chat_id).split(",") if cid.strip()]

    success_count = 0
    for cid in chat_ids:
        payload = {
            "chat_id": cid,
            "text": message,
        }

        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print(f"✅ 텔레그램 전송 성공 (To: {cid})")
                success_count += 1
            else:
                print(f"❌ 텔레그램 전송 실패 (To: {cid}): {response.text}")
        except Exception as e:
            print(f"❌ 텔레그램 오류 (To: {cid}): {e}")

    return success_count > 0
