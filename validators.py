import re

MONEY_PATTERNS = [
    r"заработать\s+\d+",
    r"\d+\s*(руб|р\.?|тыс\.?\s*руб|миллион)",
    r"доход",
    r"прибыль",
    r"выручка",
    r"заработать\s+денег",
]

def validate_goal(goal_text: str) -> bool:
    """Возвращает True, если цель не содержит денежных формулировок."""
    for pattern in MONEY_PATTERNS:
        if re.search(pattern, goal_text, re.IGNORECASE):
            return False
    return True
