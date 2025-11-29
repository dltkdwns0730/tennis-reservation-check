import sys
import io
import time
import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from .config import HOME_URL, COURT_NAME_MAP

class WeeklyReservationChecker:
    def __init__(self, court_id=3, days=7):
        """
        Args:
            court_id (int): 코트 번호
            days (int): 조회할 일수 (기본 7일)
        """
        self.home_url = HOME_URL
        self.court_id = court_id
        self.days = days
        self.court_names = COURT_NAME_MAP
        self.driver = None
        self.weekly_data = []

    def setup_driver(self):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1920,1080')
        # 로그 레벨 조정
        chrome_options.add_argument('--log-level=3')

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def navigate_to_court(self):
        """코트 페이지로 이동"""
        try:
            court_name = self.court_names.get(self.court_id, "자유공원 테니스코트")
            # print(f"홈페이지 접속: {self.home_url}")
            self.driver.get(self.home_url)
            time.sleep(3)

            # print(f"{court_name} 페이지로 이동 중...")
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
        """URL을 통해 특정 날짜로 이동"""
        try:
            date_str = target_date.strftime('%Y-%m-%d')
            # print(f"  {date_str} 페이지로 이동 중...")
            url = f"/daily/{self.court_id}/{date_str}"
            self.driver.execute_script(f"window.location.href = '{url}';")
            time.sleep(5) # 대기 시간 조정

            # 데이터 로딩 확인
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
        """현재 페이지의 예약 현황 추출"""
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
                if not rows: continue

                court_name = rows[0].text.strip()
                slots_info = []
                available_times = []

                for time_idx, row in enumerate(rows[1:], 0):
                    if time_idx >= len(time_slots): break
                    time_slot = time_slots[time_idx]
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if not cells: continue

                    cell = cells[0]
                    cell_info = self.analyze_cell(cell)
                    status, reason = self.determine_status(cell_info)

                    slots_info.append({'time': time_slot, 'status': status, 'reason': reason})
                    if status == 'available':
                        available_times.append(time_slot)

                courts_data[court_name] = {
                    'slots': slots_info,
                    'available_count': len(available_times),
                    'available_times': available_times
                }
            return courts_data
        except Exception as e:
            print(f"  데이터 추출 오류: {e}")
            return None

    def analyze_cell(self, cell):
        info = {'checkbox_exists': False, 'checkbox_disabled': False, 'checkbox_title': '', 'icon_visible': False, 'icon_text': '', 'has_content': False}
        try:
            try:
                checkbox = cell.find_element(By.TAG_NAME, "input")
                info['checkbox_exists'] = True
                info['checkbox_disabled'] = not checkbox.is_enabled()
                info['checkbox_title'] = checkbox.get_attribute("title") or ""
            except: pass
            try:
                icons = cell.find_elements(By.TAG_NAME, "i")
                for icon in icons:
                    if icon.is_displayed():
                        info['icon_visible'] = True
                        icon_text = icon.text.strip()
                        if icon_text: info['icon_text'] += icon_text + " "
                        if icon.get_attribute("innerHTML").strip(): info['has_content'] = True
            except: pass
        except: pass
        return info

    def determine_status(self, cell_info):
        if cell_info['checkbox_title'] == "예약불가": return "unavailable", "예약불가"
        if cell_info['icon_visible'] or cell_info['has_content']:
            reason = cell_info['icon_text'].strip() if cell_info['icon_text'] else ""
            return "reserved", reason
        if cell_info['checkbox_exists'] and not cell_info['checkbox_disabled']:
            if not cell_info['icon_visible'] and not cell_info['has_content']: return "available", ""
        if cell_info['checkbox_disabled']: return "unavailable", cell_info['checkbox_title']
        return "unknown", ""

    def check_weekly(self):
        """7일간 예약 현황 조회"""
        try:
            self.setup_driver()
            # court_name = self.court_names.get(self.court_id, "Unknown")
            
            if not self.navigate_to_court():
                print("코트 페이지 초기 접속 실패")
                return None

            today = datetime.now()
            for day_offset in range(self.days):
                target_date = today + timedelta(days=day_offset)
                # print(f"[{day_offset + 1}/{self.days}] {target_date.strftime('%Y-%m-%d')} 조회 중...", end='\r')
                
                if not self.navigate_to_date(target_date):
                    continue

                courts_data = self.extract_reservation_data()
                if courts_data:
                    day_data = {
                        'date': target_date.strftime('%Y-%m-%d'),
                        'day_of_week': target_date.strftime('%A'),
                        'day_offset': day_offset,
                        'courts': courts_data
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
