"""Intent: 텔레그램 봇 API를 통해 예약 요약을 전송합니다.
Used by: 예약 결과 포맷팅 후 CLI 진입점.
Flow: 토큰/채팅 ID 해결, 수신자별 메시지 전송, 전송 상태 보고."""

import requests

from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_telegram_message(message, token=None, chat_id=None):
    """Caller: 요약 생성 후 알림 흐름에서 호출됨.
    Purpose: 하나 이상의 텔레그램 채팅 수신자에게 메시지 전달.
    Returns: 최소 한 번의 전송 성공 여부를 나타내는 불리언 값.
    Deps: requests; Telegram Bot API; src.config 기본값.
    Args: message: 전송할 메시지 본문; token: 봇 토큰 재정의; chat_id: 채팅 ID 목록 재정의.
    Note: 쉼표로 구분된 채팅 ID를 허용하며 각각 동일한 페이로드를 전송함."""
    token = token or TELEGRAM_BOT_TOKEN
    chat_id = chat_id or TELEGRAM_CHAT_ID

    if not token or not chat_id:
        print("텔레그램 설정이 없습니다. (메시지 전송 건너뜀)")
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
                print(f"텔레그램 전송 성공 (To: {cid})")
                success_count += 1
            else:
                print(f"텔레그램 전송 실패 (To: {cid}): {response.text}")
        except Exception as e:
            print(f"텔레그램 오류 (To: {cid}): {e}")

    return success_count > 0
