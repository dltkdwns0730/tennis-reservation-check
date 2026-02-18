# Tennis Reservation Checker

안양 도시공사 테니스장 예약 현황을 조회하고 텔레그램으로 알림을 보내주는 도구입니다.

## Features

- **자동 조회**: 7일간의 예약 현황을 크롤링합니다.
- **텔레그램 알림**: 조회 결과를 텔레그램으로 전송합니다.
- **다중 사용자 지원**: 여러 명에게 동시에 알림을 보낼 수 있습니다.
- **CLI 지원**: 명령줄 인자로 조회할 코트를 지정할 수 있습니다.

## Structure

- `src/`: 핵심 로직 (크롤러, 알림, 설정)
- `main.py`: 실행 진입점

## Setup

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

## Telegram Notification Setup

텔레그램 알림을 받으려면 봇 설정이 필요합니다.

### 1. 봇 생성 (BotFather)

1. 텔레그램에서 **`@BotFather`** 검색 후 선택.
2. 메세지로 `/newbot` 입력.
3. 봇의 이름(예: `Tennis Checker`)과 사용자명(예: `MyTennis_bot`, 반드시 `bot`으로 끝나야 함)을 순서대로 입력.
4. 발급된 **HTTP API Token**을 복사합니다. 이 값이 `TELEGRAM_BOT_TOKEN` 입니다.

### 2. Chat ID 확인 (UserInfoBot)

1. 텔레그램에서 **`@userinfobot`** 검색.
2. **Start** 버튼 클릭.
3. `Id` 숫자를 복사합니다. 이 값이 `TELEGRAM_CHAT_ID` 입니다.

### 3. 프로젝트 설정

1. 프로젝트 폴더의 `.env` 파일(없으면 `.env.example` 복사)을 엽니다.
2. 값을 입력합니다:

   ```ini
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
   TELEGRAM_CHAT_ID=12345678
   ```

### 4. 봇 활성화

1. 텔레그램에서 생성한 봇을 검색합니다.
2. **Start** 버튼을 눌러 대화를 시작합니다. (이 과정을 거쳐야 봇이 메세지를 보낼 수 있습니다)

## Usage

### 기본 실행 (설정 파일 기준)

```bash
python main.py
```

### 특정 코트 조회

```bash
python main.py 자유 호계
```
