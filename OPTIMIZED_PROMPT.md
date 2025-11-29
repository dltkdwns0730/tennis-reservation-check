# 🏗️ Modularization Plan for Collaboration

## 🎯 Objective

- 단일 스크립트(`check_weekly.py`, `weekly_monitor.py`) 형태의 코드를 **유지보수와 협업이 용이한 패키지 구조**로 리팩토링합니다.
- 기능은 유지하되, 코드의 책임(Responsibility)을 명확히 분리합니다.

## 📂 Proposed Structure

```text
tennis_reservation_checker/
├── src/
│   ├── __init__.py
│   ├── config.py       # 환경 변수, 상수 (Settings)
│   ├── crawler.py      # Selenium 크롤링 로직 (WeeklyReservationChecker)
│   ├── notifier.py     # 텔레그램 알림 (TelegramBot)
│   └── utils.py        # 헬퍼 함수 (날짜 파싱, 메시지 포맷팅)
├── main.py             # 프로그램 진입점 (Entry Point)
├── requirements.txt    # 의존성 목록
└── README.md           # 프로젝트 설명서
```

## 📝 Implementation Details

### 1. `src/config.py`

- `dotenv` 로딩.
- `COURT_NAMES`, `TELEGRAM_SETTINGS` 등 상수 정의.

### 2. `src/crawler.py`

- `check_weekly.py`의 `WeeklyReservationChecker` 클래스 이동.
- `print` 문 대신 `logging` 사용 권장 (또는 콜백 구조).

### 3. `src/notifier.py`

- `send_telegram` 함수를 클래스화 (`TelegramNotifier`)하거나 모듈 함수로 정리.

### 4. `src/utils.py`

- `format_matrix_summary`, `parse_court_ids` 등 순수 로직 이동.

### 5. `main.py`

- `argparse` 로직 구현 (CLI 지원 복구).
- `Crawler`와 `Notifier`를 조립하여 실행.

## 🚀 Action Plan

1. Create `src` directory.
2. Split `check_weekly.py` & `weekly_monitor.py` into `src/`.
3. Create `main.py` with CLI support.
4. Generate `requirements.txt`.
