"""Intent: 코트 예약 페이지를 크롤링하고 일일 가용성 스냅샷을 수집합니다.
Used by: 선택된 코트의 주간 예약을 확인하는 main.py 워크플로우.
Flow: 헤드리스 브라우저 시작, 날짜별 탐색, 예약 테이블 파싱, 구조화된 주간 데이터 반환."""

import io
import json
import sys
import time
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from .config import COURT_NAME_MAP, HOME_URL
from .parser import ReservationParser


class WeeklyReservationChecker:
    """Purpose: 단일 테니스 코트 타겟에 대한 주간 예약 가용성을 가져옴.
    Context: main.py의 CLI 오케스트레이션에 의해 코트 ID별로 인스턴스화됨.
    Attrs: home_url: 예약 사이트 URL; court_id: 타겟 코트 식별자; days: 검사할 일수; court_names: ID-이름 매핑; driver: Selenium 드라이버 인스턴스; weekly_data: 축적된 크롤링 결과."""

    def __init__(self, court_id=3, days=7):
        """Caller: 모니터링 루프에서 체커 인스턴스 생성 시 호출됨.
        Purpose: 크롤링 타겟 설정 및 런타임 상태 컨테이너 초기화.
        Returns: None.
        Deps: src.config.HOME_URL 및 src.config.COURT_NAME_MAP.
        Args: court_id: 타겟 코트 번호; days: 검사할 일수.
        Note: weekly_data는 비어있는 상태로 시작하며 check_weekly에 의해 채워짐."""
        self.home_url = HOME_URL
        self.court_id = court_id
        self.days = days
        self.court_names = COURT_NAME_MAP
        self.driver = None
        self.weekly_data = []

    def setup_driver(self):
        """Caller: 페이지 탐색 전 내부적으로 호출됨.
        Purpose: 헤드리스 Chrome WebDriver 인스턴스 구성 및 실행.
        Returns: None.
        Deps: selenium.webdriver; webdriver_manager.chrome.
        Args: None.
        Note: 무인 실행을 위해 노이즈가 적은 헤드리스 옵션 사용."""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--log-level=3")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def navigate_to_court(self):
        """Caller: 드라이버 설정 후 check_weekly에 의해 호출됨.
        Purpose: 홈 페이지를 열고 구성된 코트 페이지로 클릭하여 이동.
        Returns: 코트 페이지 탐색 성공 여부를 나타내는 불리언 값.
        Deps: Selenium WebDriver DOM 쿼리 및 스크립트 실행.
        Args: None.
        Note: 안전을 위해 보이는 링크 텍스트와 예상 일일 경로 패턴을 모두 일치시킴."""
        try:
            court_name = self.court_names.get(self.court_id, "자유공원 테니스코트")
            self.driver.get(self.home_url)
            time.sleep(3)

            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            for link in all_links:
                text = link.text.strip()
                href = link.get_attribute("href") or ""
                if court_name in text and f"/daily/{self.court_id}" in href:
                    if link.is_displayed():
                        self.driver.execute_script("arguments[0].click();", link)
                        time.sleep(5)
                        return True
            return False
        except Exception as e:
            print(f"페이지 이동 오류: {e}")
            return False

    def navigate_to_date(self, target_date):
        """Caller: check_weekly에서 각 날짜 오프셋마다 호출됨.
        Purpose: 브라우저를 특정 코트/날짜 페이지로 이동하고 페이지 데이터 정렬 확인.
        Returns: 타겟 날짜 페이지 로드 성공 여부를 나타내는 불리언 값.
        Deps: Selenium WebDriver DOM 쿼리 및 스크립트 실행.
        Args: target_date: 검사할 날짜를 나타내는 datetime 값.
        Note: 탐색 후 테이블 입력 메타데이터를 검사하여 날짜 확인."""
        try:
            date_str = target_date.strftime("%Y-%m-%d")
            url = f"/daily/{self.court_id}/{date_str}"
            self.driver.execute_script(f"window.location.href = '{url}';")
            time.sleep(5)

            try:
                tables = self.driver.find_elements(By.CSS_SELECTOR, "table.innerCustom.innerTop")
                if tables and len(tables) > 0:
                    rows = tables[0].find_elements(By.TAG_NAME, "tr")
                    if len(rows) > 1:
                        cells = rows[1].find_elements(By.TAG_NAME, "td")
                        if cells:
                            input_elem = cells[0].find_element(By.TAG_NAME, "input")
                            value = input_elem.get_attribute("value")
                            if value and "|" in value:
                                table_date = value.split("|")[0]
                                if table_date == date_str:
                                    return True
            except Exception:
                pass
            return False
        except Exception as e:
            print(f"  날짜 이동 오류: {e}")
            return False

    def extract_reservation_data(self):
        """Caller: 데이터 추출을 위해 성공적인 날짜 탐색 후 호출됨.
        Purpose: 현재 페이지에서 시간 슬롯 및 코트별 가용성 파싱.
        Returns: 파싱된 예약 데이터 딕셔너리 또는 추출 실패 시 None.
        Deps: Selenium WebDriver 테이블 파싱 헬퍼; analyze_cell; determine_status.
        Args: None.
        Note: 코트별 슬롯 메타데이터와 파생된 가용 시간 목록을 생성."""
        try:
            time.sleep(2)
            time_tables = self.driver.find_elements(By.CSS_SELECTOR, "table.custom")
            time_slots = []

            for table in time_tables:
                if "innerCustom" not in (table.get_attribute("class") or ""):
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    for row in rows[1:]:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if cells:
                            time_text = cells[0].text.strip()
                            if time_text and "~" in time_text:
                                time_slots.append(time_text)
                    break

            court_tables = self.driver.find_elements(By.CSS_SELECTOR, "table.innerCustom.innerTop")
            courts_data = {}

            for court_idx, court_table in enumerate(court_tables, 1):
                rows = court_table.find_elements(By.TAG_NAME, "tr")
                if not rows:
                    continue

                court_name = rows[0].text.strip()
                slots_info = []
                available_times = []

                for time_idx, row in enumerate(rows[1:], 0):
                    if time_idx >= len(time_slots):
                        break
                    time_slot = time_slots[time_idx]
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if not cells:
                        continue

                    cell = cells[0]
                    # Use extracted parser logic
                    cell_info = ReservationParser.analyze_cell(cell)
                    status, reason = ReservationParser.determine_status(cell_info)

                    slots_info.append({"time": time_slot, "status": status, "reason": reason})
                    if status == "available":
                        available_times.append(time_slot)

                courts_data[court_name] = {
                    "slots": slots_info,
                    "available_count": len(available_times),
                    "available_times": available_times,
                }
            return courts_data
        except Exception as e:
            print(f"  데이터 추출 오류: {e}")
            return None



    def check_weekly(self):
        """Caller: 타겟 코트별 메인 모니터링 루프에서 트리거됨.
        Purpose: 엔드투엔드 주간 크롤링 실행 및 일별 예약 데이터 반환.
        Returns: 일별 예약 딕셔너리 목록 또는 치명적 실패 시 None.
        Deps: Selenium 드라이버 라이프사이클; navigate_to_court; navigate_to_date; extract_reservation_data.
        Args: None.
        Note: finally 블록에서 브라우저 드라이버 종료를 항상 시도함."""
        try:
            self.setup_driver()

            if not self.navigate_to_court():
                print("코트 페이지 초기 접속 실패")
                return None

            today = datetime.now()
            for day_offset in range(self.days):
                target_date = today + timedelta(days=day_offset)

                if not self.navigate_to_date(target_date):
                    continue

                courts_data = self.extract_reservation_data()
                if courts_data:
                    day_data = {
                        "date": target_date.strftime("%Y-%m-%d"),
                        "day_of_week": target_date.strftime("%A"),
                        "day_offset": day_offset,
                        "courts": courts_data,
                    }
                    self.weekly_data.append(day_data)

                time.sleep(1)

            return self.weekly_data
        except Exception as e:
            print(f"오류 발생: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()
