# ui/widgets/node_editor.py
import streamlit as st
from typing import Optional, Union
from models.nodes import ProgressNode, EntriesNode, DummyNode, Node
from models.goals import Goal
from models.rewards import Reward
from .minbet_widget import render_minbet_widget
from .goal_widget import render_goal_widget
from .reward_widget import render_rewards_list
from utils.helpers import parse_comma_separated_list, process_multiline_text


def render_progress_node_form(prefix: str, existing: Optional[ProgressNode] = None) -> ProgressNode:
    """Форма ProgressNode. Возвращает заполненный объект."""
    with st.form(key=f"{prefix}_progress_form"):
        st.subheader("📊 Progress Node")
        col1, col2 = st.columns(2)
        with col1:
            node_id = st.number_input(
                "NodeID",
                value=existing.node_id if existing else 1,
                min_value=1, step=1,
                key=f"{prefix}_p_nodeid"
            )
            next_id = st.number_input(
                "NextNodeID (одно число)",
                value=existing.next_node_ids[0] if existing and existing.next_node_ids else 2,
                min_value=1, step=1,
                key=f"{prefix}_p_nextid"
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
            is_last = st.checkbox(
                "IsLastNode",
                value=existing.is_last_node if existing else False,
                key=f"{prefix}_p_islast"
            )

        min_bet = render_minbet_widget(f"{prefix}_p_minbet", existing.min_bet if existing else None)

        # Goal
        st.write("**Цель:**")
        goal = render_goal_widget(f"{prefix}_p_goal", existing.goal if existing else None)

        # Rewards – только просмотр внутри формы (редактирование отключено)
        rewards = existing.rewards if existing else []
        st.write("**Награды:**")
        render_rewards_list(f"{prefix}_p", rewards, editable=False)

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

        col3, col4 = st.columns(2)
        with col3:
            hide_loading = st.checkbox(
                "HideLoadingScreenForReward",
                value=existing.hide_loading_screen if existing else False,
                key=f"{prefix}_p_hideload"
            )
        with col4:
            prize_box = st.number_input(
                "PrizeBoxIndex (0 = не задано)",
                value=existing.prize_box_index if existing else -1,
                step=1,
                key=f"{prefix}_p_prizebox"
            )

        submitted = st.form_submit_button("💾 Сохранить Progress Node")
        if submitted:
            game_list = parse_comma_separated_list(games_str)
            custom_texts = process_multiline_text(custom_texts_str)
            return ProgressNode(
                node_id=int(node_id),
                next_node_ids=[int(next_id)],
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

    # Если форма не отправлена и есть существующий объект, возвращаем его
    return existing


def render_entries_node_form(prefix: str, existing: Optional[EntriesNode] = None) -> EntriesNode:
    """Форма EntriesNode."""
    with st.form(key=f"{prefix}_entries_form"):
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
            value=existing.prize_box_index if existing else -1,
            step=1,
            key=f"{prefix}_e_prizebox"
        )

        submitted = st.form_submit_button("💾 Сохранить Entries Node")
        if submitted:
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
    """Форма DummyNode."""
    with st.form(key=f"{prefix}_dummy_form"):
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
            is_choice = st.checkbox(
                "IsChoiceEvent",
                value=existing.is_choice_event if existing else True,
                key=f"{prefix}_d_ischoice"
            )

        # Rewards – только просмотр (редактирование отключено)
        rewards = existing.rewards if existing else []
        st.write("**Награды:**")
        render_rewards_list(f"{prefix}_d", rewards, editable=False)

        custom_texts_str = st.text_area(
            "CustomTexts (каждая строка — отдельный текст)",
            value="\n".join(existing.custom_texts) if existing else "",
            key=f"{prefix}_d_ctexts"
        )

        col3, col4 = st.columns(2)
        with col3:
            hide_loading = st.checkbox(
                "HideLoadingScreenForReward",
                value=existing.hide_loading_screen if existing else False,
                key=f"{prefix}_d_hideload"
            )
        with col4:
            prize_box = st.number_input(
                "PrizeBoxIndex (0 = не задано)",
                value=existing.prize_box_index if existing else -1,
                step=1,
                key=f"{prefix}_d_prizebox"
            )

        submitted = st.form_submit_button("💾 Сохранить Dummy Node")
        if submitted:
            next_ids = [int(x.strip()) for x in next_ids_str.split(",") if x.strip()]
            custom_texts = process_multiline_text(custom_texts_str)
            return DummyNode(
                node_id=int(node_id),
                next_node_ids=next_ids if next_ids else [11,21,31],
                default_node_id=int(default_node_id),
                rewards=rewards,
                is_choice_event=is_choice,
                custom_texts=custom_texts,
                hide_loading_screen=hide_loading,
                prize_box_index=int(prize_box),
            )
    return existing


def render_node_editor(
    node_type: str,
    existing: Optional[Node] = None,
    key_prefix: str = "node"
) -> Optional[Node]:
    """
    Универсальный рендерер редактора узла в зависимости от типа.
    Возвращает None, если форма не отправлена.
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