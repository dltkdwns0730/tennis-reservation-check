"""Intent: 예약 데이터를 사람이 읽을 수 있는 문자열로 포맷팅합니다.
Used by: main.py에서 텔레그램 메시지 생성 시 사용.
Flow: 야간 시간대 데이터를 필터링하고 간결한 텍스트 요약으로 포맷팅."""


def format_matrix_summary(all_results):
    """Caller: 크롤링 완료 후 알림 출력을 준비하기 위해 호출됨.
    Purpose: 야간 예약 가용성에 대한 날짜별 코트 요약을 간결하게 생성.
    Returns: 포맷팅된 요약 텍스트 문자열.
    Deps: None.
    Args: all_results: 코트 이름과 수집된 주간 예약 데이터의 매핑.
    Note: 19:00 이후 시간대로 필터링하며 야간 슬롯이 없는 날짜는 생략함."""
    lines = []
    lines.append("야간(19시~) 예약 현황")

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

                day_lines.append(f" {short_name}: {', '.join(slots_list)}")

        if has_evening_in_day:
            has_any_data = True
            lines.append(f"\n{date_str}")
            lines.extend(day_lines)

    if not has_any_data:
        lines.append("\n(예약 가능한 야간 시간대 없음)")

    return "\n".join(lines)
