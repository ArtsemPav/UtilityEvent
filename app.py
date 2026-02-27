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

def make_segment(segment_name: str, vip_range: str) -> dict:
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
        if st.button(f"✏️", key=f"edit_event_{event_idx}", help=f"Редактировать событие {event_data['EventID']}"):
            # Загружаем событие для редактирования
            st.session_state.editing_event_data = deepcopy(event_data)
            st.session_state.editing_event_idx = event_idx
            st.session_state.is_editing = True
            st.session_state.is_editing_segment = False
            st.session_state.is_editing_node = False
            st.session_state.creation_mode = "event"
            st.session_state.force_expand_event = True
            
            # Заполняем поля значениями из события
            st.session_state.edit_event_id = event_data['EventID']
            st.session_state.edit_asset_bundle = event_data['AssetBundlePath']
            st.session_state.edit_blocker = event_data['BlockerPrefabPath']
            st.session_state.edit_roundel = event_data['RoundelPrefabPath']
            st.session_state.edit_event_card = event_data['EventCardPrefabPath']
            st.session_state.edit_node_completion = event_data['NodeCompletionPrefabPath']
            st.session_state.edit_content_key = event_data['ContentKey']
            st.session_state.edit_min_level = event_data['MinLevel']
            st.session_state.edit_repeats = event_data['NumberOfRepeats']
            st.session_state.edit_segment = event_data['Segment']
            st.session_state.edit_time_warning = event_data['TimeWarning']
            st.session_state.edit_start_currency = event_data['StartingEventCurrency']
            st.session_state.edit_is_currency = event_data['IsCurrencyEvent']
            st.session_state.edit_entry_types = ', '.join(event_data.get('EntryTypes', []))
            
            st.success(f"✅ Событие загружено для редактирования. Перейдите на вкладку 'Настройка события'")
            st.rerun()
    with col_event3:
        if st.button(f"❌", key=f"del_event_{event_idx}", help=f"Удалить событие {event_data['EventID']}"):
            # Удаляем событие
            st.session_state.cfg["Events"].pop(event_idx)
            
            # Обновляем current_event_idx если нужно
            if len(st.session_state.cfg["Events"]) == 0:
                # Если событий не осталось
                st.session_state.current_event_idx = -1
                st.session_state.current_segment_name = ""
                st.session_state.creation_mode = "event"
            elif st.session_state.current_event_idx >= len(st.session_state.cfg["Events"]):
                # Если текущий индекс больше не существует
                st.session_state.current_event_idx = len(st.session_state.cfg["Events"]) - 1
            elif st.session_state.current_event_idx == event_idx:
                # Если удалили текущее выбранное событие
                if event_idx < len(st.session_state.cfg["Events"]):
                    # Если есть событие на том же индексе (после удаления сдвинулись)
                    st.session_state.current_event_idx = event_idx
                else:
                    # Если нет, берем последнее
                    st.session_state.current_event_idx = len(st.session_state.cfg["Events"]) - 1
            
            # Сбрасываем режимы редактирования
            st.session_state.is_editing = False
            st.session_state.is_editing_segment = False
            st.session_state.is_editing_node = False
            st.session_state.editing_event_data = None
            st.session_state.editing_segment_data = None
            st.session_state.editing_segment_name = None
            st.session_state.editing_node_data = None
            st.session_state.editing_node_type = None
            st.session_state.editing_node_index = -1
            st.session_state.force_expand_event = False
            st.session_state.force_expand_segment = False
            st.session_state.force_expand_node = False
            
            st.success(f"✅ Событие удалено")
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
                    # Сохраняем данные сегмента для редактирования
                    st.session_state.editing_segment_data = deepcopy(segment_data)
                    st.session_state.editing_segment_name = segment_name
                    st.session_state.editing_event_idx = event_idx
                    st.session_state.is_editing_segment = True
                    st.session_state.is_editing = False
                    st.session_state.is_editing_node = False
                    st.session_state.creation_mode = "segment"
                    st.session_state.force_expand_segment = True
                    
                    # Заполняем поля значениями из сегмента
                    st.session_state.edit_segment_name = segment_name
                    
                    # Получаем VIP диапазон
                    if isinstance(segment_data, dict):
                        segment_info = segment_data.get('PossibleSegmentInfo', {})
                        st.session_state.edit_vip_range = segment_info.get('VIPRange', '1-10+')
                    else:
                        st.session_state.edit_vip_range = '1-10+'
                    
                    # Загружаем ноды для возможного редактирования
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
                    
                    st.success(f"✅ Сегмент '{segment_name}' загружен для редактирования. Перейдите на вкладку 'Настройка события'")
                    st.rerun()
        
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
                    # Контейнер для ноды с кнопками
                    col_node1, col_node2, col_node3 = st.columns([3, 1, 1])
                    with col_node1:
                        st.write(f"         🔹 {node_type} (NodeID: {node_info.get('NodeID', 'N/A')}, NextNodeID: {node_info.get('NextNodeID', 'N/A')})")
                    with col_node2:
                        if st.button("✏️", key=f"edit_node_{event_idx}_{segment_name}_{stage_id}_{i}", help=f"Редактировать ноду {node_info.get('NodeID', 'N/A')}"):
                            # Загружаем данные ноды для редактирования
                            st.session_state.editing_node_data = deepcopy(node_data)
                            st.session_state.editing_node_type = node_type
                            st.session_state.editing_node_index = i
                            st.session_state.editing_node_stage_id = stage_id
                            st.session_state.editing_segment_name = segment_name
                            st.session_state.editing_event_idx = event_idx
                            st.session_state.is_editing_node = True
                            st.session_state.is_editing = False
                            st.session_state.is_editing_segment = False
                            st.session_state.creation_mode = "node"
                            st.session_state.force_expand_node = True
                            st.session_state.current_segment_name = segment_name
                            
                            # Устанавливаем выбранный тип ноды
                            st.session_state.selected_node_type = node_type
                            
                            # Загружаем данные ноды в зависимости от типа
                            if node_type == "ProgressNode":
                                # Загружаем данные Progress Node
                                st.session_state.edit_p_node_id = node_info.get('NodeID', 1)
                                st.session_state.edit_p_next_id = node_info.get('NextNodeID', [2])[0] if node_info.get('NextNodeID') else 2
                                st.session_state.edit_p_games = ', '.join(node_info.get('GameList', ['AllGames']))
                                st.session_state.edit_p_minigame = node_info.get('MiniGame', 'FlatReward')
                                st.session_state.edit_p_button_text = node_info.get('ButtonActionText', 'PLAY NOW!')
                                st.session_state.edit_p_button_type = node_info.get('ButtonActionType', '')
                                st.session_state.edit_p_button_data = node_info.get('ButtonActionData', '')
                                st.session_state.edit_p_is_last = node_info.get('IsLastNode', False)
                                st.session_state.edit_p_custom_texts = '\n'.join(node_info.get('CustomTexts', []))
                                st.session_state.edit_p_item_collect = node_info.get('PossibleItemCollect', '')
                                
                                # Загружаем MinBet
                                min_bet = node_info.get('MinBet', {})
                                if 'FixedMinBet' in min_bet:
                                    st.session_state.edit_p_minbet_type = "Fixed"
                                    st.session_state.edit_p_fixed = min_bet['FixedMinBet'].get('MinBet', 250000)
                                elif 'MinBetVariable' in min_bet:
                                    st.session_state.edit_p_minbet_type = "Variable"
                                    var_data = min_bet['MinBetVariable']
                                    st.session_state.edit_p_var = var_data.get('Variable', 0.8)
                                    st.session_state.edit_p_min = var_data.get('Min', 25000)
                                    st.session_state.edit_p_max = var_data.get('Max', 5000000)
                                
                                # Загружаем Goal
                                st.session_state.progress_goal = node_info.get('Goal', get_default_goal())
                                
                                # Загружаем Rewards
                                st.session_state.progress_rewards = node_info.get('Rewards', [get_default_reward()])
                                
                            elif node_type == "EntriesNode":
                                # Загружаем данные Entries Node
                                st.session_state.edit_e_node_id = node_info.get('NodeID', 1)
                                st.session_state.edit_e_game = ', '.join(node_info.get('GameList', ['AllGames']))
                                st.session_state.edit_e_goal = ', '.join(node_info.get('GoalType', ['Spins']))
                                st.session_state.edit_e_button_text = node_info.get('ButtonActionText', 'PLAY NOW!')
                                st.session_state.edit_e_button_type = node_info.get('ButtonActionType', '')
                                st.session_state.edit_e_button_data = node_info.get('ButtonActionData', '')
                                st.session_state.edit_e_entry_types = ', '.join(node_info.get('EntryTypes', ['MyEvent']))
                                st.session_state.edit_e_custom_texts = '\n'.join(node_info.get('CustomTexts', []))
                                st.session_state.edit_e_item_collect = node_info.get('PossibleItemCollect', 'Default')
                                
                                # Загружаем MinBet
                                min_bet = node_info.get('MinBet', {})
                                if 'FixedMinBet' in min_bet:
                                    st.session_state.edit_e_minbet_type = "Fixed"
                                    st.session_state.edit_e_fixed = min_bet['FixedMinBet'].get('MinBet', 250000)
                                elif 'MinBetVariable' in min_bet:
                                    st.session_state.edit_e_minbet_type = "Variable"
                                    var_data = min_bet['MinBetVariable']
                                    st.session_state.edit_e_var = var_data.get('Variable', 0.8)
                                    st.session_state.edit_e_min = var_data.get('Min', 25000)
                                    st.session_state.edit_e_max = var_data.get('Max', 5000000)
                            
                            elif node_type == "DummyNode":
                                # Загружаем данные Dummy Node
                                st.session_state.edit_d_node_id = node_info.get('NodeID', 1)
                                next_ids = node_info.get('NextNodeID', [11, 21, 31])
                                st.session_state.edit_d_next = ', '.join([str(id) for id in next_ids])
                                st.session_state.edit_d_button_text = node_info.get('ButtonActionText', 'PLAY NOW!')
                                st.session_state.edit_d_is_choice = node_info.get('IsChoiceEvent', True)
                                st.session_state.edit_d_custom_texts = '\n'.join(node_info.get('CustomTexts', []))
                                
                                # Загружаем Rewards
                                st.session_state.temp_rewards = node_info.get('Rewards', [])
                            
                            st.success(f"✅ Нода {node_info.get('NodeID', 'N/A')} загружена для редактирования")
                            st.rerun()
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
    
    with col2:
        # Определяем индекс для selectbox
        params_options = [
            "SpinpadGoal",
            "FixedGoal",
            "ConsecutiveWinsGoal",
            "TotalCoinsPerDay",
            "TotalCoinsPerDayWithSpinLimiter",
            "FixedGoalWithSpinLimiter"
        ]
        current_params = st.session_state[f"temp_goal_params_{unique_key}"]
        params_index = params_options.index(current_params) if current_params in params_options else 1
        
        goal_params_type = st.selectbox(
            "Параметры цели",
            options=params_options,
            index=params_index,
            key=f"{unique_key}_params_type"
        )
       
    goal_params = make_fixed_goal(20)  # Значение по умолчанию
    
    if goal_params_type == "SpinpadGoal":
        c1, c2, c3 = st.columns(3)
        with c1:
            multiplier = st.number_input(
                "Multiplier",
                value=st.session_state.get(f"{unique_key}_multiplier", 0.5),
                min_value=0.0,
                max_value=10.0,
                step=0.1,
                format="%.3f",
                key=f"{unique_key}_multiplier"
            )
        with c2:
            min_val = st.number_input(
                "Min",
                value=st.session_state.get(f"{unique_key}_min", 10),
                min_value=1,
                step=1,
                key=f"{unique_key}_min"
            )
        with c3:
            max_val = st.number_input(
                "Max",
                value=st.session_state.get(f"{unique_key}_max", 150),
                min_value=1,
                step=1,
                key=f"{unique_key}_max"
            )
        goal_params = make_spinpad_goal(float(multiplier), int(min_val), int(max_val))
    
    elif goal_params_type == "FixedGoal":
        target = st.number_input(
            "Target",
            value=st.session_state.get(f"{unique_key}_target", 20),
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
                value=st.session_state.get(f"{unique_key}_streaks", 3),
                min_value=1,
                step=1,
                key=f"{unique_key}_streaks"
            )
        with c2:
            multiplier = st.number_input(
                "Multiplier",
                value=st.session_state.get(f"{unique_key}_wins_multiplier", 0.01),
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
                value=st.session_state.get(f"{unique_key}_wins_min", 2),
                min_value=1,
                step=1,
                key=f"{unique_key}_wins_min"
            )
        with c4:
            max_val = st.number_input(
                "Max",
                value=st.session_state.get(f"{unique_key}_wins_max", 5),
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
                value=st.session_state.get(f"{unique_key}_tcpd_multiplier", 0.5),
                min_value=0.0,
                max_value=10.0,
                step=0.1,
                format="%.3f",
                key=f"{unique_key}_tcpd_multiplier"
            )
        with c2:
            min_val = st.number_input(
                "Min",
                value=st.session_state.get(f"{unique_key}_tcpd_min", 10),
                min_value=1,
                step=1,
                key=f"{unique_key}_tcpd_min"
            )
        with c3:
            max_val = st.number_input(
                "Max",
                value=st.session_state.get(f"{unique_key}_tcpd_max", 150),
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
                value=st.session_state.get(f"{unique_key}_spin_limiter", 3),
                min_value=1,
                step=1,
                key=f"{unique_key}_spin_limiter"
            )
            multiplier = st.number_input(
                "Multiplier",
                value=st.session_state.get(f"{unique_key}_tcpdwl_multiplier", 0.097),
                min_value=0.0,
                max_value=1.0,
                step=0.001,
                format="%.3f",
                key=f"{unique_key}_tcpdwl_multiplier"
            )
        with c2:
            min_val = st.number_input(
                "Min",
                value=st.session_state.get(f"{unique_key}_tcpdwl_min", 3500000),
                min_value=1,
                step=1000,
                key=f"{unique_key}_tcpdwl_min"
            )
            max_val = st.number_input(
                "Max",
                value=st.session_state.get(f"{unique_key}_tcpdwl_max", 50000000),
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
                value=st.session_state.get(f"{unique_key}_fgwl_target", 10),
                min_value=1,
                step=1,
                key=f"{unique_key}_fgwl_target"
            )
        with c2:
            spin_limiter = st.number_input(
                "Spin Limiter",
                value=st.session_state.get(f"{unique_key}_fgwl_spin_limiter", 3),
                min_value=1,
                step=1,
                key=f"{unique_key}_fgwl_spin_limiter"
            )
        goal_params = make_fixed_goal_with_spin_limiter_goal(int(target), int(spin_limiter))
    
    # Кнопка применения цели (только одна)
    apply_button = st.button("✅ Применить цель", key=f"{unique_key}_apply", use_container_width=True)
    
    # Всегда создаем текущую цель
    current_goal = make_goal(goal_type, goal_params)
    
    if apply_button:
        # Сохраняем текущие значения в session_state для последующего использования
        st.session_state[f"temp_goal_type_{unique_key}"] = goal_type
        st.session_state[f"temp_goal_params_{unique_key}"] = goal_params_type
        
        # Обновляем прогресс цель в session_state
        if prefix == "P":
            st.session_state.progress_goal = current_goal
            # Сохраняем текущие значения для отображения
            st.session_state.last_goal_type = goal_type
            st.session_state.last_goal_params = goal_params_type
        else:
            st.session_state[f"applied_goal_{unique_key}"] = current_goal
        
        # Принудительно обновляем интерфейс
        st.rerun()
    
    # Возвращаем примененную цель
    if prefix == "P":
        return st.session_state.progress_goal
    elif f"applied_goal_{unique_key}" in st.session_state:
        return st.session_state[f"applied_goal_{unique_key}"]
    
    return current_goal

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

def get_current_event_safe():
    """Безопасно возвращает текущее событие или None"""
    if (st.session_state.cfg["Events"] and 
        st.session_state.current_event_idx >= 0 and 
        st.session_state.current_event_idx < len(st.session_state.cfg["Events"])):
        return st.session_state.cfg["Events"][st.session_state.current_event_idx]["PossibleNodeEventData"]
    return None

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
    st.session_state.temp_rewards = []
if "temp_goal" not in st.session_state:
    st.session_state.temp_goal = get_default_goal()
if "last_node_tab" not in st.session_state:
    st.session_state.last_node_tab = None
if 'progress_rewards' not in st.session_state:
    st.session_state.progress_rewards = [get_default_reward()]
if 'progress_goal' not in st.session_state:
    st.session_state.progress_goal = get_default_goal()
if 'last_progress_reward_count' not in st.session_state:
    st.session_state.last_progress_reward_count = 0
if "current_segment_name" not in st.session_state:
    st.session_state.current_segment_name = ""

# Новые переменные для редактирования
if "editing_event_data" not in st.session_state:
    st.session_state.editing_event_data = None
if "is_editing" not in st.session_state:
    st.session_state.is_editing = False
if "force_expand_event" not in st.session_state:
    st.session_state.force_expand_event = False

# Переменные для редактирования сегментов
if "editing_segment_data" not in st.session_state:
    st.session_state.editing_segment_data = None
if "editing_segment_name" not in st.session_state:
    st.session_state.editing_segment_name = None
if "is_editing_segment" not in st.session_state:
    st.session_state.is_editing_segment = False
if "force_expand_segment" not in st.session_state:
    st.session_state.force_expand_segment = False
if "edit_segment_name" not in st.session_state:
    st.session_state.edit_segment_name = ""
if "edit_vip_range" not in st.session_state:
    st.session_state.edit_vip_range = ""

# Переменные для редактирования нод
if "editing_node_data" not in st.session_state:
    st.session_state.editing_node_data = None
if "editing_node_type" not in st.session_state:
    st.session_state.editing_node_type = None
if "editing_node_index" not in st.session_state:
    st.session_state.editing_node_index = -1
if "editing_node_stage_id" not in st.session_state:
    st.session_state.editing_node_stage_id = None
if "is_editing_node" not in st.session_state:
    st.session_state.is_editing_node = False
if "force_expand_node" not in st.session_state:
    st.session_state.force_expand_node = False

# Переменные для выбора типа ноды
if "last_node_type" not in st.session_state:
    st.session_state.last_node_type = None
if "selected_node_type" not in st.session_state:
    st.session_state.selected_node_type = "ProgressNode"


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
        if st.session_state.current_event_idx >= 0 and st.session_state.current_event_idx < len(st.session_state.cfg["Events"]):
            event_name = st.session_state.cfg["Events"][st.session_state.current_event_idx]["PossibleNodeEventData"]["EventID"]
            st.info(f"✏️ Текущее событие: {event_name}")
        else:
            # Если индекс невалидный, сбрасываем его
            if st.session_state.cfg["Events"]:
                st.session_state.current_event_idx = 0
                event_name = st.session_state.cfg["Events"][0]["PossibleNodeEventData"]["EventID"]
                st.info(f"✏️ Текущее событие: {event_name}")
            else:
                st.info("✏️ Нет текущего события")
                st.session_state.current_event_idx = -1
                st.session_state.current_segment_name = ""
    
    with col_status3:
        mode_text = "Редактирование события" if st.session_state.is_editing else \
                   "Редактирование сегмента" if st.session_state.is_editing_segment else \
                   "Редактирование ноды" if st.session_state.is_editing_node else \
                   "Создание"
        st.info(f"📌 Режим: {mode_text}")
    
    st.divider()
    
    colwww1, colwww2 =  st.columns(2)
    
    with colwww1:
        # ===== ШАГ 1: СОЗДАНИЕ СОБЫТИЯ =====
        # Определяем, должен ли expander быть развернут
        should_expand_event = (
            st.session_state.creation_mode == "event" or 
            st.session_state.is_editing or 
            st.session_state.force_expand_event
        )
        
        with st.expander("📋 ШАГ 1: Создание события", expanded=should_expand_event):
            # Сбрасываем флаг после использования
            if st.session_state.force_expand_event:
                st.session_state.force_expand_event = False
            
            if st.session_state.is_editing:
                st.write("✏️ **Редактирование события**")
                if st.session_state.editing_event_data:
                    st.info(f"Редактируется событие: {st.session_state.editing_event_data['EventID']}")
            else:
                st.write("Заполните общие параметры события и нажмите кнопку 'Добавить событие'")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Используем значения из session_state если есть редактирование
                default_event_id = st.session_state.get('edit_event_id', 'MyEvent')
                event_id = st.text_input("EventID", value=default_event_id, key="event_id")
                
                default_asset_bundle = st.session_state.get('edit_asset_bundle', '_events/MyEvent')
                asset_bundle = st.text_input("AssetBundlePath", value=default_asset_bundle, key="asset_bundle")
                
                default_blocker = st.session_state.get('edit_blocker', 'Dialogs/MyEvent_Dialog')
                blocker = st.text_input("BlockerPrefabPath", value=default_blocker, key="blocker")
                
                default_node_completion = st.session_state.get('edit_node_completion', 'Dialogs/MyEvent_Dialog')
                node_completion = st.text_input("NodeCompletionPrefabPath", value=default_node_completion, key="node_completion")
                
                default_event_card = st.session_state.get('edit_event_card', '')
                event_card = st.text_input("EventCardPrefabPath", value=default_event_card, key="event_card")
            
            with col2:
                default_roundel = st.session_state.get('edit_roundel', 'Roundels/MyEvent_Roundel')
                roundel = st.text_input("RoundelPrefabPath", value=default_roundel, key="roundel")
                
                default_content_key = st.session_state.get('edit_content_key', 'MyEvent')
                content_key = st.text_input("ContentKey", value=default_content_key, key="content_key")
                
                default_min_level = st.session_state.get('edit_min_level', 1)
                min_level = st.number_input("MinLevel", min_value=1, value=int(default_min_level), step=1, key="min_level")
                
                default_repeats = st.session_state.get('edit_repeats', -1)
                repeats = st.number_input("NumberOfRepeats", value=int(default_repeats), step=1, key="repeats")
                
                default_segment = st.session_state.get('edit_segment', 'Default')
                segment = st.text_input("Segment (основной сегмент)", value=default_segment, key="segment")
            
            col3, col4 = st.columns(2)
            with col3:
                default_time_warning = st.session_state.get('edit_time_warning', '2026-02-21T16:00:00Z')
                time_warning = st.text_input("TimeWarning (ISO)", value=default_time_warning, key="time_warning")
                
                default_start_currency = st.session_state.get('edit_start_currency', 0.0)
                start_currency = st.number_input("StartingEventCurrency", value=float(default_start_currency), key="start_currency")
            
            with col4:
                default_is_currency = st.session_state.get('edit_is_currency', False)
                is_currency_event = st.checkbox("IsCurrencyEvent", value=bool(default_is_currency), key="is_currency")
                
                default_entry_types = st.session_state.get('edit_entry_types', '')
                entry_types = st.text_input("EntryTypes (через запятую)", value=default_entry_types, key="event_entry_types")
            
            # Кнопка добавления/сохранения события
            if st.session_state.is_editing:
                button_text = "💾 СОХРАНИТЬ ИЗМЕНЕНИЯ"
                button_type = "primary"
            else:
                button_text = "➕ ДОБАВИТЬ СОБЫТИЕ"
                button_type = "primary"
            
            if st.button(button_text, use_container_width=True, type=button_type):
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
                
                if st.session_state.is_editing:
                    # Обновляем существующее событие
                    st.session_state.cfg["Events"][st.session_state.editing_event_idx] = ev
                    st.session_state.is_editing = False
                    st.session_state.editing_event_data = None
                    st.session_state.creation_mode = "event"
                    st.success(f"✅ Событие {event_id} обновлено!")
                else:
                    # Добавляем новое событие
                    st.session_state.cfg["Events"].append(ev)
                    st.session_state.current_event_idx = len(st.session_state.cfg["Events"]) - 1
                    st.session_state.creation_mode = "segment"
                    st.success(f"✅ Событие {event_id} добавлено! Теперь можно добавлять сегменты")
                
                # Очищаем временные данные редактирования
                for key in list(st.session_state.keys()):
                    if key.startswith('edit_'):
                        del st.session_state[key]
                
                st.rerun()
        
        # ===== ШАГ 2: СОЗДАНИЕ СЕГМЕНТА =====
        if st.session_state.cfg["Events"] and st.session_state.current_event_idx >= 0 and st.session_state.current_event_idx < len(st.session_state.cfg["Events"]):
            # Определяем, должен ли expander для сегмента быть развернут
            should_expand_segment = (
                st.session_state.creation_mode == "segment" or
                st.session_state.is_editing_segment or
                st.session_state.force_expand_segment
            )
            
            with st.expander("📁 ШАГ 2: Создание сегмента", expanded=should_expand_segment):
                # Сбрасываем флаг после использования
                if st.session_state.force_expand_segment:
                    st.session_state.force_expand_segment = False
                
                current_event = st.session_state.cfg["Events"][st.session_state.current_event_idx]["PossibleNodeEventData"]
                
                if st.session_state.is_editing_segment:
                    st.write(f"✏️ **Редактирование сегмента:** {st.session_state.editing_segment_name}")
                    st.info(f"Событие: {current_event['EventID']}")
                else:
                    st.write("Заполните параметры сегмента и нажмите кнопку 'Добавить сегмент'")
                    st.info(f"📦 Текущее событие: {current_event['EventID']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    # Определяем значение по умолчанию для имени сегмента
                    if st.session_state.is_editing_segment:
                        # Если редактируем, берем из edit_segment_name
                        default_segment_name = st.session_state.get('edit_segment_name', 'VIP1_10')
                    elif st.session_state.get('edit_segment_name'):
                        # Если есть временные данные (например, после неудачного сохранения)
                        default_segment_name = st.session_state.edit_segment_name
                    else:
                        # Иначе стандартное значение
                        default_segment_name = 'VIP1_10'
                    
                    segment_name = st.text_input(
                        "Имя сегмента", 
                        value=default_segment_name, 
                        key="segment_name_edit" if st.session_state.is_editing_segment else "segment_name"
                    )
                
                with col2:
                    # Определяем значение по умолчанию для VIP диапазона
                    if st.session_state.is_editing_segment:
                        # Если редактируем, берем из edit_vip_range
                        default_vip_range = st.session_state.get('edit_vip_range', '1-10+')
                    elif st.session_state.get('edit_vip_range'):
                        # Если есть временные данные
                        default_vip_range = st.session_state.edit_vip_range
                    else:
                        # Иначе стандартное значение
                        default_vip_range = '1-10+'
                    
                    vip_range = st.text_input(
                        "VIP Range", 
                        value=default_vip_range, 
                        key="vip_range_edit" if st.session_state.is_editing_segment else "vip_range"
                    )
                
                # Кнопка добавления/сохранения сегмента
                if st.session_state.is_editing_segment:
                    button_text = "💾 СОХРАНИТЬ ИЗМЕНЕНИЯ СЕГМЕНТА"
                    button_type = "primary"
                else:
                    button_text = "➕ ДОБАВИТЬ СЕГМЕНТ"
                    button_type = "primary"
                
                if st.button(button_text, use_container_width=True, type=button_type):
                    if st.session_state.is_editing_segment:
                        # Обновляем существующий сегмент
                        if segment_name != st.session_state.editing_segment_name and segment_name in current_event["Segments"]:
                            st.error(f"❌ Сегмент {segment_name} уже существует!")
                        else:
                            # Получаем текущие данные сегмента
                            old_segment_name = st.session_state.editing_segment_name
                            old_segment_data = current_event["Segments"][old_segment_name]
                            
                            # Если имя изменилось, удаляем старый и создаем новый
                            if segment_name != old_segment_name:
                                # Сохраняем Stages из старого сегмента
                                stages = old_segment_data.get('Stages', []) if isinstance(old_segment_data, dict) else []
                                
                                # Создаем новый сегмент с обновленным именем
                                new_segment = make_segment(segment_name, vip_range)
                                
                                # Копируем Stages из старого сегмента
                                if stages:
                                    if isinstance(new_segment[segment_name], dict):
                                        new_segment[segment_name]['Stages'] = stages
                                
                                # Удаляем старый сегмент
                                del current_event["Segments"][old_segment_name]
                                # Добавляем новый
                                current_event["Segments"].update(new_segment)
                            else:
                                # Обновляем VIP диапазон существующего сегмента
                                if isinstance(old_segment_data, dict):
                                    if 'PossibleSegmentInfo' not in old_segment_data:
                                        old_segment_data['PossibleSegmentInfo'] = {}
                                    old_segment_data['PossibleSegmentInfo']['VIPRange'] = vip_range
                            
                            st.session_state.current_segment_name = segment_name
                            st.session_state.is_editing_segment = False
                            st.session_state.editing_segment_data = None
                            st.session_state.editing_segment_name = None
                            st.session_state.creation_mode = "node"
                            
                            st.success(f"✅ Сегмент {segment_name} обновлен! Теперь можно добавлять/редактировать ноды")
                            
                            # Очищаем временные данные редактирования
                            for key in list(st.session_state.keys()):
                                if key.startswith('edit_segment_') or key in ['edit_segment_name', 'edit_vip_range']:
                                    del st.session_state[key]
                            
                            st.rerun()
                    else:
                        # Добавляем новый сегмент
                        if segment_name in current_event["Segments"]:
                            st.error(f"❌ Сегмент {segment_name} уже существует!")
                        else:
                            # Создаем сегмент
                            new_segment = make_segment(segment_name, vip_range)
                            current_event["Segments"].update(new_segment)
                            st.session_state.current_segment_name = segment_name
                            st.session_state.creation_mode = "node"
                            st.success(f"✅ Сегмент {segment_name} добавлен! Теперь можно добавлять ноды")
                            st.rerun()
        
        # ===== ШАГ 3: СОЗДАНИЕ НОДЫ =====
        if (st.session_state.cfg["Events"] and st.session_state.current_event_idx >= 0 and 
            st.session_state.current_event_idx < len(st.session_state.cfg["Events"]) and
            st.session_state.current_segment_name):
            
            current_event = st.session_state.cfg["Events"][st.session_state.current_event_idx]["PossibleNodeEventData"]
            
            if st.session_state.current_segment_name in current_event["Segments"]:
                # Определяем, должен ли expander для ноды быть развернут
                should_expand_node = (
                    st.session_state.creation_mode == "node" or
                    st.session_state.is_editing_node or
                    st.session_state.force_expand_node
                )
                
                with st.expander("🔧 ШАГ 3: Создание ноды", expanded=should_expand_node):
                    # Сбрасываем флаг после использования
                    if st.session_state.force_expand_node:
                        st.session_state.force_expand_node = False
                    
                    if st.session_state.is_editing_node:
                        st.write(f"✏️ **Редактирование ноды** (Тип: {st.session_state.editing_node_type})")
                        st.info(f"Сегмент: {st.session_state.current_segment_name}, Событие: {current_event['EventID']}")
                    else:
                        st.write(f"Добавление ноды в сегмент: **{st.session_state.current_segment_name}**")

                    # Определяем текущий выбранный тип
                    if st.session_state.is_editing_node and st.session_state.editing_node_type:
                        # При редактировании используем тип редактируемой ноды
                        default_node_type = st.session_state.editing_node_type
                    elif st.session_state.get('selected_node_type'):
                        # Если есть сохраненный выбор
                        default_node_type = st.session_state.selected_node_type
                    else:
                        # По умолчанию ProgressNode
                        default_node_type = 'ProgressNode'

                    # Создаем индекс для radio
                    type_index = 0
                    if default_node_type == "ProgressNode":
                        type_index = 0
                    elif default_node_type == "EntriesNode":
                        type_index = 1
                    elif default_node_type == "DummyNode":
                        type_index = 2

                    # Добавим уникальный ключ для radio, который меняется при редактировании
                    radio_key = f"node_type_selector_{st.session_state.is_editing_node}_{st.session_state.editing_node_index}"

                    node_type = st.radio(
                        "Тип ноды",
                        options=["ProgressNode", "EntriesNode", "DummyNode"],
                        index=type_index,
                        horizontal=True,
                        key=radio_key,
                        label_visibility="collapsed"
                    )

                    # Сохраняем выбранный тип в session_state
                    st.session_state.selected_node_type = node_type

                    # Если мы в режиме редактирования, но выбранный тип не совпадает с типом редактируемой ноды,
                    # обновляем данные для нового типа
                    if st.session_state.is_editing_node and node_type != st.session_state.editing_node_type:
                        st.warning(f"⚠️ Вы изменили тип ноды с {st.session_state.editing_node_type} на {node_type}. Данные будут сброшены.")
                        # Здесь можно добавить логику для сброса данных при смене типа

                    # Сброс данных при переключении типа ноды (только если не в режиме редактирования)
                    if not st.session_state.is_editing_node:
                        if st.session_state.last_node_type != node_type:
                            if node_type == "ProgressNode":
                                st.session_state.progress_goal = get_default_goal()
                                st.session_state.progress_rewards = [get_default_reward()]
                            elif node_type == "DummyNode":
                                # Не нужно инициализировать temp_rewards, так как награда фиксирована
                                pass
                            st.session_state.last_node_type = node_type
                    
                    # Progress Node
                    if node_type == "ProgressNode":
                        st.subheader("📊 Progress Node")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            default_p_node_id = st.session_state.get('edit_p_node_id', 1)
                            node_id = st.number_input("NodeID", min_value=1, value=int(default_p_node_id), step=1, key="p_node_id_edit" if st.session_state.is_editing_node else "p_node_id")
                            
                            default_p_next_id = st.session_state.get('edit_p_next_id', 2)
                            next_id = st.number_input("NextNodeID", min_value=1, value=int(default_p_next_id), step=1, key="p_next_id_edit" if st.session_state.is_editing_node else "p_next_id")
                            
                            default_p_games = st.session_state.get('edit_p_games', 'AllGames')
                            games = st.text_input("GameList (через запятую)", value=default_p_games, key="p_games_edit" if st.session_state.is_editing_node else "p_games")
                            
                            default_p_minigame = st.session_state.get('edit_p_minigame', 'FlatReward')
                            minigame = st.text_input("MiniGame", value=default_p_minigame, key="minigame_edit" if st.session_state.is_editing_node else "minigame")
                        
                        with col2:
                            default_p_button_text = st.session_state.get('edit_p_button_text', 'PLAY NOW!')
                            button_text = st.text_input("ButtonActionText", value=default_p_button_text, key="btn_1_edit" if st.session_state.is_editing_node else "btn_1")
                            
                            default_p_button_type = st.session_state.get('edit_p_button_type', '')
                            button_type = st.text_input("ButtonActionType", value=default_p_button_type, key="btn_2_edit" if st.session_state.is_editing_node else "btn_2")
                            
                            default_p_button_data = st.session_state.get('edit_p_button_data', '')
                            button_data = st.text_input("ButtonActionData", value=default_p_button_data, key="btn_3_edit" if st.session_state.is_editing_node else "btn_3")
                            
                            default_p_is_last = st.session_state.get('edit_p_is_last', False)
                            is_last_node = st.checkbox("IsLastNode", value=bool(default_p_is_last), key="is_last_edit" if st.session_state.is_editing_node else "is_last")
                        
                        # MinBet выбор
                        min_bet_prefix = "P_edit" if st.session_state.is_editing_node else "P"
                        default_minbet_type = st.session_state.get('edit_p_minbet_type', 'Fixed')
                        
                        st.write("**Тип MinBet:**")
                        minbet_type = st.radio(
                            "Выберите тип",
                            options=["Fixed", "Variable"],
                            index=0 if default_minbet_type == "Fixed" else 1,
                            key=f"{min_bet_prefix}_minbet_type",
                            horizontal=True,
                            label_visibility="collapsed"
                        )
                        
                        if minbet_type == "Variable":
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                default_var = st.session_state.get('edit_p_var', 0.8)
                                var = st.number_input(
                                    f"Variable", 
                                    value=float(default_var), 
                                    min_value=0.0, 
                                    max_value=10.0, 
                                    step=0.1,
                                    format="%.2f",
                                    key=f"{min_bet_prefix}_var"
                                )
                            with col2:
                                default_min = st.session_state.get('edit_p_min', 25000.0)
                                min_v = st.number_input(
                                    f"Min", 
                                    value=float(default_min), 
                                    min_value=0.0, 
                                    step=1000.0,
                                    format="%.2f",
                                    key=f"{min_bet_prefix}_min"
                                )
                            with col3:
                                default_max = st.session_state.get('edit_p_max', 5000000.0)
                                max_v = st.number_input(
                                    f"Max", 
                                    value=float(default_max), 
                                    min_value=0.0, 
                                    step=10000.0,
                                    format="%.2f",
                                    key=f"{min_bet_prefix}_max"
                                )
                            min_bet = make_minbet_variable(float(var), float(min_v), float(max_v))
                        else:
                            col1, _ = st.columns([1, 2])
                            with col1:
                                default_fixed = st.session_state.get('edit_p_fixed', 250000.0)
                                fixed_value = st.number_input(
                                    f"Fixed MinBet", 
                                    value=float(default_fixed), 
                                    min_value=0.0, 
                                    step=10000.0,
                                    format="%.2f",
                                    key=f"{min_bet_prefix}_fixed"
                                )
                            min_bet = make_fixed_minbet(float(fixed_value))

                        st.write("**Цель:**")

                        # Отображение текущей цели
                        if st.session_state.progress_goal is not None:
                            goal = st.session_state.progress_goal
                            goal_types = goal.get('Type', [])
                            goal_type_str = ', '.join(goal_types) if goal_types else "No Type"
                            
                            # Определяем тип параметров цели из структуры goal
                            goal_params_type = "Unknown"
                            if goal:
                                # Ищем ключ, который не равен "Type"
                                for key in goal.keys():
                                    if key != "Type":
                                        goal_params_type = key
                                        break
                            
                            # Используем сохраненные значения из session_state если они есть
                            display_goal_type = st.session_state.get('last_goal_type', goal_type_str)
                            display_goal_params = st.session_state.get('last_goal_params', goal_params_type)
                            
                            if st.session_state.is_editing_node:
                                st.success(f"✅ Текущая цель: {display_goal_type} с параметрами {display_goal_params}")
                            else:
                                st.success(f"✅ Текущая цель: {display_goal_type} с параметрами {display_goal_params}")
                            
                            new_goal = goal_creator_block("P", goal_index=0, key_suffix=f"progress_edit" if st.session_state.is_editing_node else "progress")
                            # Всегда обновляем цель, даже если она не None
                            if new_goal is not None:
                                st.session_state.progress_goal = new_goal

                        st.write("**Награды:**")
                        
                        # Отображение текущих наград
                        if st.session_state.progress_rewards:
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
                                    if st.button("✏️", key=f"edit_reward_progress_{j}_edit" if st.session_state.is_editing_node else f"edit_reward_progress_{j}"):
                                        st.info("Редактирование будет доступно позже")
                                with colr3:
                                    if st.button("❌", key=f"remove_reward_progress_{j}_edit" if st.session_state.is_editing_node else f"remove_reward_progress_{j}"):
                                        st.session_state.progress_rewards.pop(j)
                                        st.rerun()
                        else:
                            st.info("📭 Награды не добавлены")
                            if not st.session_state.is_editing_node:
                                st.session_state.progress_rewards = [get_default_reward()]
                                st.rerun()
                        
                        # Добавление новой награды
                        with st.expander("➕ Добавить дополнительную награду"):
                            new_reward = reward_creator_block("P", reward_index=f"progress_extra_edit" if st.session_state.is_editing_node else "progress_extra")
                            col_button, _ = st.columns([1, 3])                           
                            if st.button("➕ Добавить эту награду в список", key="add_reward_progress_extra_edit" if st.session_state.is_editing_node else "add_reward_progress_extra"):
                                if new_reward:
                                    st.session_state.progress_rewards.append(new_reward)
                                    st.rerun()
                        
                        default_p_custom_texts = st.session_state.get('edit_p_custom_texts', 'SPIN\n##\nTIMES')
                        custom_texts = st.text_area(
                            "CustomTexts (каждая строка - отдельный текст)", 
                            value=default_p_custom_texts, 
                            height=None,
                            key="p_ct_edit" if st.session_state.is_editing_node else "p_ct",
                            help="Вводите каждый текст с новой строки"
                        )
                        
                        default_p_item_collect = st.session_state.get('edit_p_item_collect', 'Default')
                        item_collect = st.text_input("PossibleItemCollect", value=default_p_item_collect, key="p_ic_edit" if st.session_state.is_editing_node else "p_ic")
                        
                        # Кнопка добавления/сохранения ноды
                        if st.session_state.is_editing_node and st.session_state.editing_node_type == "ProgressNode":
                            button_text_node = "💾 СОХРАНИТЬ ИЗМЕНЕНИЯ PROGRESS NODE"
                        else:
                            button_text_node = "➕ ДОБАВИТЬ PROGRESS NODE"
                        
                        if st.button(button_text_node, key="add_progress_edit" if st.session_state.is_editing_node else "add_progress", use_container_width=True, type="primary"):
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
                                possible_item_collect=item_collect.strip() or "Default",
                            )
                            
                            if st.session_state.is_editing_node and st.session_state.editing_node_type == "ProgressNode":
                                # Обновляем существующую ноду
                                segment_data = current_event["Segments"][st.session_state.current_segment_name]
                                if segment_data["Stages"]:
                                    nodes_list = segment_data["Stages"][0]["Nodes"]
                                    nodes_list[st.session_state.editing_node_index] = node
                                    
                                st.session_state.is_editing_node = False
                                st.session_state.editing_node_data = None
                                st.session_state.editing_node_type = None
                                st.session_state.editing_node_index = -1
                                st.session_state.creation_mode = "node"
                                
                                st.success(f"✅ Progress Node (ID: {node_id}) обновлена в сегменте {st.session_state.current_segment_name}")
                            else:
                                # Добавляем новую ноду в сегмент
                                segment_data = current_event["Segments"][st.session_state.current_segment_name]
                                if segment_data["Stages"]:
                                    segment_data["Stages"][0]["Nodes"].append(node)
                                else:
                                    segment_data["Stages"] = [make_stage(1, [node])]
                                
                                # Сбрасываем для следующей ноды
                                st.session_state.progress_rewards = [get_default_reward()]
                                st.session_state.progress_goal = get_default_goal()
                                
                                st.success(f"✅ Progress Node (ID: {node_id}) добавлена в сегмент {st.session_state.current_segment_name}")
                            
                            # Очищаем временные данные редактирования
                            for key in list(st.session_state.keys()):
                                if key.startswith('edit_p_'):
                                    del st.session_state[key]
                            
                            st.rerun()
                    
                    # Entries Node
                    elif node_type == "EntriesNode":
                        st.subheader("🚪 Entries Node")
                        
                        default_e_game = st.session_state.get('edit_e_game', 'AllGames')
                        game_name = st.text_input("GameList (через запятую)", value=default_e_game, key="e_game_edit" if st.session_state.is_editing_node else "e_game")

                        default_e_goal = st.session_state.get('edit_e_goal', 'Spins')
                        goal_type = st.text_input("GoalType", value=default_e_goal, key="e_goal_edit" if st.session_state.is_editing_node else "e_goal")
                        
                        default_e_button_text = st.session_state.get('edit_e_button_text', 'PLAY NOW!')
                        button_text = st.text_input("ButtonActionText", value=default_e_button_text, key="btn_11_edit" if st.session_state.is_editing_node else "btn_11")
                        
                        default_e_button_type = st.session_state.get('edit_e_button_type', '')
                        button_type = st.text_input("ButtonActionType", value=default_e_button_type, key="btn_12_edit" if st.session_state.is_editing_node else "btn_12")
                        
                        default_e_button_data = st.session_state.get('edit_e_button_data', '')
                        button_data = st.text_input("ButtonActionData", value=default_e_button_data, key="btn_13_edit" if st.session_state.is_editing_node else "btn_13")
                        
                        default_e_entry_types = st.session_state.get('edit_e_entry_types', 'MyEvent')
                        entry_types_raw = st.text_input("EntryTypes (через запятую)", value=default_e_entry_types, key="e_entry_types_edit" if st.session_state.is_editing_node else "e_entry_types")
                        
                        # MinBet выбор
                        min_bet_prefix = "E_edit" if st.session_state.is_editing_node else "E"
                        default_minbet_type = st.session_state.get('edit_e_minbet_type', 'Fixed')
                        
                        st.write("**Тип MinBet:**")
                        minbet_type = st.radio(
                            "Выберите тип",
                            options=["Fixed", "Variable"],
                            index=0 if default_minbet_type == "Fixed" else 1,
                            key=f"{min_bet_prefix}_minbet_type",
                            horizontal=True,
                            label_visibility="collapsed"
                        )
                        
                        if minbet_type == "Variable":
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                default_var = st.session_state.get('edit_e_var', 0.8)
                                var = st.number_input(
                                    f"Variable", 
                                    value=float(default_var), 
                                    min_value=0.0, 
                                    max_value=10.0, 
                                    step=0.1,
                                    format="%.2f",
                                    key=f"{min_bet_prefix}_var"
                                )
                            with col2:
                                default_min = st.session_state.get('edit_e_min', 25000.0)
                                min_v = st.number_input(
                                    f"Min", 
                                    value=float(default_min), 
                                    min_value=0.0, 
                                    step=1000.0,
                                    format="%.2f",
                                    key=f"{min_bet_prefix}_min"
                                )
                            with col3:
                                default_max = st.session_state.get('edit_e_max', 5000000.0)
                                max_v = st.number_input(
                                    f"Max", 
                                    value=float(default_max), 
                                    min_value=0.0, 
                                    step=10000.0,
                                    format="%.2f",
                                    key=f"{min_bet_prefix}_max"
                                )
                            min_bet = make_minbet_variable(float(var), float(min_v), float(max_v))
                        else:
                            col1, _ = st.columns([1, 2])
                            with col1:
                                default_fixed = st.session_state.get('edit_e_fixed', 250000.0)
                                fixed_value = st.number_input(
                                    f"Fixed MinBet", 
                                    value=float(default_fixed), 
                                    min_value=0.0, 
                                    step=10000.0,
                                    format="%.2f",
                                    key=f"{min_bet_prefix}_fixed"
                                )
                            min_bet = make_fixed_minbet(float(fixed_value))
                        
                        default_e_custom_texts = st.session_state.get('edit_e_custom_texts', '')
                        custom_texts = st.text_area(
                            "CustomTexts (каждая строка - отдельный текст)", 
                            value=default_e_custom_texts, 
                            height=None,
                            key="e_ct_edit" if st.session_state.is_editing_node else "e_ct",
                            help="Вводите каждый текст с новой строки"
                        )
                        
                        default_e_item_collect = st.session_state.get('edit_e_item_collect', 'Default')
                        item_collect = st.text_input("PossibleItemCollect", value=default_e_item_collect, key="e_ic_edit" if st.session_state.is_editing_node else "e_ic")
                        
                        # Кнопка добавления/сохранения ноды
                        if st.session_state.is_editing_node and st.session_state.editing_node_type == "EntriesNode":
                            button_text_node = "💾 СОХРАНИТЬ ИЗМЕНЕНИЯ ENTRIES NODE"
                        else:
                            button_text_node = "➕ ДОБАВИТЬ ENTRIES NODE"
                        
                        if st.button(button_text_node, key="add_entries_edit" if st.session_state.is_editing_node else "add_entries", use_container_width=True, type="primary"):
                            node = make_entries_node(
                                node_id=1,  # Фиксированное значение 1
                                game_list=[x.strip() for x in game_name.split(",") if x.strip()],
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
                            
                            if st.session_state.is_editing_node and st.session_state.editing_node_type == "EntriesNode":
                                # Обновляем существующую ноду
                                segment_data = current_event["Segments"][st.session_state.current_segment_name]
                                if segment_data["Stages"]:
                                    nodes_list = segment_data["Stages"][0]["Nodes"]
                                    nodes_list[st.session_state.editing_node_index] = node
                                    
                                st.session_state.is_editing_node = False
                                st.session_state.editing_node_data = None
                                st.session_state.editing_node_type = None
                                st.session_state.editing_node_index = -1
                                st.session_state.creation_mode = "node"
                                
                                st.success(f"✅ Entries Node обновлена в сегменте {st.session_state.current_segment_name}")  # Убрали ID из сообщения
                            else:
                                # Добавляем новую ноду в сегмент
                                segment_data = current_event["Segments"][st.session_state.current_segment_name]
                                if segment_data["Stages"]:
                                    segment_data["Stages"][0]["Nodes"].append(node)
                                else:
                                    segment_data["Stages"] = [make_stage(1, [node])]
                                
                                st.success(f"✅ Entries Node добавлена в сегмент {st.session_state.current_segment_name}")  # Убрали ID из сообщения
                            
                            # Очищаем временные данные редактирования
                            for key in list(st.session_state.keys()):
                                if key.startswith('edit_e_'):
                                    del st.session_state[key]
                            
                            st.rerun()
                    
                    # Dummy Choice Node
                    elif node_type == "DummyNode":
                        st.subheader("🎲 Dummy Choice Node")
                        
                        default_d_node_id = st.session_state.get('edit_d_node_id', 1)
                        node_id = st.number_input("NodeID", min_value=1, value=int(default_d_node_id), step=1, key="d_node_id_edit" if st.session_state.is_editing_node else "d_node_id")
                        
                        default_d_next = st.session_state.get('edit_d_next', '11,21,31')
                        next_ids_raw = st.text_input("NextNodeID (через запятую)", value=default_d_next, key="d_next_edit" if st.session_state.is_editing_node else "d_next")
                        
                        default_d_custom_texts = st.session_state.get('edit_d_custom_texts', '')
                        custom_texts = st.text_area(
                            "CustomTexts (каждая строка - отдельный текст)", 
                            value=default_d_custom_texts, 
                            height=None,
                            key="d_ct_edit" if st.session_state.is_editing_node else "d_ct",
                            help="Вводите каждый текст с новой строки"
                        )
                        
                        # Кнопка добавления/сохранения ноды
                        if st.session_state.is_editing_node and st.session_state.editing_node_type == "DummyNode":
                            button_text_node = "💾 СОХРАНИТЬ ИЗМЕНЕНИЯ DUMMY NODE"
                        else:
                            button_text_node = "➕ ДОБАВИТЬ DUMMY NODE"
                        
                        if st.button(button_text_node, key="add_dummy_edit" if st.session_state.is_editing_node else "add_dummy", use_container_width=True, type="primary"):
                            # Всегда используем фиксированную награду
                            rewards = [fixed_reward]
                            
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
                                rewards=rewards,
                                is_last=False,
                                resegment=False,
                                mini_game="FlatReward",
                                contribution_level="Node",
                                button_action_type="",
                                button_action_data="",
                                button_action_text="",
                                custom_texts=process_multiline_custom_texts(custom_texts),
                                is_choice_event=True,
                            )
                            
                            if st.session_state.is_editing_node and st.session_state.editing_node_type == "DummyNode":
                                # Обновляем существующую ноду
                                segment_data = current_event["Segments"][st.session_state.current_segment_name]
                                if segment_data["Stages"]:
                                    nodes_list = segment_data["Stages"][0]["Nodes"]
                                    nodes_list[st.session_state.editing_node_index] = node
                                    
                                st.session_state.is_editing_node = False
                                st.session_state.editing_node_data = None
                                st.session_state.editing_node_type = None
                                st.session_state.editing_node_index = -1
                                st.session_state.creation_mode = "node"
                                
                                st.success(f"✅ Dummy Node (ID: {node_id}) обновлена в сегменте {st.session_state.current_segment_name}")
                            else:
                                # Добавляем новую ноду в сегмент
                                segment_data = current_event["Segments"][st.session_state.current_segment_name]
                                if segment_data["Stages"]:
                                    segment_data["Stages"][0]["Nodes"].append(node)
                                else:
                                    segment_data["Stages"] = [make_stage(1, [node])]
                                
                                st.success(f"✅ Dummy Node (ID: {node_id}) добавлена в сегмент {st.session_state.current_segment_name}")
                            
                            # Очищаем временные данные редактирования
                            for key in list(st.session_state.keys()):
                                if key.startswith('edit_d_'):
                                    del st.session_state[key]
                            
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
                st.session_state.is_editing = False
                st.session_state.is_editing_segment = False
                st.session_state.is_editing_node = False
                st.session_state.editing_event_data = None
                st.session_state.editing_segment_data = None
                st.session_state.editing_segment_name = None
                st.session_state.editing_node_data = None
                st.session_state.editing_node_type = None
                st.session_state.editing_node_index = -1
                st.session_state.force_expand_event = False
                st.session_state.force_expand_segment = False
                st.session_state.force_expand_node = False
                # Очищаем временные данные редактирования
                for key in list(st.session_state.keys()):
                    if key.startswith('edit_'):
                        del st.session_state[key]
                st.rerun()
        
        with col_reset2:
            if st.button("➕ Добавить еще сегмент", use_container_width=True):
                if st.session_state.current_event_idx >= 0:
                    # Если были в режиме редактирования сегмента, выходим из него
                    st.session_state.is_editing_segment = False
                    st.session_state.editing_segment_data = None
                    st.session_state.editing_segment_name = None
                    st.session_state.creation_mode = "segment"
                    st.rerun()
        
        # Кнопка отмены редактирования (если в режиме редактирования)
        if st.session_state.is_editing:
            if st.button("❌ Отменить редактирование события", use_container_width=True):
                st.session_state.is_editing = False
                st.session_state.editing_event_data = None
                st.session_state.creation_mode = "event"
                st.session_state.force_expand_event = False
                # Очищаем временные данные редактирования
                for key in list(st.session_state.keys()):
                    if key.startswith('edit_'):
                        del st.session_state[key]
                st.rerun()
        
        # Кнопка отмены редактирования сегмента (если в режиме редактирования)
        if st.session_state.is_editing_segment:
            if st.button("❌ Отменить редактирование сегмента", use_container_width=True):
                st.session_state.is_editing_segment = False
                st.session_state.editing_segment_data = None
                st.session_state.editing_segment_name = None
                st.session_state.creation_mode = "event"
                st.session_state.force_expand_segment = False
                # Очищаем временные данные редактирования
                for key in list(st.session_state.keys()):
                    if key.startswith('edit_segment_') or key in ['edit_segment_name', 'edit_vip_range']:
                        del st.session_state[key]
                st.rerun()
        
        # Кнопка отмены редактирования ноды (если в режиме редактирования)
        if st.session_state.is_editing_node:
            if st.button("❌ Отменить редактирование ноды", use_container_width=True):
                st.session_state.is_editing_node = False
                st.session_state.editing_node_data = None
                st.session_state.editing_node_type = None
                st.session_state.editing_node_index = -1
                st.session_state.creation_mode = "event"
                st.session_state.force_expand_node = False
                # Сбрасываем временные данные
                st.session_state.progress_rewards = [get_default_reward()]
                st.session_state.progress_goal = get_default_goal()
                st.session_state.temp_rewards = []
                # Очищаем временные данные редактирования
                for key in list(st.session_state.keys()):
                    if key.startswith('edit_'):
                        del st.session_state[key]
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