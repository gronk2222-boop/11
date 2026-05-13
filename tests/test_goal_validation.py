import pytest
from services.validators import validate_goal

@pytest.mark.parametrize("goal, valid", [
    ("Заработать 5000 рублей", False),
    ("Доход 10к", False),
    ("Прибыль 1000р", False),
    ("Сделать 2 звонка", True),
    ("Посетить объект", True),
    ("Выставить счёт", True),
])
def test_validate_goal(goal, valid):
    assert validate_goal(goal) == valid
