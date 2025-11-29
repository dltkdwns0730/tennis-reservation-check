import requests
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(message, token=None, chat_id=None):
    """
    텔레그램 메시지 전송
    """
    # 인자가 없으면 config 값 사용
    token = token or TELEGRAM_BOT_TOKEN
    chat_id = chat_id or TELEGRAM_CHAT_ID

    if not token or not chat_id:
        print("⚠ 텔레그램 설정이 없습니다. (메시지 전송 건너뜀)")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    # 다중 사용자 지원 (콤마로 구분된 경우)
    chat_ids = [cid.strip() for cid in str(chat_id).split(',') if cid.strip()]
    
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
