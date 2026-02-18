"""Intent: 코트 선택 및 요약 포맷팅을 위한 헬퍼 유틸리티를 제공합니다.
Used by: 코트 입력을 파싱하고 알림 텍스트를 생성하는 CLI 워크플로우.
Flow: 코트 식별자를 정규화하고 주간 가용성을 간결한 야간 매트릭스로 렌더링."""

from .config import COURT_NAME_MAP


def parse_court_ids(input_str):
    """Caller: main.py의 CLI 인수 처리에서 호출됨.
    Purpose: 사용자 제공 코트 이름 또는 ID를 정규화된 숫자 코트 ID로 변환.
    Returns: 고유하고 정렬된 코트 ID 목록.
    Deps: 유효한 ID 범위 컨텍스트를 위한 src.config.COURT_NAME_MAP.
    Args: input_str: 쉼표로 구분된 문자열 또는 CLI 토큰 목록.
    Note: 동의어 매칭을 지원하며 알 수 없는 값은 무시함."""
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



