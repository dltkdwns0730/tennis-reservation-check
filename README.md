# 🎾 Tennis Reservation Checker

안양 도시공사 테니스장 예약 현황을 조회하고 텔레그램으로 알림을 보내주는 도구입니다.

## 🚀 Features

- **자동 조회**: 7일간의 예약 현황을 크롤링합니다.
- **텔레그램 알림**: 조회 결과를 텔레그램으로 전송합니다.
- **다중 사용자 지원**: 여러 명에게 동시에 알림을 보낼 수 있습니다.
- **CLI 지원**: 명령줄 인자로 조회할 코트를 지정할 수 있습니다.

## 📂 Structure

- `src/`: 핵심 로직 (크롤러, 알림, 설정)
- `main.py`: 실행 진입점

## 🛠️ Setup

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**
   `.env.example`을 `.env`로 복사하고 설정을 입력하세요.

   ```ini
   TELEGRAM_BOT_TOKEN=...
   TELEGRAM_CHAT_ID=12345,67890
   TARGET_COURTS=3,5
   ```

## 🏃 Usage

**기본 실행 (설정 파일 기준)**

```bash
python main.py
```

**특정 코트 조회**

```bash
python main.py 자유 호계
```
