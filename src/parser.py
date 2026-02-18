"""Intent: 예약 상태 확인을 위한 DOM 파싱 및 비즈니스 로직을 캡슐화합니다.
Used by: src.crawler.WeeklyReservationChecker.
Flow: Selenium WebElement(셀)을 수신하고, 자식 요소(체크박스, 아이콘)를 검사하여 예약 가능 여부를 판단합니다."""

from selenium.webdriver.common.by import By


class ReservationParser:
    """Purpose: 예약 테이블 셀을 파싱하여 슬롯 상태를 결정.
    Context: WeeklyReservationChecker를 위한 헬퍼 클래스.
    Attrs: None."""

    @staticmethod
    def analyze_cell(cell):
        """Caller: crawler.py의 extract_reservation_data에서 호출됨.
        Purpose: 체크박스/아이콘 상태를 검사하여 점유 표시를 수집.
        Returns: 체크박스/아이콘 가시성 및 내용 플래그를 포함하는 딕셔너리.
        Deps: Selenium WebElement API.
        Args: cell: 예약 컨트롤을 포함하는 테이블 셀 WebElement.
        Note: 추출 중단을 방지하기 위해 사소한 DOM 차이를 허용하는 파싱을 사용."""
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

    @staticmethod
    def determine_status(cell_info):
        """Caller: analyze_cell 이후 크롤러에서 사용됨.
        Purpose: 원시 셀 표시를 비즈니스 레벨의 예약 상태로 변환.
        Returns: (상태, 사유) 문자열의 튜플.
        Deps: None.
        Args: cell_info: analyze_cell에서 파싱된 셀 표시 딕셔너리.
        Note: 가용성 추론보다 명시적인 불가/예약 마커를 우선순위로 둠."""
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
