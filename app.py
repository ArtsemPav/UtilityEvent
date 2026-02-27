import json
from copy import deepcopy
import streamlit as st

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except Exception:
    HAS_JSONSCHEMA = False


def ensure_root(cfg: dict) -> dict:
    if not isinstance(cfg, dict):
        cfg = {}
    cfg.setdefault("Events", [])
    cfg.setdefault("IsFallbackConfig", False)
    if not isinstance(cfg["Events"], list):
        cfg["Events"] = []
    return cfg


def make_minbet_variable(variable: float, min_v: float, max_v: float) -> dict:
    return {"MinBetVariable": {"Variable": variable, "Min": min_v, "Max": max_v}}


def make_fixed_minbet(min_bet: float) -> dict:
    return {"FixedMinBet": {"MinBet": min_bet}}


def make_goal(goal_type: str, goal_params: dict) -> dict:
    """
    Создает цель с указанным типом и параметрами
    goal_type - строка типа "Item_BISON", "Spins" и т.д.
    goal_params - словарь с параметрами цели (SpinpadGoal, FixedGoal и т.д.)
    """
    return {
        "Type": [goal_type],
        **goal_params
    }


def make_spinpad_goal(multiplier: float, min_spins: float, max_spins: float) -> dict:
    """Создает SpinpadGoal параметры"""
    return {"SpinpadGoal": {"Multiplier": multiplier, "Min": min_spins, "Max": max_spins}}


def make_fixed_goal(target: int) -> dict:
    """Создает FixedGoal параметры"""
    return {"FixedGoal": {"Target": target}}


def make_consecutive_wins_goal(streaks: int, multiplier: float, min_val: int, max_val: int) -> dict:
    """Создает ConsecutiveWinsGoal параметры"""
    return {
        "ConsecutiveWinsGoal": {
            "NumberOfStreaksTarget": streaks,
            "WinsInStreakSpinPadGoal": {
                "Multiplier": multiplier,
                "Min": min_val,
                "Max": max_val
            }
        }
    }


def make_total_coins_per_day_goal(multiplier: float, min_val: int, max_val: int) -> dict:
    """Создает TotalCoinsPerDay параметры"""
    return {"TotalCoinsPerDay": {"Multiplier": multiplier, "Min": min_val, "Max": max_val}}


def make_total_coins_per_day_with_spin_limiter_goal(spin_limiter: int, multiplier: float, min_val: int, max_val: int) -> dict:
    """Создает TotalCoinsPerDayWithSpinLimiter параметры"""
    return {
        "TotalCoinsPerDayWithSpinLimiter": {
            "SpinLimiter": spin_limiter,
            "Multiplier": multiplier,
            "Min": min_val,
            "Max": max_val
        }
    }


def make_fixed_goal_with_spin_limiter_goal(target: int, spin_limiter: int) -> dict:
    """Создает FixedGoalWithSpinLimiter параметры"""
    return {
        "FixedGoalWithSpinLimiter": {
            "Target": target,
            "SpinLimiter": spin_limiter
        }
    }


def make_reward(reward_type: str, params: dict) -> dict:
    """
    Создает награду указанного типа с параметрами
    """
    if reward_type == "Chips":
        return {"FixedReward": {"Currency": "Chips", "Amount": params.get("amount", 0)}}
    elif reward_type == "VariableChips":
        return {"RtpReward": {
            "Currency": "Chips",
            "Percentage": params.get("percentage", 0.03),
            "Min": params.get("min", 250000),
            "Max": params.get("max", 10000000)
        }}
    elif reward_type == "MLM":
        return {"FixedReward": {"Currency": "Tickets", "Amount": params.get("amount", 250000)}}
    elif reward_type == "Loyalty Point":
        return {"FixedReward": {"Currency": "Loyalty", "Amount": params.get("amount", 250000)}}
    elif reward_type == "Vip Points":
        return {"FixedReward": {"Currency": "VipPoints", "Amount": params.get("amount", 250000)}}
    elif reward_type == "Sweepstakes":
        return {"FixedReward": {"Currency": "Entries_Name", "Amount": params.get("amount", 250000)}}
    elif reward_type == "FreePlays":
        return {"FreeplayUnlockReward": {
            "GameName": params.get("game_name", "Buffalo"),
            "Spins": params.get("spins", 16)
        }}
    elif reward_type == "Packs":
        return {"CollectableSellPacksReward": {
            "PackId": params.get("pack_id", "sellPack50"),
            "NumPacks": params.get("num_packs", 4)
        }}
    elif reward_type == "BoardGameDices":
        return {"FixedReward": {"Currency": "BoardGameDices", "Amount": params.get("amount", 2)}}
    elif reward_type == "BoardGameBuilds":
        return {"FixedReward": {"Currency": "BoardGameBuilds", "Amount": params.get("amount", 2)}}
    elif reward_type == "BoardGameRareBuilds":
        return {"FixedReward": {"Currency": "BoardGameRareBuilds", "Amount": params.get("amount", 2)}}
    else:
        return {"FixedReward": {"Currency": "Chips", "Amount": 0}}


def make_progress_node(node_id: int, next_ids: list[int], game_list: list[str], min_bet: dict,
                       goal: dict, rewards: list[dict], is_last: bool,
                       resegment: bool, mini_game: str, contribution_level: str,
                       button_action_type: str, button_action_data: str, button_action_text: str,
                       custom_texts: list[str], possible_item_collect: str = "") -> dict:
    node = {
        "ProgressNode": {
            "NodeID": node_id,
            "NextNodeID": next_ids,
            "GameList": game_list,
            "MinBet": min_bet,
            "Goal": goal,
            "Rewards": rewards,
            "IsLastNode": is_last,
            "ResegmentFlag": resegment,
            "MiniGame": mini_game,
            "ContributionLevel": contribution_level,
            "ButtonActionType": button_action_type,
            "ButtonActionData": button_action_data,
            "ButtonActionText": button_action_text,
            "CustomTexts": custom_texts,
        }
    }
    if possible_item_collect:
        node["ProgressNode"]["PossibleItemCollect"] = possible_item_collect
    return node


def make_entries_node(node_id: int, game_list: list[str], min_bet: dict,
                      goal_types: list[str], resegment: bool,
                      button_action_type: str, button_action_data: str, button_action_text: str,
                      custom_texts: list[str], entry_types: list[str],
                      possible_item_collect: str = "Default") -> dict:
    return {
        "EntriesNode": {
            "NodeID": node_id,
            "GameList": game_list,
            "MinBet": min_bet,
            "GoalType": goal_types,
            "ResegmentFlag": resegment,
            "ButtonActionType": button_action_type,
            "ButtonActionData": button_action_data,
            "ButtonActionText": button_action_text,
            "CustomTexts": custom_texts,
            "PossibleItemCollect": possible_item_collect,
            "EntryTypes": entry_types,
        }
    }


def make_dummy_choice_node(node_id: int, next_ids: list[int], rewards: list[dict], is_last: bool,
                           resegment: bool, mini_game: str, contribution_level: str,
                           button_action_type: str, button_action_data: str, button_action_text: str,
                           custom_texts: list[str], is_choice_event: bool = True) -> dict:
    return {
        "DummyNode": {
            "NodeID": node_id,
            "NextNodeID": next_ids,
            "Rewards": rewards,
            "IsLastNode": is_last,
            "ResegmentFlag": resegment,
            "MiniGame": mini_game,
            "ContributionLevel": contribution_level,
            "ButtonActionType": button_action_type,
            "ButtonActionData": button_action_data,
            "ButtonActionText": button_action_text,
            "CustomTexts": custom_texts,
            "IsChoiceEvent": is_choice_event,
        }
    }


def make_node_event(event_id: str, min_level: int, segment: str,
                    asset_bundle_path: str, blocker_prefab_path: str, roundel_prefab_path: str,
                    event_card_prefab_path: str, node_completion_prefab_path: str,
                    content_key: str, number_of_repeats: int,
                    starting_event_currency: float, is_currency_event: bool,
                    time_warning_iso: str, entry_types: list[str],
                    segments: dict = None) -> dict:
    """
    Создает событие с поддержкой множественных сегментов
    """
    # Преобразуем segments в правильный формат, если необходимо
    # Если segments не передан, создаем пустой словарь
    if segments is None:
        segments = {}
    formatted_segments = {}
    for seg_name, seg_data in segments.items():
        if isinstance(seg_data, dict) and "Stages" in seg_data and "PossibleSegmentInfo" in seg_data:
            # Если уже в правильном формате с PossibleSegmentInfo
            formatted_segments[seg_name] = seg_data
        elif isinstance(seg_data, dict) and "Stages" in seg_data:
            # Если есть Stages но нет PossibleSegmentInfo
            formatted_segments[seg_name] = {
                "Stages": seg_data["Stages"],
                "PossibleSegmentInfo": {
                    "VIPRange": "1-10+"  # Значение по умолчанию
                }
            }
        elif isinstance(seg_data, list):
            # Если stages - это список, создаем структуру с PossibleSegmentInfo по умолчанию
            formatted_segments[seg_name] = {
                "Stages": seg_data,
                "PossibleSegmentInfo": {
                    "VIPRange": "1-10+"  # Значение по умолчанию
                }
            }
        else:
            # Если неизвестный формат, создаем пустую структуру
            formatted_segments[seg_name] = {
                "Stages": [], 
                "PossibleSegmentInfo": {
                    "VIPRange": "1-10+"
                }
            }
    
    return {
        "PossibleNodeEventData": {
            "EventID": event_id,
            "MinLevel": min_level,
            "Segment": segment,
            "AssetBundlePath": asset_bundle_path,
            "BlockerPrefabPath": blocker_prefab_path,
            "RoundelPrefabPath": roundel_prefab_path,
            "EventCardPrefabPath": event_card_prefab_path,
            "NodeCompletionPrefabPath": node_completion_prefab_path,
            "ContentKey": content_key,
            "NumberOfRepeats": number_of_repeats,
            "StartingEventCurrency": starting_event_currency,
            "IsCurrencyEvent": is_currency_event,
            "TimeWarning": time_warning_iso,
            "EntryTypes": entry_types,
            "Segments": formatted_segments,
        }
    }


def make_stage(stage_id: int, nodes: list) -> dict:
    """Создает стадию с указанным ID и списком нод"""
    return {"StageID": stage_id, "Nodes": nodes}

def make_segment(segment_name: str, vip_range: str) -> dict:  # <-- Переместите сюда
    """Создает новый сегмент с пустой стадией"""
    return {
        segment_name: {
            "Stages": [make_stage(1, [])],
            "PossibleSegmentInfo": {
                "VIPRange": vip_range
            }
        }
    }

def display_event_structure(event, event_idx=None):
    """Показывает древовидную структуру события с кнопками управления сегментами"""
    event_data = event['PossibleNodeEventData']
    # Контейнер для Ивента с кнопками
    col_event1, col_event2, col_event3 = st.columns([3, 1, 1])
    with col_event1:
        st.write(f"📦 **Событие:** {event_data['EventID']}")
    with col_event2:
        if st.button(f"✏️", key=f"edit_event_{idx}", help=f"Редактировать событие {event_data['EventID']}"):
            # Загружаем событие для редактирования
            event_data = event['PossibleNodeEventData']
            segments = event_data.get('Segments', {})
            
            # Преобразуем сегменты в формат для редактирования
            formatted_segments = {}
            for seg_name, seg_data in segments.items():
                if isinstance(seg_data, dict):
                    # Проверяем, есть ли уже структура с Stages и PossibleSegmentInfo
                    if "Stages" in seg_data and "PossibleSegmentInfo" in seg_data:
                        formatted_segments[seg_name] = seg_data
                    elif "Stages" in seg_data:
                        # Добавляем PossibleSegmentInfo если его нет
                        formatted_segments[seg_name] = {
                            "Stages": seg_data["Stages"],
                            "PossibleSegmentInfo": {"VIPRange": "1-10+"}
                        }
                    else:
                        # Если сегмент в другом формате, создаем правильную структуру
                        formatted_segments[seg_name] = {
                            "Stages": seg_data if isinstance(seg_data, list) else [],
                            "PossibleSegmentInfo": {"VIPRange": "1-10+"}
                        }
                elif isinstance(seg_data, list):
                    formatted_segments[seg_name] = {
                        "Stages": seg_data,
                        "PossibleSegmentInfo": {"VIPRange": "1-10+"}
                    }
                else:
                    formatted_segments[seg_name] = {
                        "Stages": [], 
                        "PossibleSegmentInfo": {"VIPRange": "1-10+"}
                    }
            
            st.session_state.current_event_segments = formatted_segments
            st.session_state.current_editing_segment = None
            st.session_state.current_editing_nodes = []
            st.session_state.editing_event_idx = idx
            st.session_state.temp_rewards = []
            st.session_state.temp_goal = None
            st.session_state.progress_rewards = []
            st.session_state.progress_goal = None
            
            # Очищаем старые примененные цели
            for key in list(st.session_state.keys()):
                if key.startswith("applied_goal_"):
                    del st.session_state[key]
            
            st.success(f"✅ Событие загружено для редактирования. Перейдите на вкладку 'Настройка события'")
    with col_event3:
        if st.button(f"❌", key=f"del_event_{idx}", help=f"Удалить событие {event_data['EventID']}"):
            st.session_state.cfg["Events"].pop(idx)
            st.rerun()
    
    # Отображаем все сегменты
    segments = event_data.get('Segments', {})
    
    if not segments:
        st.info("   📭 Нет сегментов в этом событии")
        return
    
    for segment_name, segment_data in segments.items():
        # Создаем уникальный ключ для сегмента
        segment_key = f"{event_data['EventID']}_{segment_name}"
        
        # Контейнер для сегмента с кнопками
        col_seg1, col_seg2, col_seg3 = st.columns([3, 1, 1])
        
        with col_seg1:
            # Получаем VIPRange из PossibleSegmentInfo
            vip_range = "N/A"
            if isinstance(segment_data, dict):
                segment_info = segment_data.get('PossibleSegmentInfo', {})
                vip_range = segment_info.get('VIPRange', 'N/A')
            
            st.write(f"   📁 **Сегмент:** {segment_name} (VIP: {vip_range})")
        
        with col_seg2:
            # Кнопка редактирования сегмента
            if st.button("✏️", key=f"edit_seg_{segment_key}", help=f"Редактировать сегмент {segment_name}"):
                if event_idx is not None:
                    # Загружаем сегмент в режим редактирования
                    if isinstance(segment_data, dict):
                        if "Stages" in segment_data:
                            # Сохраняем сегмент с правильной структурой
                            st.session_state.current_event_segments = {segment_name: deepcopy(segment_data)}
                        else:
                            # Если нет Stages, создаем правильную структуру
                            st.session_state.current_event_segments = {
                                segment_name: {
                                    "Stages": segment_data.get('Stages', []) if isinstance(segment_data, dict) else [],
                                    "PossibleSegmentInfo": segment_data.get('PossibleSegmentInfo', {"VIPRange": "1-10+"})
                                }
                            }
                    elif isinstance(segment_data, list):
                        st.session_state.current_event_segments = {
                            segment_name: {
                                "Stages": segment_data,
                                "PossibleSegmentInfo": {"VIPRange": "1-10+"}
                            }
                        }
                    else:
                        st.session_state.current_event_segments = {
                            segment_name: {
                                "Stages": [],
                                "PossibleSegmentInfo": {"VIPRange": "1-10+"}
                            }
                        }
                    
                    st.session_state.current_editing_segment = segment_name
                    
                    # Загружаем ноды из Stage 1
                    stages = []
                    if isinstance(segment_data, dict):
                        stages = segment_data.get('Stages', [])
                    elif isinstance(segment_data, list):
                        stages = segment_data
                    
                    if stages and len(stages) > 0:
                        if isinstance(stages[0], dict):
                            st.session_state.current_editing_nodes = stages[0].get('Nodes', [])
                        else:
                            st.session_state.current_editing_nodes = []
                    else:
                        st.session_state.current_editing_nodes = []
                    
                    st.session_state.editing_event_idx = event_idx
                    st.session_state.temp_rewards = []
                    st.session_state.temp_goal = None
                    st.session_state.progress_rewards = []
                    st.session_state.progress_goal = None
                    
                    st.success(f"✅ Сегмент '{segment_name}' загружен для редактирования. Перейдите на вкладку 'Настройка события'")
        
        with col_seg3:
            # Кнопка удаления сегмента
            if st.button("❌", key=f"del_seg_{segment_key}", help=f"Удалить сегмент {segment_name}"):
                if event_idx is not None:
                    # Удаляем сегмент
                    del segments[segment_name]
                    # Обновляем событие
                    event['PossibleNodeEventData']['Segments'] = segments
                    st.success(f"✅ Сегмент '{segment_name}' удален")
                    st.rerun()
        
        # Теперь отображаем содержимое сегмента (стадии и ноды) под ним
        with st.container():
            st.write("      ")  # Отступ для содержимого
            
            # Проверяем тип segment_data
            if isinstance(segment_data, dict) and 'Stages' in segment_data:
                # Если это словарь с ключом 'Stages'
                stages = segment_data['Stages']
            elif isinstance(segment_data, list):
                # Если это список стадий напрямую (альтернативный формат)
                stages = segment_data
            else:
                st.warning(f"      ⚠️ Неизвестный формат данных для сегмента {segment_name}")
                continue
            
            # Отображаем стадии
            for stage in stages:
                if isinstance(stage, dict):
                    stage_id = stage.get('StageID', 'N/A')
                    nodes = stage.get('Nodes', [])
                else:
                    st.warning(f"      ⚠️ Неизвестный формат стадии")
                    continue
                    
                for i, node_data in enumerate(nodes):
                    if not isinstance(node_data, dict):
                        continue
                        
                    node_type = list(node_data.keys())[0] if node_data else "Unknown"
                    node_info = node_data.get(node_type, {})
                    # Контейнер для сегмента с кнопками
                    col_node1, col_node2, col_node3 = st.columns([3, 1, 1])
                    with col_node1:
                        st.write(f"         🔹 {node_type} (NodeID: {node_info.get('NodeID', 'N/A')}, NextNodeID: {node_info.get('NextNodeID', 'N/A')})")
                    with col_node2:
                        if st.button("✏️", key=f"edit_node_{event_idx}_{segment_name}_{stage_id}_{i}", help=f"Редактировать ноду {node_info.get('NodeID', 'N/A')}"):
                            # Здесь будет логика редактирования ноды
                            st.info(f"🔄 Редактирование ноды {node_info.get('NodeID', 'N/A')} будет доступно в следующей версии")                       
                    with col_node3:
                        # Кнопка удаления ноды
                        if st.button("❌", key=f"del_node_{event_idx}_{segment_name}_{stage_id}_{i}", help=f"Удалить ноду {node_info.get('NodeID', 'N/A')}"):
                            # Удаляем ноду из списка
                            nodes.pop(i)
                            # Обновляем данные
                            if isinstance(segment_data, dict) and 'Stages' in segment_data:
                                for s in segment_data['Stages']:
                                    if s.get('StageID') == stage_id:
                                        s['Nodes'] = nodes
                                        break
                            elif isinstance(segment_data, list):
                                # Если сегмент - это список стадий
                                for s in segment_data:
                                    if isinstance(s, dict) and s.get('StageID') == stage_id:
                                        s['Nodes'] = nodes
                                        break
                            
                            st.success(f"✅ Нода {node_info.get('NodeID', 'N/A')} удалена")
                            st.rerun()
                        



def make_minbet_block(prefix="", default_type="Fixed"):
    """
    Создает блок выбора типа MinBet (Fixed или Variable)
    Возвращает словарь с конфигурацией MinBet
    """
    st.write("**Тип MinBet:**")
    
    minbet_type = st.radio(
        "Выберите тип",
        options=["Fixed", "Variable"],
        index=0,
        key=f"{prefix}_minbet_type",
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if minbet_type == "Variable":
        col1, col2, col3 = st.columns(3)
        with col1:
            var = st.number_input(
                f"{prefix}Variable", 
                value=0.8, 
                min_value=0.0, 
                max_value=10.0, 
                step=0.1,
                format="%.2f",
                key=f"{prefix}_var"
            )
        with col2:
            min_v = st.number_input(
                f"{prefix}Min", 
                value=25000.0, 
                min_value=0.0, 
                step=1000.0,
                format="%.2f",
                key=f"{prefix}_min"
            )
        with col3:
            max_v = st.number_input(
                f"{prefix}Max", 
                value=5000000.0, 
                min_value=0.0, 
                step=10000.0,
                format="%.2f",
                key=f"{prefix}_max"
            )
        return make_minbet_variable(float(var), float(min_v), float(max_v))
    else:
        col1, _ = st.columns([1, 2])
        with col1:
            fixed_value = st.number_input(
                f"{prefix}Fixed MinBet", 
                value=250000.0, 
                min_value=0.0, 
                step=10000.0,
                format="%.2f",
                key=f"{prefix}_fixed"
            )
        return make_fixed_minbet(float(fixed_value))


def goal_creator_block(prefix="", goal_index=0, key_suffix=""):
    """
    Создает интерфейс для создания цели
    goal_index - уникальный индекс для создания уникальных ключей
    key_suffix - дополнительный суффикс для ключей
    Возвращает словарь с целью (Type + параметры) или None, если не применяли
    """
    unique_key = f"{prefix}_goal_{goal_index}_{key_suffix}"
    
    # Используем session state для хранения временных значений цели
    if f"temp_goal_type_{unique_key}" not in st.session_state:
        st.session_state[f"temp_goal_type_{unique_key}"] = "Spins"
    if f"temp_goal_params_{unique_key}" not in st.session_state:
        st.session_state[f"temp_goal_params_{unique_key}"] = "FixedGoal"
    
    col1, col2 = st.columns([1, 3])
    with col1:
        goal_type = st.text_input(
            "Тип цели (Type)",
            value=st.session_state[f"temp_goal_type_{unique_key}"],
            key=f"{unique_key}_type_str",
            help="Строка, которая будет в массиве Type, например: Item_BISON, Spins, и т.д."
        )
        # Сохраняем в session state
        st.session_state[f"temp_goal_type_{unique_key}"] = goal_type
    
    with col2:
        goal_params_type = st.selectbox(
            "Параметры цели",
            options=[
                "SpinpadGoal",
                "FixedGoal",
                "ConsecutiveWinsGoal",
                "TotalCoinsPerDay",
                "TotalCoinsPerDayWithSpinLimiter",
                "FixedGoalWithSpinLimiter"
            ],
            index=1,
            key=f"{unique_key}_params_type"
        )
        # Сохраняем в session state
        st.session_state[f"temp_goal_params_{unique_key}"] = goal_params_type
    
    st.write("**Параметры:**")
    
    # Используем unique ключи для всех элементов ввода
    if goal_params_type == "SpinpadGoal":
        c1, c2, c3 = st.columns(3)
        with c1:
            multiplier = st.number_input(
                "Multiplier",
                value=0.5,
                min_value=0.0,
                max_value=10.0,
                step=0.1,
                format="%.3f",
                key=f"{unique_key}_multiplier"
            )
        with c2:
            min_val = st.number_input(
                "Min",
                value=10,
                min_value=1,
                step=1,
                key=f"{unique_key}_min"
            )
        with c3:
            max_val = st.number_input(
                "Max",
                value=150,
                min_value=1,
                step=1,
                key=f"{unique_key}_max"
            )
        goal_params = make_spinpad_goal(float(multiplier), int(min_val), int(max_val))
    
    elif goal_params_type == "FixedGoal":
        target = st.number_input(
            "Target",
            value=20,
            min_value=1,
            step=1,
            key=f"{unique_key}_target"
        )
        goal_params = make_fixed_goal(int(target))
    
    elif goal_params_type == "ConsecutiveWinsGoal":
        c1, c2 = st.columns(2)
        with c1:
            streaks = st.number_input(
                "Number of Streaks",
                value=3,
                min_value=1,
                step=1,
                key=f"{unique_key}_streaks"
            )
        with c2:
            multiplier = st.number_input(
                "Multiplier",
                value=0.01,
                min_value=0.0,
                max_value=1.0,
                step=0.01,
                format="%.3f",
                key=f"{unique_key}_wins_multiplier"
            )
        
        c3, c4 = st.columns(2)
        with c3:
            min_val = st.number_input(
                "Min",
                value=2,
                min_value=1,
                step=1,
                key=f"{unique_key}_wins_min"
            )
        with c4:
            max_val = st.number_input(
                "Max",
                value=5,
                min_value=1,
                step=1,
                key=f"{unique_key}_wins_max"
            )
        goal_params = make_consecutive_wins_goal(int(streaks), float(multiplier), int(min_val), int(max_val))
    
    elif goal_params_type == "TotalCoinsPerDay":
        c1, c2, c3 = st.columns(3)
        with c1:
            multiplier = st.number_input(
                "Multiplier",
                value=0.5,
                min_value=0.0,
                max_value=10.0,
                step=0.1,
                format="%.3f",
                key=f"{unique_key}_tcpd_multiplier"
            )
        with c2:
            min_val = st.number_input(
                "Min",
                value=10,
                min_value=1,
                step=1,
                key=f"{unique_key}_tcpd_min"
            )
        with c3:
            max_val = st.number_input(
                "Max",
                value=150,
                min_value=1,
                step=1,
                key=f"{unique_key}_tcpd_max"
            )
        goal_params = make_total_coins_per_day_goal(float(multiplier), int(min_val), int(max_val))
    
    elif goal_params_type == "TotalCoinsPerDayWithSpinLimiter":
        c1, c2 = st.columns(2)
        with c1:
            spin_limiter = st.number_input(
                "Spin Limiter",
                value=3,
                min_value=1,
                step=1,
                key=f"{unique_key}_spin_limiter"
            )
            multiplier = st.number_input(
                "Multiplier",
                value=0.097,
                min_value=0.0,
                max_value=1.0,
                step=0.001,
                format="%.3f",
                key=f"{unique_key}_tcpdwl_multiplier"
            )
        with c2:
            min_val = st.number_input(
                "Min",
                value=3500000,
                min_value=1,
                step=1000,
                key=f"{unique_key}_tcpdwl_min"
            )
            max_val = st.number_input(
                "Max",
                value=50000000,
                min_value=1,
                step=1000,
                key=f"{unique_key}_tcpdwl_max"
            )
        goal_params = make_total_coins_per_day_with_spin_limiter_goal(int(spin_limiter), float(multiplier), int(min_val), int(max_val))
    
    elif goal_params_type == "FixedGoalWithSpinLimiter":
        c1, c2 = st.columns(2)
        with c1:
            target = st.number_input(
                "Target",
                value=10,
                min_value=1,
                step=1,
                key=f"{unique_key}_fgwl_target"
            )
        with c2:
            spin_limiter = st.number_input(
                "Spin Limiter",
                value=3,
                min_value=1,
                step=1,
                key=f"{unique_key}_fgwl_spin_limiter"
            )
        goal_params = make_fixed_goal_with_spin_limiter_goal(int(target), int(spin_limiter))
    
    st.write("---")
    
    # Кнопка применения цели
    col_button1, col_button2 = st.columns(2)
    with col_button1:
        apply_button = st.button("✅ Применить цель", key=f"{unique_key}_apply", use_container_width=True)
    with col_button2:
        clear_button = st.button("🔄 Очистить", key=f"{unique_key}_clear", use_container_width=True)
    
    if apply_button:
        # Создаем полную цель с Type и параметрами
        goal = make_goal(goal_type, goal_params)
        st.session_state[f"applied_goal_{unique_key}"] = goal
        st.success(f"✅ Цель применена: {goal_type} с параметрами {goal_params_type}")
        return goal
    elif clear_button:
        if f"applied_goal_{unique_key}" in st.session_state:
            del st.session_state[f"applied_goal_{unique_key}"]
        st.info("🔄 Цель очищена")
        return None
    
    # Возвращаем примененную цель, если она есть
    if f"applied_goal_{unique_key}" in st.session_state:
        return st.session_state[f"applied_goal_{unique_key}"]
    
    return None


def reward_creator_block(prefix="", reward_index=0):
    """
    Создает интерфейс для создания награды
    reward_index - уникальный индекс для создания уникальных ключей
    Возвращает словарь с наградой или None
    """
    unique_key = f"{prefix}_reward_{reward_index}"
    
    col1, col2 = st.columns([1, 3])
    with col1:
        reward_type = st.selectbox(
            "Тип награды",
            options=[
                "Chips", "VariableChips", "MLM", "Loyalty Point", 
                "Vip Points", "Sweepstakes", "FreePlays", "Packs",
                "BoardGameDices", "BoardGameBuilds", "BoardGameRareBuilds"
            ],
            key=f"{unique_key}_type"
        )
    
    params = {}
    with col2:
        if reward_type in ["Chips", "MLM", "Loyalty Point", "Vip Points", "Sweepstakes"]:
            amount = st.number_input(
                "Amount", 
                value=250000.0, 
                min_value=0.0, 
                step=1000.0,
                format="%.2f",
                key=f"{unique_key}_amount"
            )
            params["amount"] = float(amount)
        
        elif reward_type == "VariableChips":
            c1, c2, c3 = st.columns(3)
            with c1:
                percentage = st.number_input(
                    "Percentage", 
                    value=0.03, 
                    min_value=0.0, 
                    max_value=1.0, 
                    step=0.01,
                    format="%.3f",
                    key=f"{unique_key}_percentage"
                )
            with c2:
                min_val = st.number_input(
                    "Min", 
                    value=250000.0, 
                    min_value=0.0, 
                    step=10000.0,
                    format="%.2f",
                    key=f"{unique_key}_min"
                )
            with c3:
                max_val = st.number_input(
                    "Max", 
                    value=10000000.0, 
                    min_value=0.0, 
                    step=100000.0,
                    format="%.2f",
                    key=f"{unique_key}_max"
                )
            params.update({
                "percentage": float(percentage),
                "min": float(min_val),
                "max": float(max_val)
            })
        
        elif reward_type == "FreePlays":
            c1, c2 = st.columns(2)
            with c1:
                game_name = st.text_input(
                    "Game Name", 
                    value="Buffalo",
                    key=f"{unique_key}_game_name"
                )
            with c2:
                spins = st.number_input(
                    "Spins", 
                    value=16, 
                    min_value=1, 
                    step=1,
                    key=f"{unique_key}_spins"
                )
            params.update({
                "game_name": game_name,
                "spins": int(spins)
            })
        
        elif reward_type == "Packs":
            c1, c2 = st.columns(2)
            with c1:
                pack_id = st.text_input(
                    "Pack ID", 
                    value="sellPack50",
                    key=f"{unique_key}_pack_id"
                )
            with c2:
                num_packs = st.number_input(
                    "Number of Packs", 
                    value=4, 
                    min_value=1, 
                    step=1,
                    key=f"{unique_key}_num_packs"
                )
            params.update({
                "pack_id": pack_id,
                "num_packs": int(num_packs)
            })
        
        elif reward_type in ["BoardGameDices", "BoardGameBuilds", "BoardGameRareBuilds"]:
            amount = st.number_input(
                "Amount", 
                value=2, 
                min_value=1, 
                step=1,
                key=f"{unique_key}_board_amount"
            )
            params["amount"] = int(amount)
    
    return make_reward(reward_type, params)

def get_default_goal():
    """Возвращает цель по умолчанию (FixedGoal)"""
    return make_goal("Spins", make_fixed_goal(20))
    
def get_default_reward():
    """Возвращает награду по умолчанию (Chips)"""
    return make_reward("Chips", {"amount": 2500000})

def process_multiline_custom_texts(text: str) -> list[str]:
    """
    Преобразует многострочный текст в список строк
    Пустые строки игнорируются
    """
    if not text:  # Если текст пустой, возвращаем пустой список
        return []
    
    # Разделяем по строкам, удаляем пустые и обрезаем пробелы
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return lines

st.set_page_config(page_title="LiveEvent JSON Builder", layout="wide")
st.title("🎮 LiveEvent JSON Builder")

# Инициализация session state
if "cfg" not in st.session_state:
    st.session_state.cfg = ensure_root({"Events": [], "IsFallbackConfig": False})
if "schema" not in st.session_state:
    st.session_state.schema = None
if "current_event_segments" not in st.session_state:
    st.session_state.current_event_segments = {}
if "current_editing_segment" not in st.session_state:
    st.session_state.current_editing_segment = None
if "current_editing_nodes" not in st.session_state:
    st.session_state.current_editing_nodes = []
if "editing_event_idx" not in st.session_state:
    st.session_state.editing_event_idx = -1
if "current_event_idx" not in st.session_state:
    st.session_state.current_event_idx = -1
if "creation_mode" not in st.session_state:
    st.session_state.creation_mode = "event"
if "temp_rewards" not in st.session_state:
    st.session_state.temp_rewards = [get_default_reward()]  # Изменено
if "temp_goal" not in st.session_state:
    st.session_state.temp_goal = get_default_goal()  # Изменено
if "last_node_tab" not in st.session_state:
    st.session_state.last_node_tab = None
if 'progress_rewards' not in st.session_state:
    st.session_state.progress_rewards = [get_default_reward()]  # Изменено
if 'progress_goal' not in st.session_state:
    st.session_state.progress_goal = get_default_goal()  # Изменено
if 'last_progress_reward_count' not in st.session_state:
    st.session_state.last_progress_reward_count = 0
if "current_segment_name" not in st.session_state:
    st.session_state.current_segment_name = ""


# Создаем 3 главные вкладки
tab1, tab2, tab3 = st.tabs([
    "📁 1. Загрузка и валидация", 
    "⚙️ 2. Настройка события", 
    "🌳 3. Структура и сохранение"
])

# ========== ВКЛАДКА 1: ЗАГРУЗКА И ВАЛИДАЦИЯ ==========
with tab1:
    st.header("Загрузка и валидация JSON")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📂 Загрузка конфига")
        
        # Загрузка существующего JSON
        uploaded_json = st.file_uploader("Загрузить существующий JSON", type=["json"], key="upload_json")
        if uploaded_json is not None:
            try:
                loaded = json.loads(uploaded_json.read().decode("utf-8"))
                st.session_state.cfg = ensure_root(loaded)
                st.success("✅ JSON успешно загружен")
            except Exception as e:
                st.error(f"❌ Ошибка загрузки: {e}")
        
        st.subheader("🔍 JSON Schema валидация")
        
        # Загрузка схемы
        schema_file = st.file_uploader("Загрузить JSON-Schema (schema.json)", type=["json"], key="schema_upload")
        if schema_file is not None:
            try:
                st.session_state.schema = json.loads(schema_file.read().decode("utf-8"))
                st.success("✅ Schema загружена")
            except Exception as e:
                st.error(f"❌ Ошибка загрузки схемы: {e}")
        
        # Кнопка валидации
        can_validate = HAS_JSONSCHEMA and st.session_state.schema is not None
        
        if st.button("✅ Проверить валидацию", disabled=not can_validate, use_container_width=True):
            try:
                jsonschema.validate(instance=st.session_state.cfg, schema=st.session_state.schema)
                st.success("✅ JSON полностью валиден по схеме!")
            except Exception as e:
                st.error(f"❌ Ошибка валидации: {e}")
        
        if not HAS_JSONSCHEMA:
            st.info("📌 Для валидации установите jsonschema: `pip install jsonschema`")
    
    with col2:
        # Управление конфигом
        st.divider()
        st.subheader("🆕 Новый конфиг")
        
        if st.button("🗑️ Создать новый пустой конфиг", use_container_width=True):
            st.session_state.cfg = ensure_root({"Events": [], "IsFallbackConfig": st.session_state.cfg["IsFallbackConfig"]})
            st.session_state.current_event_segments = {}
            st.session_state.current_editing_segment = None
            st.session_state.current_editing_nodes = []
            st.session_state.editing_event_idx = -1
            st.session_state.temp_rewards = []
            st.session_state.temp_goal = None
            st.success("✅ Создан новый пустой конфиг")

# ========== ВКЛАДКА 2: НАСТРОЙКА СОБЫТИЯ ==========
with tab2:
    # Отображение текущего состояния
    col_status1, col_status2, col_status3 = st.columns(3)
    with col_status1:
        if st.session_state.cfg["Events"]:
            st.info(f"📊 Всего событий: {len(st.session_state.cfg['Events'])}")
        else:
            st.info("📊 Нет событий")
    
    with col_status2:
        if st.session_state.current_event_idx >= 0:
            event_name = st.session_state.cfg["Events"][st.session_state.current_event_idx]["PossibleNodeEventData"]["EventID"]
            st.info(f"✏️ Текущее событие: {event_name}")
    
    with col_status3:
        st.info(f"📌 Режим: {st.session_state.creation_mode}")
    
    st.divider()
    
    colwww1, colwww2 =  st.columns(2)
    with colwww1:
        # ===== ШАГ 1: СОЗДАНИЕ СОБЫТИЯ =====
        with st.expander("📋 ШАГ 1: Создание события", expanded=st.session_state.creation_mode == "event"):
            st.write("Заполните общие параметры события и нажмите кнопку 'Добавить событие'")
            
            col1, col2 = st.columns(2)
            
            with col1:
                event_id = st.text_input("EventID", value="MyEvent", key="event_id")
                asset_bundle = st.text_input("AssetBundlePath", value="_events/MyEvent", key="asset_bundle")
                blocker = st.text_input("BlockerPrefabPath", value="Dialogs/MyEvent_Dialog", key="blocker")
                node_completion = st.text_input("NodeCompletionPrefabPath", value="Dialogs/MyEvent_Dialog", key="node_completion")
                event_card = st.text_input("EventCardPrefabPath", value="", key="event_card")
            
            with col2:
                roundel = st.text_input("RoundelPrefabPath", value="Roundels/MyEvent_Roundel", key="roundel")
                content_key = st.text_input("ContentKey", value="MyEvent", key="content_key")
                min_level = st.number_input("MinLevel", min_value=1, value=1, step=1, key="min_level")
                repeats = st.number_input("NumberOfRepeats", value=-1, step=1, key="repeats")
                segment = st.text_input("Segment (основной сегмент)", value="Default", key="segment")
            
            col3, col4 = st.columns(2)
            with col3:
                time_warning = st.text_input("TimeWarning (ISO)", value="2026-02-21T16:00:00Z", key="time_warning")
                start_currency = st.number_input("StartingEventCurrency", value=0.0, key="start_currency")
            
            with col4:
                is_currency_event = st.checkbox("IsCurrencyEvent", value=False, key="is_currency")
                entry_types = st.text_input("EntryTypes (через запятую)", value="", key="event_entry_types")
            
            # Кнопка добавления события
            if st.button("➕ ДОБАВИТЬ СОБЫТИЕ", use_container_width=True, type="primary"):
                # Создаем событие
                ev = make_node_event(
                    event_id=event_id,
                    min_level=int(min_level),
                    segment=segment,
                    asset_bundle_path=asset_bundle,
                    blocker_prefab_path=blocker,
                    roundel_prefab_path=roundel,
                    event_card_prefab_path=event_card,
                    node_completion_prefab_path=node_completion,
                    content_key=content_key,
                    number_of_repeats=int(repeats),
                    starting_event_currency=float(start_currency),
                    is_currency_event=bool(is_currency_event),
                    time_warning_iso=time_warning,
                    entry_types=[x.strip() for x in entry_types.split(",") if x.strip()],
                )
                
                # Добавляем в конфиг
                st.session_state.cfg["Events"].append(ev)
                st.session_state.current_event_idx = len(st.session_state.cfg["Events"]) - 1
                st.session_state.creation_mode = "segment"
                st.success(f"✅ Событие {event_id} добавлено! Теперь можно добавлять сегменты")
                st.rerun()
        
        # ===== ШАГ 2: СОЗДАНИЕ СЕГМЕНТА =====
        if st.session_state.cfg["Events"] and st.session_state.current_event_idx >= 0:
            with st.expander("📁 ШАГ 2: Создание сегмента", expanded=st.session_state.creation_mode == "segment"):
                st.write("Заполните параметры сегмента и нажмите кнопку 'Добавить сегмент'")
                
                current_event = st.session_state.cfg["Events"][st.session_state.current_event_idx]["PossibleNodeEventData"]
                st.info(f"📦 Текущее событие: {current_event['EventID']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    segment_name = st.text_input("Имя сегмента", value="VIP1_10", key="segment_name")
                with col2:
                    vip_range = st.text_input("VIP Range", value="1-10+", key="vip_range")
                
                # Кнопка добавления сегмента
                if st.button("➕ ДОБАВИТЬ СЕГМЕНТ", use_container_width=True, type="primary"):
                    if segment_name in current_event["Segments"]:
                        st.error(f"❌ Сегмент {segment_name} уже существует!")
                    else:
                        # Создаем сегмент
                        new_segment = make_segment(segment_name, vip_range)
                        current_event["Segments"].update(new_segment)
                        st.session_state.current_segment_name = segment_name
                        st.session_state.current_segment_vip = vip_range
                        st.session_state.creation_mode = "node"
                        st.success(f"✅ Сегмент {segment_name} добавлен! Теперь можно добавлять ноды")
                        st.rerun()
        
        # ===== ШАГ 3: СОЗДАНИЕ НОДЫ =====
        if (st.session_state.cfg["Events"] and st.session_state.current_event_idx >= 0 and 
            st.session_state.current_segment_name):
            
            current_event = st.session_state.cfg["Events"][st.session_state.current_event_idx]["PossibleNodeEventData"]
            
            if st.session_state.current_segment_name in current_event["Segments"]:
                with st.expander("🔧 ШАГ 3: Создание ноды", expanded=st.session_state.creation_mode == "node"):
                    st.write(f"Добавление ноды в сегмент: **{st.session_state.current_segment_name}**")
                    
                    # Вкладки для разных типов нод
                    node_tabs = st.tabs(["📊 Progress Node", "🚪 Entries Node", "🎲 Dummy Choice Node"])
                    
                    # Progress Node Tab
                    with node_tabs[0]:
                        st.subheader("➕ Добавить Progress Node")
                        
                        # Сброс при переключении на вкладку
                        if st.session_state.last_node_tab != "progress":
                            st.session_state.progress_goal = get_default_goal()
                            st.session_state.progress_rewards = [get_default_reward()]
                            st.session_state.last_node_tab = "progress"
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            node_id = st.number_input("NodeID", min_value=1, value=1, step=1, key="p_node_id")
                            next_id = st.number_input("NextNodeID", min_value=1, value=2, step=1, key="p_next_id")
                            games = st.text_input("GameList (через запятую)", value="AllGames", key="p_games")
                            minigame = st.text_input("MiniGame", value="FlatReward", key="minigame")
                        
                        with col2:
                            button_text = st.text_input("ButtonActionText", value="PLAY NOW!", key="btn_1")
                            button_type = st.text_input("ButtonActionType", value="", key="btn_2")
                            button_data = st.text_input("ButtonActionData", value="", key="btn_3")
                            is_last_node = st.checkbox("IsLastNode", value=False, key="is_last")
                        
                        # MinBet выбор
                        min_bet = make_minbet_block("P", default_type="Fixed")
                        
                        st.write("---")
                        st.write("**Цель:**")
                        
                        # Отображение текущей цели
                        if st.session_state.progress_goal is not None:
                            goal = st.session_state.progress_goal
                            goal_types = goal.get('Type', [])
                            goal_type_str = ', '.join(goal_types) if goal_types else "No Type"
                            st.success(f"✅ Текущая цель (по умолчанию): {goal_type_str}")
                            
                            st.write("**Изменить цель (если нужно):**")
                            new_goal = goal_creator_block("P", goal_index=0, key_suffix=f"progress")
                            if new_goal is not None:
                                st.session_state.progress_goal = new_goal
                                st.rerun()
                        
                        st.write("---")
                        st.write("**Награды:**")
                        
                        # Отображение текущих наград
                        if st.session_state.progress_rewards:
                            st.write(f"Добавлено наград: {len(st.session_state.progress_rewards)}")
                            for j, reward in enumerate(st.session_state.progress_rewards):
                                colr1, colr2, colr3 = st.columns([4, 1, 1])
                                with colr1:
                                    if 'FixedReward' in reward:
                                        desc = f"Fixed: {reward['FixedReward'].get('Amount')} {reward['FixedReward'].get('Currency')}"
                                    elif 'RtpReward' in reward:
                                        rtp = reward['RtpReward']
                                        desc = f"RTP: {rtp.get('Percentage')*100}% {rtp.get('Currency')}"
                                    elif 'FreeplayUnlockReward' in reward:
                                        fp = reward['FreeplayUnlockReward']
                                        desc = f"FreePlay: {fp.get('Spins')} on {fp.get('GameName')}"
                                    elif 'CollectableSellPacksReward' in reward:
                                        pack = reward['CollectableSellPacksReward']
                                        desc = f"Packs: {pack.get('NumPacks')}x {pack.get('PackId')}"
                                    else:
                                        desc = str(reward)[:50]
                                    st.write(f"  {j+1}. {desc}")
                                with colr2:
                                    if st.button("✏️", key=f"edit_reward_progress_{j}"):
                                        st.info("Редактирование будет доступно позже")
                                with colr3:
                                    if st.button("❌", key=f"remove_reward_progress_{j}"):
                                        st.session_state.progress_rewards.pop(j)
                                        st.rerun()
                        else:
                            st.info("📭 Награды не добавлены")
                            st.session_state.progress_rewards = [get_default_reward()]
                            st.rerun()
                        
                        # Добавление новой награды
                        with st.expander("➕ Добавить дополнительную награду"):
                            new_reward = reward_creator_block("P", reward_index=f"progress_extra")
                            col_button, _ = st.columns([1, 3])
                            with col_button:
                                if st.button("➕ Добавить эту награду в список", key="add_reward_progress_extra"):
                                    if new_reward:
                                        st.session_state.progress_rewards.append(new_reward)
                                        st.rerun()
                        
                        custom_texts = st.text_area(
                            "CustomTexts (каждая строка - отдельный текст)", 
                            value="SPIN\n##\nTIMES", 
                            height=None,
                            key="p_ct",
                            help="Вводите каждый текст с новой строки"
                        )
                        item_collect = st.text_input("PossibleItemCollect (optional)", value="", key="p_ic")
                        
                        # Кнопка добавления ноды
                        if st.button("➕ ДОБАВИТЬ PROGRESS NODE", key="add_progress", use_container_width=True, type="primary"):
                            if st.session_state.progress_goal is None:
                                st.warning("⚠️ Цель не установлена, используется по умолчанию")
                                st.session_state.progress_goal = get_default_goal()
                            
                            if not st.session_state.progress_rewards:
                                st.warning("⚠️ Награды не добавлены, используется по умолчанию")
                                st.session_state.progress_rewards = [get_default_reward()]
                            
                            node = make_progress_node(
                                node_id=int(node_id),
                                next_ids=[int(next_id)],
                                game_list=[x.strip() for x in games.split(",") if x.strip()],
                                min_bet=min_bet,
                                goal=st.session_state.progress_goal,
                                rewards=st.session_state.progress_rewards,
                                is_last=is_last_node,
                                resegment=False,
                                mini_game=minigame,
                                contribution_level="Node",
                                button_action_type=button_type,
                                button_action_data=button_data,
                                button_action_text=button_text,
                                custom_texts=process_multiline_custom_texts(custom_texts),
                                possible_item_collect=item_collect.strip(),
                            )
                            
                            # Добавляем ноду в сегмент
                            segment_data = current_event["Segments"][st.session_state.current_segment_name]
                            if segment_data["Stages"]:
                                segment_data["Stages"][0]["Nodes"].append(node)
                            else:
                                segment_data["Stages"] = [make_stage(1, [node])]
                            
                            # Сбрасываем для следующей ноды
                            st.session_state.progress_rewards = [get_default_reward()]
                            st.session_state.progress_goal = get_default_goal()
                            
                            st.success(f"✅ Progress Node (ID: {node_id}) добавлена в сегмент {st.session_state.current_segment_name}")
                            st.rerun()
                    
                    # Entries Node Tab
                    with node_tabs[1]:
                        st.subheader("➕ Добавить Entries Node")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            node_id = st.number_input("NodeID", min_value=1, value=1, step=1, key="e_node_id")
                            game_name = st.text_input("GameName", value="AllGames", key="e_game")
                        
                        with col2:
                            goal_type = st.text_input("GoalType", value="Spins", key="e_goal")
                            button_text = st.text_input("ButtonActionText", value="PLAY NOW!", key="btn_11")
                            button_type = st.text_input("ButtonActionType", value="", key="btn_12")
                            button_data = st.text_input("ButtonActionData", value="", key="btn_13")
                        
                        entry_types_raw = st.text_input("EntryTypes (через запятую)", value="MyEvent", key="e_entry_types")
                        
                        min_bet = make_minbet_block("E", default_type="Fixed")
                        
                        custom_texts = st.text_area(
                            "CustomTexts (каждая строка - отдельный текст)", 
                            value="", 
                            height=None,
                            key="e_ct",
                            help="Вводите каждый текст с новой строки"
                        )
                        item_collect = st.text_input("PossibleItemCollect", value="Default", key="e_ic")
                        
                        if st.button("➕ ДОБАВИТЬ ENTRIES NODE", key="add_entries", use_container_width=True, type="primary"):
                            node = make_entries_node(
                                node_id=int(node_id),
                                game_list=[game_name],
                                min_bet=min_bet,
                                goal_types=[goal_type],
                                resegment=False,
                                button_action_type=button_type,
                                button_action_data=button_data,
                                button_action_text=button_text,
                                custom_texts=process_multiline_custom_texts(custom_texts),
                                entry_types=[x.strip() for x in entry_types_raw.split(",") if x.strip()],
                                possible_item_collect=item_collect.strip() or "Default",
                            )
                            
                            # Добавляем ноду в сегмент
                            segment_data = current_event["Segments"][st.session_state.current_segment_name]
                            if segment_data["Stages"]:
                                segment_data["Stages"][0]["Nodes"].append(node)
                            else:
                                segment_data["Stages"] = [make_stage(1, [node])]
                            
                            st.success(f"✅ Entries Node (ID: {node_id}) добавлена в сегмент {st.session_state.current_segment_name}")
                            st.rerun()
                    
                    # Dummy Choice Tab
                    with node_tabs[2]:
                        st.subheader("➕ Добавить Dummy Choice Node")
                        
                        if st.session_state.last_node_tab != "dummy":
                            st.session_state.last_node_tab = "dummy"
                            st.session_state.temp_rewards = []
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            node_id = st.number_input("NodeID", min_value=1, value=1, step=1, key="d_node_id")
                            next_ids_raw = st.text_input("NextNodeID (через запятую)", value="11,21,31", key="d_next")
                        
                        with col2:
                            button_text = st.text_input("ButtonActionText", value="PLAY NOW!", key="d_btn")
                            is_choice = st.checkbox("IsChoiceEvent", value=True, key="d_choice")
                        
                        st.write("---")
                        st.write("**Награды:**")
                        
                        if st.session_state.temp_rewards:
                            st.write(f"Добавлено наград: {len(st.session_state.temp_rewards)}")
                            for j, reward in enumerate(st.session_state.temp_rewards):
                                colr1, colr2 = st.columns([5, 1])
                                with colr1:
                                    desc = f"Fixed: 0 Chips"
                                    st.write(f"  {j+1}. {desc}")
                                with colr2:
                                    if st.button("❌", key=f"remove_reward_d_{j}"):
                                        st.session_state.temp_rewards.pop(j)
                                        st.rerun()
                        else:
                            st.info("📭 Награды не добавлены")
                        
                        with st.expander("➕ Добавить награду"):
                            st.write("**Фиксированная награда:** 0 Chips")
                            col_button, _ = st.columns([1, 3])
                            with col_button:
                                if st.button("➕ Добавить эту награду в список", key="add_reward_d"):
                                    fixed_reward = {"FixedReward": {"Currency": "Chips", "Amount": 0}}
                                    st.session_state.temp_rewards.append(fixed_reward)
                                    st.rerun()
                        
                        custom_texts = st.text_area(
                            "CustomTexts (каждая строка - отдельный текст)", 
                            value="", 
                            height=None,
                            key="d_ct",
                            help="Вводите каждый текст с новой строки"
                        )
                        
                        if st.button("➕ ДОБАВИТЬ DUMMY NODE", key="add_dummy", use_container_width=True, type="primary"):
                            if not st.session_state.temp_rewards:
                                st.warning("⚠️ Добавьте хотя бы одну награду")
                            else:
                                next_ids = []
                                for x in next_ids_raw.split(","):
                                    x = x.strip()
                                    if x:
                                        try:
                                            next_ids.append(int(x))
                                        except:
                                            pass
                                
                                node = make_dummy_choice_node(
                                    node_id=int(node_id),
                                    next_ids=next_ids if next_ids else [11, 21, 31],
                                    rewards=st.session_state.temp_rewards.copy(),
                                    is_last=False,
                                    resegment=False,
                                    mini_game="FlatReward",
                                    contribution_level="Node",
                                    button_action_type="",
                                    button_action_data="",
                                    button_action_text=button_text,
                                    custom_texts=process_multiline_custom_texts(custom_texts),
                                    is_choice_event=bool(is_choice),
                                )
                                
                                # Добавляем ноду в сегмент
                                segment_data = current_event["Segments"][st.session_state.current_segment_name]
                                if segment_data["Stages"]:
                                    segment_data["Stages"][0]["Nodes"].append(node)
                                else:
                                    segment_data["Stages"] = [make_stage(1, [node])]
                                
                                st.session_state.temp_rewards = []
                                st.success(f"✅ Dummy Node (ID: {node_id}) добавлена в сегмент {st.session_state.current_segment_name}")
                                st.rerun()
        
        # Кнопки управления
        st.divider()
        col_reset1, col_reset2, col_reset3 = st.columns(3)
        
        with col_reset1:
            if st.button("🔄 Начать новое событие", use_container_width=True):
                st.session_state.current_event_idx = -1
                st.session_state.current_segment_name = ""
                st.session_state.creation_mode = "event"
                st.session_state.temp_rewards = []
                st.session_state.temp_goal = None
                st.session_state.progress_rewards = []
                st.session_state.progress_goal = None
                st.rerun()
        
        with col_reset2:
            if st.button("➕ Добавить еще сегмент", use_container_width=True):
                if st.session_state.current_event_idx >= 0:
                    st.session_state.creation_mode = "segment"
                    st.rerun()

    with colwww2:
        # Отображение всех событий
        if st.session_state.cfg.get("Events"):
            st.subheader(f"📋 Все события ({len(st.session_state.cfg['Events'])}):")
            
            for idx, event in enumerate(st.session_state.cfg["Events"]):
                with st.expander(f"Событие {idx+1}: {event['PossibleNodeEventData']['EventID']}"):
                    # Передаем индекс события для возможности редактирования сегментов
                    display_event_structure(event, idx)
                    
        else:
            st.info("📭 Нет сохраненных событий")

# ========== ВКЛАДКА 3: СТРУКТУРА И СОХРАНЕНИЕ ==========
with tab3:
    st.header("Структура события и сохранение")
    
    # Полный JSON
    with st.expander("📄 Полный JSON", expanded=False):
        st.code(json.dumps(st.session_state.cfg, ensure_ascii=False, indent=4), language="json")
    
    # Кнопка скачивания
    st.download_button(
        "📥 Скачать JSON файл",
        data=json.dumps(st.session_state.cfg, ensure_ascii=False, indent=4).encode("utf-8"),
        file_name="LiveEventData.json",
        mime="application/json",
        use_container_width=True
    )