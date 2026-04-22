import streamlit as st
from typing import Optional
from models.nodes import ProgressNode, EntriesNode, DummyNode, Node
from .minbet_widget import render_minbet_widget
from .goal_widget import render_goal_widget
from .rewards_editor import render_rewards_editor, get_default_reward
from utils.helpers import parse_comma_separated_list, process_multiline_text


# ---------------------------------------------------------------------------
# Вместо инъекции в ключи виджетов — храним "снимок" редактируемой ноды
# в session_state и читаем дефолтные значения из него.
# ---------------------------------------------------------------------------

def _snapshot_key(prefix: str) -> str:
    return f"_node_snapshot_{prefix}"


def set_node_snapshot(prefix: str, node: Node) -> None:
    """Сохраняет снимок ноды для последующего заполнения формы."""
    st.session_state[_snapshot_key(prefix)] = node
    # Сбрасываем все ключи виджетов этого префикса, чтобы они
    # взяли значения из value= при следующем рендере
    _clear_widget_keys(prefix, node)


def _clear_widget_keys(prefix: str, node: Node) -> None:
    """Удаляет из session_state все ключи виджетов данного префикса."""
    if isinstance(node, ProgressNode):
        suffixes = [
            f"{prefix}_p_nodeid", f"{prefix}_p_nextids", f"{prefix}_p_games",
            f"{prefix}_p_minigame", f"{prefix}_p_btntext", f"{prefix}_p_btntype",
            f"{prefix}_p_btndata", f"{prefix}_p_islast", f"{prefix}_p_hideload",
            f"{prefix}_p_ctexts", f"{prefix}_p_itemcoll", f"{prefix}_p_prizebox",
            f"{prefix}_p_rewards",
            f"{prefix}_p_minbet_minbet_type", f"{prefix}_p_minbet_fixed",
            f"{prefix}_p_minbet_var", f"{prefix}_p_minbet_min", f"{prefix}_p_minbet_max",
            f"{prefix}_p_goal_goal_type", f"{prefix}_p_goal_goal_params",
            f"{prefix}_p_goal_spin_mult", f"{prefix}_p_goal_spin_min", f"{prefix}_p_goal_spin_max",
            f"{prefix}_p_goal_fixed_target",
        ]
    elif isinstance(node, EntriesNode):
        suffixes = [
            f"{prefix}_e_nodeid", f"{prefix}_e_games", f"{prefix}_e_goaltype",
            f"{prefix}_e_entrytypes", f"{prefix}_e_btntext", f"{prefix}_e_btntype",
            f"{prefix}_e_btndata", f"{prefix}_e_ctexts", f"{prefix}_e_itemcoll",
            f"{prefix}_e_prizebox",
            f"{prefix}_e_minbet_minbet_type", f"{prefix}_e_minbet_fixed",
            f"{prefix}_e_minbet_var", f"{prefix}_e_minbet_min", f"{prefix}_e_minbet_max",
        ]
    elif isinstance(node, DummyNode):
        suffixes = [
            f"{prefix}_d_nodeid", f"{prefix}_d_nextids",
            f"{prefix}_d_defnode", f"{prefix}_d_ctexts",
        ]
    else:
        suffixes = []

    for key in suffixes:
        st.session_state.pop(key, None)


def _get_snapshot(prefix: str) -> Optional[Node]:
    return st.session_state.get(_snapshot_key(prefix))


def _clear_snapshot(prefix: str) -> None:
    st.session_state.pop(_snapshot_key(prefix), None)


# ---------------------------------------------------------------------------
# Формы
# ---------------------------------------------------------------------------

def render_progress_node_form(prefix: str, existing: Optional[ProgressNode] = None) -> ProgressNode:
    """Форма ProgressNode."""
    st.subheader("📊 Progress Node")

    # Используем снимок если есть, иначе existing
    snap = _get_snapshot(prefix)
    src: Optional[ProgressNode] = snap if isinstance(snap, ProgressNode) else existing

    rewards_key = f"{prefix}_p_rewards"
    if rewards_key not in st.session_state:
        st.session_state[rewards_key] = list(src.rewards) if src and src.rewards else [get_default_reward()]

    col1, col2 = st.columns(2)
    with col1:
        node_id = st.number_input(
            "NodeID",
            value=src.node_id if src else 1,
            min_value=1, step=1,
            key=f"{prefix}_p_nodeid"
        )
        next_ids_str = st.text_input(
            "NextNodeID (через запятую)",
            value=",".join(str(x) for x in src.next_node_ids) if src and src.next_node_ids else "2",
            key=f"{prefix}_p_nextids"
        )
        games_str = st.text_input(
            "GameList (через запятую)",
            value=",".join(src.game_list) if src else "AllGames",
            key=f"{prefix}_p_games"
        )
        minigame = st.text_input(
            "MiniGame",
            value=src.mini_game if src else "FlatReward",
            key=f"{prefix}_p_minigame"
        )
    with col2:
        btn_text = st.text_input(
            "ButtonActionText",
            value=src.button_action_text if src else "PLAY NOW!",
            key=f"{prefix}_p_btntext"
        )
        btn_type = st.text_input(
            "ButtonActionType",
            value=src.button_action_type if src else "",
            key=f"{prefix}_p_btntype"
        )
        btn_data = st.text_input(
            "ButtonActionData",
            value=src.button_action_data if src else "",
            key=f"{prefix}_p_btndata"
        )
        ch_col1, ch_col2 = st.columns(2)
        with ch_col1:
            is_last = st.checkbox(
                "IsLastNode",
                value=src.is_last_node if src else False,
                key=f"{prefix}_p_islast"
            )
        with ch_col2:
            hide_loading = st.checkbox(
                "HideLoadingScreenForReward",
                value=src.hide_loading_screen if src else False,
                key=f"{prefix}_p_hideload"
            )

    min_bet = render_minbet_widget(f"{prefix}_p_minbet", src.min_bet if src else None)

    st.write("**Цель:**")
    goal = render_goal_widget(f"{prefix}_p_goal", src.goal if src else None)

    rewards = render_rewards_editor(f"{prefix}_p", st.session_state[rewards_key])

    custom_texts_str = st.text_area(
        "CustomTexts (каждая строка — отдельный текст)",
        value="\n".join(src.custom_texts) if src else "",
        key=f"{prefix}_p_ctexts"
    )
    possible_item = st.text_input(
        "PossibleItemCollect",
        value=src.possible_item_collect if src else "",
        key=f"{prefix}_p_itemcoll"
    )
    prize_box = st.number_input(
        "PrizeBoxIndex (0 = не задано)",
        value=src.prize_box_index if src else 0,
        step=1,
        key=f"{prefix}_p_prizebox"
    )

    if st.button("💾 Сохранить Progress Node", key=f"{prefix}_save_progress", type="primary"):
        game_list = parse_comma_separated_list(games_str)
        next_ids = [int(x.strip()) for x in next_ids_str.split(",") if x.strip()]
        if not next_ids:
            next_ids = [2]
        custom_texts = process_multiline_text(custom_texts_str)
        st.session_state.pop(rewards_key, None)
        _clear_snapshot(prefix)
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
    return None


def render_entries_node_form(prefix: str, existing: Optional[EntriesNode] = None) -> EntriesNode:
    """Форма EntriesNode."""
    st.subheader("🚪 Entries Node")

    snap = _get_snapshot(prefix)
    src: Optional[EntriesNode] = snap if isinstance(snap, EntriesNode) else existing

    col1, col2 = st.columns(2)
    with col1:
        node_id = st.number_input(
            "NodeID",
            value=src.node_id if src else 1,
            min_value=1, step=1,
            key=f"{prefix}_e_nodeid"
        )
        games_str = st.text_input(
            "GameList (через запятую)",
            value=",".join(src.game_list) if src else "AllGames",
            key=f"{prefix}_e_games"
        )
    with col2:
        goal_type_str = st.text_input(
            "GoalType",
            value=",".join(src.goal_types) if src else "Spins",
            key=f"{prefix}_e_goaltype"
        )
        entry_types_str = st.text_input(
            "EntryTypes (через запятую)",
            value=",".join(src.entry_types) if src else "MyEvent",
            key=f"{prefix}_e_entrytypes"
        )

    min_bet = render_minbet_widget(f"{prefix}_e_minbet", src.min_bet if src else None)

    col3, col4 = st.columns(2)
    with col3:
        btn_text = st.text_input(
            "ButtonActionText",
            value=src.button_action_text if src else "PLAY NOW!",
            key=f"{prefix}_e_btntext"
        )
    with col4:
        btn_type = st.text_input(
            "ButtonActionType",
            value=src.button_action_type if src else "",
            key=f"{prefix}_e_btntype"
        )
    btn_data = st.text_input(
        "ButtonActionData",
        value=src.button_action_data if src else "",
        key=f"{prefix}_e_btndata"
    )
    custom_texts_str = st.text_area(
        "CustomTexts (каждая строка — отдельный текст)",
        value="\n".join(src.custom_texts) if src else "",
        key=f"{prefix}_e_ctexts"
    )
    possible_item = st.text_input(
        "PossibleItemCollect",
        value=src.possible_item_collect if src else "Default",
        key=f"{prefix}_e_itemcoll"
    )
    prize_box = st.number_input(
        "PrizeBoxIndex (0 = не задано)",
        value=src.prize_box_index if src else 0,
        step=1,
        key=f"{prefix}_e_prizebox"
    )

    if st.button("💾 Сохранить Entries Node", key=f"{prefix}_save_entries", type="primary"):
        game_list = parse_comma_separated_list(games_str)
        goal_types = parse_comma_separated_list(goal_type_str)
        entry_types = parse_comma_separated_list(entry_types_str)
        custom_texts = process_multiline_text(custom_texts_str)
        _clear_snapshot(prefix)
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
    return None


def render_dummy_node_form(prefix: str, existing: Optional[DummyNode] = None) -> DummyNode:
    """Форма DummyNode."""
    st.subheader("🎲 Dummy Node")

    snap = _get_snapshot(prefix)
    src: Optional[DummyNode] = snap if isinstance(snap, DummyNode) else existing

    col1, col2 = st.columns(2)
    with col1:
        node_id = st.number_input(
            "NodeID",
            value=src.node_id if src else 1,
            min_value=1, step=1,
            key=f"{prefix}_d_nodeid"
        )
        next_ids_str = st.text_input(
            "NextNodeID (через запятую)",
            value=",".join(str(x) for x in src.next_node_ids) if src else "11,21,31",
            key=f"{prefix}_d_nextids"
        )
    with col2:
        default_node_id = st.number_input(
            "DefaultNodeID",
            value=src.default_node_id if src else 1,
            min_value=1, step=1,
            key=f"{prefix}_d_defnode"
        )

    custom_texts_str = st.text_area(
        "CustomTexts (каждая строка — отдельный текст)",
        value="\n".join(src.custom_texts) if src else "",
        key=f"{prefix}_d_ctexts"
    )

    if st.button("💾 Сохранить Dummy Node", key=f"{prefix}_save_dummy", type="primary"):
        next_ids = [int(x.strip()) for x in next_ids_str.split(",") if x.strip()]
        custom_texts = process_multiline_text(custom_texts_str)
        _clear_snapshot(prefix)
        return DummyNode(
            node_id=int(node_id),
            next_node_ids=next_ids if next_ids else [11, 21, 31],
            default_node_id=int(default_node_id),
            rewards=[get_default_reward()],
            is_choice_event=True,
            custom_texts=custom_texts,
            hide_loading_screen=False,
            prize_box_index=0,
        )
    return None


def render_node_editor(
    node_type: str,
    existing: Optional[Node] = None,
    key_prefix: str = "node"
) -> Optional[Node]:
    """
    Универсальный рендерер редактора узла.
    При смене existing сбрасывает ключи виджетов и делает rerun,
    чтобы форма отрисовалась с актуальными данными.
    """
    snap_key = _snapshot_key(key_prefix)
    id_key = f"_node_loaded_id_{key_prefix}"

    if existing is not None:
        new_node_id = (type(existing).__name__, getattr(existing, "node_id", None))
        loaded_id = st.session_state.get(id_key)

        if loaded_id != new_node_id:
            # Новая нода — сбрасываем виджеты, обновляем снимок и перезапускаем рендер
            _clear_widget_keys(key_prefix, existing)
            st.session_state[snap_key] = existing
            st.session_state[id_key] = new_node_id
            st.rerun()
    else:
        _clear_snapshot(key_prefix)
        st.session_state.pop(id_key, None)

    if node_type == "ProgressNode":
        return render_progress_node_form(key_prefix, existing)
    elif node_type == "EntriesNode":
        return render_entries_node_form(key_prefix, existing)
    elif node_type == "DummyNode":
        return render_dummy_node_form(key_prefix, existing)
    else:
        st.error(f"Неизвестный тип узла: {node_type}")
        return None
