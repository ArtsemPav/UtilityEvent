"""
Модуль валидации данных перед сохранением.
Каждая функция возвращает список строк с ошибками (пустой список – валидация пройдена).
"""

import re
from typing import List, Optional, Union
from models.minbet import FixedMinBet, VariableMinBet
from models.goals import Goal
from models.rewards import Reward

def validate_event_id(event_id: str) -> List[str]:
    errors = []
    if not event_id or not event_id.strip():
        errors.append("EventID не может быть пустым")
    elif not re.match(r'^[A-Za-z0-9_\-]+$', event_id):
        errors.append("EventID может содержать только латинские буквы, цифры, '_' и '-'")
    return errors

def validate_node_id(node_id: int, existing_ids: Optional[List[int]] = None) -> List[str]:
    errors = []
    if node_id <= 0:
        errors.append("NodeID должен быть положительным числом")
    if existing_ids and node_id in existing_ids:
        errors.append(f"NodeID {node_id} уже используется")
    return errors

def validate_game_list(game_list: List[str]) -> List[str]:
    errors = []
    if not game_list:
        errors.append("GameList не может быть пустым")
    for game in game_list:
        if not game or not game.strip():
            errors.append("Имена игр не могут быть пустыми")
    return errors

def validate_min_bet(min_bet: Union[FixedMinBet, VariableMinBet]) -> List[str]:
    errors = []
    if isinstance(min_bet, FixedMinBet):
        if min_bet.amount < 0:
            errors.append("MinBet не может быть отрицательным")
    elif isinstance(min_bet, VariableMinBet):
        if min_bet.variable <= 0:
            errors.append("Variable должен быть > 0")
        if min_bet.min < 0:
            errors.append("Min не может быть отрицательным")
        if min_bet.max < min_bet.min:
            errors.append("Max не может быть меньше Min")
    else:
        errors.append("Неизвестный тип MinBet")
    return errors

def validate_goal(goal: Goal) -> List[str]:
    errors = []
    if not goal.type:
        errors.append("Goal.Type не может быть пустым")
    # Дополнительные проверки для конкретных типов можно добавить здесь
    return errors

def validate_rewards(rewards: List[Reward]) -> List[str]:
    errors = []
    if not rewards:
        errors.append("Список наград не может быть пустым")
    for i, reward in enumerate(rewards):
        data = reward.data
        if hasattr(data, 'amount') and data.amount <= 0:
            errors.append(f"Награда #{i+1}: Amount должен быть > 0")
        # другие проверки...
    return errors

def validate_segment_name(segment_name: str) -> List[str]:
    errors = []
    if not segment_name or not segment_name.strip():
        errors.append("Имя сегмента не может быть пустым")
    elif not re.match(r'^[A-Za-z0-9_\-]+$', segment_name):
        errors.append("Имя сегмента может содержать только латинские буквы, цифры, '_' и '-'")
    return errors

def validate_vip_range(vip_range: str) -> List[str]:
    errors = []
    if not vip_range:
        errors.append("VIP Range не может быть пустым")
    # Простая проверка формата "число-число+" или "число-число"
    pattern = r'^\d+-\d+\+?$'
    if not re.match(pattern, vip_range):
        errors.append("VIP Range должен быть в формате '1-10' или '1-10+'")
    return errors