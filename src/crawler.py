"""Intent: Crawl court reservation pages and collect daily availability snapshots.
Used by: main.py workflow that checks weekly reservations for selected courts.
Flow: Start a headless browser, navigate per date, parse reservation tables, and return structured weekly data."""

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


class WeeklyReservationChecker:
    """Purpose: Fetch weekly reservation availability for a single tennis court target.
    Context: Instantiated per court ID by CLI orchestration in main.py.
    Attrs: home_url: reservation site URL; court_id: target court identifier; days: number of days to inspect; court_names: ID-to-name map; driver: Selenium driver instance; weekly_data: accumulated crawl results."""

    def __init__(self, court_id=3, days=7):
        """Caller: Called when creating a checker instance in the monitoring loop.
        Purpose: Initialize crawl target settings and runtime state containers.
        Returns: None.
        Deps: src.config.HOME_URL and src.config.COURT_NAME_MAP.
        Args: court_id: target court number; days: number of days to inspect.
        Note: weekly_data starts empty and is populated by check_weekly."""
        self.home_url = HOME_URL
        self.court_id = court_id
        self.days = days
        self.court_names = COURT_NAME_MAP
        self.driver = None
        self.weekly_data = []

    def setup_driver(self):
        """Caller: Called internally before any page navigation.
        Purpose: Configure and launch a headless Chrome WebDriver instance.
        Returns: None.
        Deps: selenium.webdriver; webdriver_manager.chrome.
        Args: None.
        Note: Uses low-noise headless options for unattended execution."""
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
        """Caller: Invoked by check_weekly after driver setup.
        Purpose: Open the home page and click through to the configured court page.
        Returns: bool indicating whether court page navigation succeeded.
        Deps: Selenium WebDriver DOM queries and script execution.
        Args: None.
        Note: Matches both visible link text and expected daily-path pattern for safety."""
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
        """Caller: Called for each day offset in check_weekly.
        Purpose: Move the browser to a specific court/date page and verify page data alignment.
        Returns: bool indicating whether the target date page loaded correctly.
        Deps: Selenium WebDriver DOM queries and script execution.
        Args: target_date: datetime value representing the date to inspect.
        Note: Confirms date by inspecting table input metadata after navigation."""
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
        """Caller: Called after successful date navigation for data extraction.
        Purpose: Parse time slots and per-court availability from the current page.
        Returns: dict of parsed reservation data or None on extraction failure.
        Deps: Selenium WebDriver table parsing helpers; analyze_cell; determine_status.
        Args: None.
        Note: Builds per-court slot metadata and a derived list of available times."""
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
                    cell_info = self.analyze_cell(cell)
                    status, reason = self.determine_status(cell_info)

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

    def analyze_cell(self, cell):
        """Caller: Called by extract_reservation_data for each reservation cell.
        Purpose: Inspect checkbox/icon state to collect raw occupancy indicators.
        Returns: dict containing checkbox/icon visibility and content flags.
        Deps: Selenium WebElement APIs.
        Args: cell: table cell WebElement containing reservation controls.
        Note: Uses tolerant parsing to handle minor DOM differences without aborting extraction."""
        info = {
            "checkbox_exists": False,
            "checkbox_disabled": False,
            "checkbox_title": "",
            "icon_visible": False,
            "icon_text": "",
            "has_content": False,
        }
        try:
            try:
                checkbox = cell.find_element(By.TAG_NAME, "input")
                info["checkbox_exists"] = True
                info["checkbox_disabled"] = not checkbox.is_enabled()
                info["checkbox_title"] = checkbox.get_attribute("title") or ""
            except:
                pass
            try:
                icons = cell.find_elements(By.TAG_NAME, "i")
                for icon in icons:
                    if icon.is_displayed():
                        info["icon_visible"] = True
                        icon_text = icon.text.strip()
                        if icon_text:
                            info["icon_text"] += icon_text + " "
                        if icon.get_attribute("innerHTML").strip():
                            info["has_content"] = True
            except:
                pass
        except:
            pass
        return info

    def determine_status(self, cell_info):
        """Caller: Used by extract_reservation_data after analyze_cell.
        Purpose: Translate raw cell indicators into business-level reservation status.
        Returns: tuple of (status, reason) strings.
        Deps: None.
        Args: cell_info: parsed cell indicator dictionary from analyze_cell.
        Note: Prioritizes explicit unavailable/reserved markers before availability inference."""
        if cell_info["checkbox_title"] == "예약불가":
            return "unavailable", "예약불가"
        if cell_info["icon_visible"] or cell_info["has_content"]:
            reason = cell_info["icon_text"].strip() if cell_info["icon_text"] else ""
            return "reserved", reason
        if cell_info["checkbox_exists"] and not cell_info["checkbox_disabled"]:
            if not cell_info["icon_visible"] and not cell_info["has_content"]:
                return "available", ""
        if cell_info["checkbox_disabled"]:
            return "unavailable", cell_info["checkbox_title"]
        return "unknown", ""

    def check_weekly(self):
        """Caller: Triggered from main monitoring loop per target court.
        Purpose: Execute end-to-end weekly crawl and return per-day reservation data.
        Returns: list of day-level reservation dictionaries or None on fatal failure.
        Deps: Selenium driver lifecycle; navigate_to_court; navigate_to_date; extract_reservation_data.
        Args: None.
        Note: Always attempts to close the browser driver in the finally block."""
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
