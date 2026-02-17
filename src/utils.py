"""Intent: Provide helper utilities for court selection and summary formatting.
Used by: CLI workflow that parses court inputs and builds notification text.
Flow: Normalize court identifiers and render weekly availability into a compact evening matrix."""

from .config import COURT_NAME_MAP


def parse_court_ids(input_str):
    """Caller: Called by CLI argument handling in main.py.
    Purpose: Convert user-provided court names or IDs into normalized numeric court IDs.
    Returns: list of unique sorted court IDs.
    Deps: src.config.COURT_NAME_MAP for valid ID range context.
    Args: input_str: comma-separated string or list of CLI tokens.
    Note: Supports synonym matching and ignores unknown values."""
    if not input_str:
        return []

    target_ids = []
    if isinstance(input_str, list):
        inputs = []
        for item in input_str:
            inputs.extend(item.replace(",", " ").split())
    else:
        inputs = [x.strip() for x in input_str.split(",")]

    extended_map = {
        "시청": 1,
        "안양시청": 1,
        "종합": 2,
        "운동장": 2,
        "안양종합운동장": 2,
        "자유": 3,
        "자유공원": 3,
        "중앙": 4,
        "중앙공원": 4,
        "호계": 5,
        "호계공원": 5,
    }

    for item in inputs:
        item = str(item).strip()
        if item.isdigit():
            cid = int(item)
            if 1 <= cid <= 5:
                target_ids.append(cid)
        else:
            for key, val in extended_map.items():
                if key in item:
                    target_ids.append(val)
                    break

    return sorted(list(set(target_ids)))


def format_matrix_summary(all_results):
    """Caller: Called after crawling completes to prepare notification output.
    Purpose: Build a compact date-by-court summary of evening reservation availability.
    Returns: str formatted summary text.
    Deps: None.
    Args: all_results: mapping of court name to collected weekly reservation data.
    Note: Filters to times starting at 19:00 or later and omits days with no evening slots."""
    lines = []
    lines.append("🌙 야간(19시~) 예약 현황")

    dates_map = {}

    for court_name, weekly_data in all_results.items():
        if not weekly_data:
            continue

        for day_data in weekly_data:
            date_obj = day_data["date"]
            try:
                short_date = date_obj[5:].replace("-", "/")
            except:
                short_date = date_obj

            date_key = f"{short_date} ({day_data['day_of_week'][:3]})"

            if date_key not in dates_map:
                dates_map[date_key] = {}

            if court_name not in dates_map[date_key]:
                dates_map[date_key][court_name] = []

            for c_num, c_data in day_data["courts"].items():
                evening_times = []
                for time_slot in c_data["available_times"]:
                    try:
                        start_h = int(time_slot.split(":")[0])
                        if start_h >= 19:
                            simple_time = time_slot.split(":")[0].strip()
                            evening_times.append(simple_time)
                    except:
                        pass

                if evening_times:
                    simple_num = c_num.replace("코트", "").strip() + "번"
                    dates_map[date_key][court_name].append(f"{simple_num}({','.join(evening_times)})")

    sorted_dates = sorted(dates_map.keys())
    has_any_data = False

    for date_str in sorted_dates:
        day_lines = []
        has_evening_in_day = False

        for court_name, slots_list in dates_map[date_str].items():
            if slots_list:
                has_evening_in_day = True
                short_name = court_name.replace("안양", "").replace("공원", "").replace("테니스장", "").strip()
                if short_name == "종합운동장":
                    short_name = "종합"

                day_lines.append(f" 🏟️ {short_name}: {', '.join(slots_list)}")

        if has_evening_in_day:
            has_any_data = True
            lines.append(f"\n📅 {date_str}")
            lines.extend(day_lines)

    if not has_any_data:
        lines.append("\n(예약 가능한 야간 시간대 없음 😭)")

    return "\n".join(lines)
