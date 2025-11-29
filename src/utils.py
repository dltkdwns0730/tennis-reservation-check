from .config import COURT_NAME_MAP

def parse_court_ids(input_str):
    """
    쉼표로 구분된 코트 이름/번호 문자열을 파싱하여 ID 리스트 반환
    예: "자유, 5" -> [3, 5]
    """
    if not input_str:
        return []

    target_ids = []
    # 리스트가 들어올 경우 처리 (argparse nargs='*')
    if isinstance(input_str, list):
        inputs = []
        for item in input_str:
            inputs.extend(item.replace(',', ' ').split())
    else:
        inputs = [x.strip() for x in input_str.split(',')]
    
    # 매핑 테이블 확장 (유의어)
    extended_map = {
        "시청": 1, "안양시청": 1,
        "종합": 2, "운동장": 2, "안양종합운동장": 2,
        "자유": 3, "자유공원": 3,
        "중앙": 4, "중앙공원": 4,
        "호계": 5, "호계공원": 5
    }
    
    for item in inputs:
        item = str(item).strip()
        # 번호 입력 시
        if item.isdigit():
            cid = int(item)
            if 1 <= cid <= 5:
                target_ids.append(cid)
        # 이름 입력 시
        else:
            for key, val in extended_map.items():
                if key in item:
                    target_ids.append(val)
                    break
    
    # 중복 제거 및 정렬
    return sorted(list(set(target_ids)))

def format_matrix_summary(all_results):
    """
    여러 코트의 예약 결과를 날짜별 매트릭스 형태의 문자열로 반환 (19시 이후만)
    all_results: { '코트이름': weekly_data_list, ... }
    """
    lines = []
    lines.append(f"{'='*30}")
    lines.append(f"🌙 통합 야간(19시~) 예약 현황")
    lines.append(f"{'='*30}")

    # 1. 날짜별로 데이터 재구성
    dates_map = {}
    
    for court_name, weekly_data in all_results.items():
        if not weekly_data:
            continue
            
        for day_data in weekly_data:
            date_key = f"{day_data['date']} ({day_data['day_of_week'][:3]})"
            
            if date_key not in dates_map:
                dates_map[date_key] = {}
            
            if court_name not in dates_map[date_key]:
                dates_map[date_key][court_name] = []
                
            # 야간 시간대 필터링
            for c_num, c_data in day_data['courts'].items():
                evening_times = []
                for time_slot in c_data['available_times']:
                    try:
                        start_h = int(time_slot.split(':')[0])
                        if start_h >= 19:
                            simple_time = time_slot.split('~')[0].strip()
                            evening_times.append(simple_time)
                    except:
                        pass
                
                if evening_times:
                    dates_map[date_key][court_name].append(f"{c_num} | {', '.join(evening_times)}")

    # 2. 문자열 생성
    sorted_dates = sorted(dates_map.keys())
    
    for date_str in sorted_dates:
        lines.append(f"\n📅 {date_str}")
        lines.append("-" * 30)
        
        has_data_in_date = False
        
        for court_name, slots_list in dates_map[date_str].items():
            if slots_list:
                has_data_in_date = True
                lines.append(f"[{court_name}]")
                for slot_str in slots_list:
                    lines.append(f"  └ {slot_str}")
        
        if not has_data_in_date:
            lines.append("  (예약 가능한 야간 시간대 없음)")
            
    return "\n".join(lines)
