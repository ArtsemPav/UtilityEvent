# ui/widgets/node_editor.py
import streamlit as st
from typing import Optional, Union
from models.nodes import ProgressNode, EntriesNode, DummyNode, Node
from models.rewards import Reward, FixedReward
from .minbet_widget import render_minbet_widget
from .goal_widget import render_goal_widget
from .reward_widget import render_reward_widget
from utils.helpers import parse_comma_separated_list, process_multiline_text


def get_default_reward() -> Reward:
    """Возвращает стандартную награду (2500000 чипов)."""
    return Reward(data=FixedReward(currency="Chips", amount=2500000.0))


def render_rewards_editor(prefix: str, existing_rewards: list[Reward]) -> list[Reward]:
    """
    Полноценный редактор наград с возможностью добавления, удаления и редактирования.
    Состояние хранится в session_state по ключу f"{prefix}_rewards".
    """
    rewards_key = f"{prefix}_rewards"
    editing_key = f"{prefix}_editing_idx"
    show_add_key = f"{prefix}_show_add"

    # Инициализация состояния
    if rewards_key not in st.session_state:
        st.session_state[rewards_key] = list(existing_rewards) if existing_rewards else [get_default_reward()]
    if editing_key not in st.session_state:
        st.session_state[editing_key] = -1
    if show_add_key not in st.session_state:
        st.session_state[show_add_key] = False

    rewards = st.session_state[rewards_key]

    st.write("**Награды:**")

    # Отображение существующих наград
    delete_indices = []
    for i, reward in enumerate(rewards):
        cols = st.columns([4, 1, 1])
        with cols[0]:
            data = reward.data
            if isinstance(data, FixedReward):
                desc = f"💰 {data.amount:,.0f} {data.currency}"
            elif hasattr(data, 'percentage'):
                desc = f"📊 RTP {data.percentage*100:.1f}% Chips"
            elif hasattr(data, 'spins'):
                desc = f"🎰 {data.spins} Free Spins on {data.game_name}"
            elif hasattr(data, 'num_packs'):
                desc = f"📦 {data.num_packs}x Pack {data.pack_id}"
            else:
                desc = f"🎁 {type(data).__name__}"
            st.write(f"{i+1}. {desc}")

        with cols[1]:
            if st.button("✏️", key=f"{prefix}_edit_reward_{i}"):
                st.session_state[editing_key] = i
                st.session_state[show_add_key] = False
                st.rerun()
        with cols[2]:
            if st.button("❌", key=f"{prefix}_del_reward_{i}"):
                delete_indices.append(i)

    # Обработка удаления
    if delete_indices:
        for idx in sorted(delete_indices, reverse=True):
            del st.session_state[rewards_key][idx]
        st.rerun()

    # Кнопка добавления новой награды
    if st.button("➕ Добавить награду", key=f"{prefix}_add_reward_btn"):
        st.session_state[show_add_key] = True
        st.session_state[editing_key] = -1
        st.rerun()

    # Редактирование существующей награды
    editing_idx = st.session_state[editing_key]
    if editing_idx >= 0 and editing_idx < len(rewards):
        with st.expander(f"✏️ Редактирование награды #{editing_idx+1}", expanded=True):
            new_reward = render_reward_widget(f"{prefix}_edit", editing_idx, rewards[editing_idx])
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button("💾 Сохранить", key=f"{prefix}_save_edit_{editing_idx}"):
                    st.session_state[rewards_key][editing_idx] = new_reward
                    st.session_state[editing_key] = -1
                    st.rerun()
            with col_cancel:
                if st.button("❌ Отмена", key=f"{prefix}_cancel_edit_{editing_idx}"):
                    st.session_state[editing_key] = -1
                    st.rerun()

    # Добавление новой награды
    if st.session_state[show_add_key]:
        with st.expander("➕ Новая награда", expanded=True):
            new_reward = render_reward_widget(f"{prefix}_new", len(rewards))
            col_add, col_cancel_add = st.columns(2)
            with col_add:
                if st.button("✅ Добавить", key=f"{prefix}_confirm_add"):
                    st.session_state[rewards_key].append(new_reward)
                    st.session_state[show_add_key] = False
                    st.rerun()
            with col_cancel_add:
                if st.button("❌ Отмена", key=f"{prefix}_cancel_add"):
                    st.session_state[show_add_key] = False
                    st.rerun()

    return rewards


def render_progress_node_form(prefix: str, existing: Optional[ProgressNode] = None) -> ProgressNode:
    """Форма ProgressNode с возможностью редактирования наград."""
    st.subheader("📊 Progress Node")

    # Инициализация состояния для наград (если редактируем существующий узел)
    rewards_key = f"{prefix}_p_rewards"
    if existing and rewards_key not in st.session_state:
        st.session_state[rewards_key] = list(existing.rewards) if existing.rewards else [get_default_reward()]
    elif not existing and rewards_key not in st.session_state:
        st.session_state[rewards_key] = [get_default_reward()]

    col1, col2 = st.columns(2)
    with col1:
        node_id = st.number_input(
            "NodeID",
            value=existing.node_id if existing else 1,
            min_value=1, step=1,
            key=f"{prefix}_p_nodeid"
        )
        # Текстовое поле для списка ID через запятую
        next_ids_str = st.text_input(
            "NextNodeID (через запятую)",
            value=",".join(str(x) for x in existing.next_node_ids) if existing and existing.next_node_ids else "2",
            key=f"{prefix}_p_nextids"
        )
        games_str = st.text_input(
            "GameList (через запятую)",
            value=",".join(existing.game_list) if existing else "AllGames",
            key=f"{prefix}_p_games"
        )
        minigame = st.text_input(
            "MiniGame",
            value=existing.mini_game if existing else "FlatReward",
            key=f"{prefix}_p_minigame"
        )
    with col2:
        btn_text = st.text_input(
            "ButtonActionText",
            value=existing.button_action_text if existing else "PLAY NOW!",
            key=f"{prefix}_p_btntext"
        )
        btn_type = st.text_input(
            "ButtonActionType",
            value=existing.button_action_type if existing else "",
            key=f"{prefix}_p_btntype"
        )
        btn_data = st.text_input(
            "ButtonActionData",
            value=existing.button_action_data if existing else "",
            key=f"{prefix}_p_btndata"
        )
        ch_col1, ch_col2 = st.columns(2)
        with ch_col1:
            is_last = st.checkbox(
                "IsLastNode",
                value=existing.is_last_node if existing else False,
                key=f"{prefix}_p_islast"
            )
        with ch_col2:
            hide_loading = st.checkbox(
                "HideLoadingScreenForReward",
                value=existing.hide_loading_screen if existing else False,
                key=f"{prefix}_p_hideload"
            )

    min_bet = render_minbet_widget(f"{prefix}_p_minbet", existing.min_bet if existing else None)

    st.write("**Цель:**")
    goal = render_goal_widget(f"{prefix}_p_goal", existing.goal if existing else None)

    # Редактор наград
    rewards = render_rewards_editor(f"{prefix}_p", st.session_state[rewards_key])

    custom_texts_str = st.text_area(
        "CustomTexts (каждая строка — отдельный текст)",
        value="\n".join(existing.custom_texts) if existing else "",
        key=f"{prefix}_p_ctexts"
    )
    possible_item = st.text_input(
        "PossibleItemCollect",
        value=existing.possible_item_collect if existing else "",
        key=f"{prefix}_p_itemcoll"
    )

    prize_box = st.number_input(
        "PrizeBoxIndex (0 = не задано)",
        value=existing.prize_box_index if existing else 0,
        step=1,
        key=f"{prefix}_p_prizebox"
    )

    if st.button("💾 Сохранить Progress Node", key=f"{prefix}_save_progress", type="primary"):
        game_list = parse_comma_separated_list(games_str)
        # Парсим список NextNodeID
        next_ids = [int(x.strip()) for x in next_ids_str.split(",") if x.strip()]
        if not next_ids:
            next_ids = [2]  # значение по умолчанию
        custom_texts = process_multiline_text(custom_texts_str)
        # Очищаем состояние наград после сохранения
        if rewards_key in st.session_state:
            del st.session_state[rewards_key]
        return ProgressNode(
            node_id=int(node_id),
            next_node_ids=next_ids,
            game_list=game_list,
            min_bet=min_bet,
            goal=goal,
            rewards=rewards,
            is_last_node=is_last,
            mini_game=minigame,
            button_action_text=btn_text,
            button_action_type=btn_type,
            button_action_data=btn_data,
            custom_texts=custom_texts,
            possible_item_collect=possible_item.strip() or "Default",
            hide_loading_screen=hide_loading,
            prize_box_index=int(prize_box),
        )
    return existing


def render_entries_node_form(prefix: str, existing: Optional[EntriesNode] = None) -> EntriesNode:
    """Форма EntriesNode."""
    st.subheader("🚪 Entries Node")
    col1, col2 = st.columns(2)
    with col1:
        node_id = st.number_input(
            "NodeID",
            value=existing.node_id if existing else 1,
            min_value=1, step=1,
            key=f"{prefix}_e_nodeid"
        )
        games_str = st.text_input(
            "GameList (через запятую)",
            value=",".join(existing.game_list) if existing else "AllGames",
            key=f"{prefix}_e_games"
        )
    with col2:
        goal_type_str = st.text_input(
            "GoalType",
            value=",".join(existing.goal_types) if existing else "Spins",
            key=f"{prefix}_e_goaltype"
        )
        entry_types_str = st.text_input(
            "EntryTypes (через запятую)",
            value=",".join(existing.entry_types) if existing else "MyEvent",
            key=f"{prefix}_e_entrytypes"
        )

    min_bet = render_minbet_widget(f"{prefix}_e_minbet", existing.min_bet if existing else None)

    col3, col4 = st.columns(2)
    with col3:
        btn_text = st.text_input(
            "ButtonActionText",
            value=existing.button_action_text if existing else "PLAY NOW!",
            key=f"{prefix}_e_btntext"
        )
    with col4:
        btn_type = st.text_input(
            "ButtonActionType",
            value=existing.button_action_type if existing else "",
            key=f"{prefix}_e_btntype"
        )
    btn_data = st.text_input(
        "ButtonActionData",
        value=existing.button_action_data if existing else "",
        key=f"{prefix}_e_btndata"
    )

    custom_texts_str = st.text_area(
        "CustomTexts (каждая строка — отдельный текст)",
        value="\n".join(existing.custom_texts) if existing else "",
        key=f"{prefix}_e_ctexts"
    )
    possible_item = st.text_input(
        "PossibleItemCollect",
        value=existing.possible_item_collect if existing else "Default",
        key=f"{prefix}_e_itemcoll"
    )
    prize_box = st.number_input(
        "PrizeBoxIndex (0 = не задано)",
        value=existing.prize_box_index if existing else 0,
        step=1,
        key=f"{prefix}_e_prizebox"
    )

    if st.button("💾 Сохранить Entries Node", key=f"{prefix}_save_entries", type="primary"):
        game_list = parse_comma_separated_list(games_str)
        goal_types = parse_comma_separated_list(goal_type_str)
        entry_types = parse_comma_separated_list(entry_types_str)
        custom_texts = process_multiline_text(custom_texts_str)
        return EntriesNode(
            node_id=int(node_id),
            game_list=game_list,
            min_bet=min_bet,
            goal_types=goal_types,
            entry_types=entry_types,
            button_action_text=btn_text,
            button_action_type=btn_type,
            button_action_data=btn_data,
            custom_texts=custom_texts,
            possible_item_collect=possible_item.strip() or "Default",
            prize_box_index=int(prize_box),
        )
    return existing


def render_dummy_node_form(prefix: str, existing: Optional[DummyNode] = None) -> DummyNode:
    """Форма DummyNode - упрощённая версия без наград и лишних параметров."""
    st.subheader("🎲 Dummy Node")

    col1, col2 = st.columns(2)
    with col1:
        node_id = st.number_input(
            "NodeID",
            value=existing.node_id if existing else 1,
            min_value=1, step=1,
            key=f"{prefix}_d_nodeid"
        )
        next_ids_str = st.text_input(
            "NextNodeID (через запятую)",
            value=",".join(str(x) for x in existing.next_node_ids) if existing else "11,21,31",
            key=f"{prefix}_d_nextids"
        )
    with col2:
        default_node_id = st.number_input(
            "DefaultNodeID",
            value=existing.default_node_id if existing else 1,
            min_value=1, step=1,
            key=f"{prefix}_d_defnode"
        )

    custom_texts_str = st.text_area(
        "CustomTexts (каждая строка — отдельный текст)",
        value="\n".join(existing.custom_texts) if existing else "",
        key=f"{prefix}_d_ctexts"
    )

    if st.button("💾 Сохранить Dummy Node", key=f"{prefix}_save_dummy", type="primary"):
        next_ids = [int(x.strip()) for x in next_ids_str.split(",") if x.strip()]
        custom_texts = process_multiline_text(custom_texts_str)
        return DummyNode(
            node_id=int(node_id),
            next_node_ids=next_ids if next_ids else [11,21,31],
            default_node_id=int(default_node_id),
            rewards=[get_default_reward()],  # одна фиктивная награда для совместимости
            is_choice_event=True,
            custom_texts=custom_texts,
            hide_loading_screen=False,
            prize_box_index=0,
        )
    return existing


def render_node_editor(
    node_type: str,
    existing: Optional[Node] = None,
    key_prefix: str = "node"
) -> Optional[Node]:
    """
    Универсальный рендерер редактора узла в зависимости от типа.
    Возвращает None, если кнопка сохранения не нажата.
    """
    if node_type == "ProgressNode":
        return render_progress_node_form(key_prefix, existing)
    elif node_type == "EntriesNode":
        return render_entries_node_form(key_prefix, existing)
    elif node_type == "DummyNode":
        return render_dummy_node_form(key_prefix, existing)
    else:
        st.error(f"Неизвестный тип узла: {node_type}")
        return None