import streamlit as st
import pandas as pd
from services.state_manager import AppState
from models.event import Segment, Stage
from models.nodes import ProgressNode
from models.minbet import FixedMinBet, VariableMinBet
from models.goals import Goal, FixedGoal
from models.rewards import Reward, FixedReward, CollectableSellPacksReward
from utils.helpers import parse_comma_separated_list

# Словарь синонимов для автомаппинга
FIELD_SYNONYMS = {
    "segment_name": ["vip_tier", "segment_name", "сегмент", "segment", "vip tier"],
    "node_id": ["nodeid", "node_id", "id", "id ноды"],
    "next_node_id": ["nextnodeid", "next_node_id", "next node id", "следующий"],
    "game_list": ["gamelist", "game_list", "games", "игры"],
    "minbet_variable": ["minbet_variable", "min_bet_variable", "variable"],
    "minbet_min": ["minbet_min", "min_bet_min", "minbet min"],
    "minbet_max": ["minbet_max", "min_bet_max", "minbet max"],
    "goal_type": ["goal_type", "goaltype", "тип цели"],
    "goal_multiplier": ["goal_multiplier", "multiplier", "множитель"],
    "goal_min": ["goal_min", "goalmin", "goal min"],
    "goal_max": ["goal_max", "goalmax", "goal max"],
    "chips_amount": ["chipsamount", "chips_amount", "chips amount", "chips"],
    "chips_amount_2": ["chipsamount_2", "chips_amount_2"],
    "is_last_node": ["islastnode", "is_last_node", "islast", "last"],
    "resegment_flag": ["resegmentflag", "resegment_flag", "resegment"],
    "mini_game": ["minigame", "mini_game", "mini game"],
    "button_action_text": ["buttonactiontext", "button_action_text", "button text"],
    "button_action_type": ["buttonactiontype", "button_action_type", "button type"],
    "button_action_data": ["buttonactiondata", "button_action_data", "button data"],
    "custom_texts": ["customtexts", "custom_texts", "custom texts"],
    "possible_item_collect": ["possibleitemcollect", "possible_item_collect", "item collect"],
    "contribution_level": ["contributionlevel", "contribution_level", "contribution"],
    "pack_id": ["packid", "pack_id", "pack id"],
    "num_packs": ["numpacks", "num_packs", "num packs"],
}

def _normalize(s: str) -> str:
    return s.strip().lower().replace("-", "_").replace(" ", "_")


def _vip_range_from_segment_name(seg_name: str) -> str:
    """
    Пытается извлечь VIPRange из имени сегмента.
    Vip0_0  → "0-0"
    Vip2_5  → "2-5"
    Vip10_10 → "10-10"
    Если не распознаётся — возвращает пустую строку.
    """
    import re
    m = re.match(r'^[Vv][Ii][Pp](\d+)[_\-](\d+)$', seg_name.strip())
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return ""

def auto_map_columns(df_columns: list[str]) -> dict[str, str | None]:
    norm_cols = {_normalize(c): c for c in df_columns}
    mapping = {}
    for field, synonyms in FIELD_SYNONYMS.items():
        matched = None
        for syn in synonyms:
            if _normalize(syn) in norm_cols:
                matched = norm_cols[_normalize(syn)]
                break
        mapping[field] = matched
    return mapping

def _read_file(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        raw = uploaded_file.read()
        encoding = "latin-1"
        for enc in ("utf-8", "utf-8-sig", "cp1251"):
            try:
                raw.decode(enc)
                encoding = enc
                break
            except (UnicodeDecodeError, LookupError):
                continue
        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file, encoding=encoding, sep=None, engine="python")
    else:
        return pd.read_excel(uploaded_file)

def _find_header_row(df_raw: pd.DataFrame) -> int:
    """
    Ищет строку-заголовок: первую строку, где хотя бы 3 ячейки
    совпадают с известными синонимами полей.
    Возвращает индекс строки (0-based) или 0 если не найдено.
    """
    all_synonyms = set()
    for syns in FIELD_SYNONYMS.values():
        for s in syns:
            all_synonyms.add(_normalize(s))

    for i, row in df_raw.iterrows():
        hits = sum(
            1 for v in row
            if pd.notna(v) and _normalize(str(v)) in all_synonyms
        )
        if hits >= 3:
            return int(i)
    return 0


def _load_with_header_detection(uploaded_file) -> pd.DataFrame:
    """
    Читает файл, автоматически пропуская строки до заголовка
    (например, строку с датой в начале файла).
    """
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        raw = uploaded_file.read()
        encoding = "latin-1"
        for enc in ("utf-8", "utf-8-sig", "cp1251"):
            try:
                raw.decode(enc)
                encoding = enc
                break
            except (UnicodeDecodeError, LookupError):
                continue
        uploaded_file.seek(0)
        df_raw = pd.read_csv(
            uploaded_file, encoding=encoding,
            sep=None, engine="python", header=None
        )
    else:
        df_raw = pd.read_excel(uploaded_file, header=None)

    header_row = _find_header_row(df_raw)
    # Используем найденную строку как заголовок
    # Строим заголовки с дедупликацией дублей (ChipsAmount → ChipsAmount, ChipsAmount_2, ...)
    raw_headers = [str(v).strip() if pd.notna(v) else f"_col{i}"
                   for i, v in enumerate(df_raw.iloc[header_row])]
    seen: dict[str, int] = {}
    deduped: list[str] = []
    for h in raw_headers:
        if h in seen:
            seen[h] += 1
            deduped.append(f"{h}_{seen[h]}")
        else:
            seen[h] = 1
            deduped.append(h)
    df_raw.columns = deduped
    df = df_raw.iloc[header_row + 1:].reset_index(drop=True)
    # Убираем полностью пустые строки
    df = df.dropna(how="all")
    return df


def render_import_tab():
    st.subheader("📥 Пакетный импорт сегментов и узлов")
    render_batch_import_panel(key="import_tab")


def render_batch_import_panel(key: str = "editor_tab"):

    with st.expander("ℹ️ Справка по формату файла", expanded=False):
        st.markdown("""
Поддерживаются **CSV** и **Excel**. Строки до заголовка (например, дата) пропускаются автоматически.

**Ожидаемые колонки (названия могут отличаться — система сопоставит автоматически):**

| Поле | Примеры заголовков |
|---|---|
| Сегмент | VIP_TIER, segment_name, сегмент |
| Node ID | NodeID, node_id, id |
| Next Node ID | NextNodeID, next_node_id |
| Game List | GameList, game_list, игры |
| MinBet Variable | MinBet_Variable, variable |
| MinBet Min | MinBet_Min |
| MinBet Max | MinBet_Max |
| Goal Type | Goal_Type, goal_type |
| Goal Multiplier | Goal_Multiplier, multiplier |
| Goal Min | Goal_Min |
| Goal Max | Goal_Max |
| Chips Amount | ChipsAmount, chips_amount |
| Is Last Node | IsLastNode, is_last_node |
| MiniGame | MiniGame, mini_game |
| Button Text | ButtonActionText |
| Pack ID | PackId, pack_id |
| Num Packs | NumPacks, num_packs |
        """)

    uploaded_file = st.file_uploader("Выберите файл", type=["csv", "xlsx", "xls"], key=f"file_uploader_{key}")
    if uploaded_file is None:
        return

    try:
        df = _load_with_header_detection(uploaded_file)
    except Exception as e:
        st.error(f"Ошибка чтения файла: {e}")
        return

    st.write(f"**Найдено строк данных: {len(df)}, колонок: {len(df.columns)}**")
    st.dataframe(df.head())

    # Автомаппинг
    mapping = auto_map_columns(list(df.columns))
    unmatched = [f for f, col in mapping.items() if col is None]

    with st.expander(
        f"🔗 Маппинг колонок {'⚠️ есть нераспознанные' if unmatched else '✅ все распознаны'}",
        expanded=bool(unmatched)
    ):
        col_options = ["— не использовать —"] + list(df.columns)
        manual: dict[str, str | None] = {}

        LABELS = {
            "segment_name": "Сегмент *",
            "node_id": "Node ID *",
            "next_node_id": "Next Node ID",
            "game_list": "Game List",
            "minbet_variable": "MinBet Variable",
            "minbet_min": "MinBet Min",
            "minbet_max": "MinBet Max",
            "goal_type": "Goal Type",
            "goal_multiplier": "Goal Multiplier",
            "goal_min": "Goal Min",
            "goal_max": "Goal Max",
            "chips_amount": "Chips Amount (1)",
            "chips_amount_2": "Chips Amount (2)",
            "is_last_node": "Is Last Node",
            "resegment_flag": "Resegment Flag",
            "mini_game": "Mini Game",
            "button_action_text": "Button Text",
            "button_action_type": "Button Type",
            "button_action_data": "Button Data",
            "custom_texts": "Custom Texts",
            "possible_item_collect": "Possible Item Collect",
            "contribution_level": "Contribution Level",
            "pack_id": "Pack ID",
            "num_packs": "Num Packs",
        }

        fields = list(LABELS.items())
        mid = len(fields) // 2 + len(fields) % 2
        col_l, col_r = st.columns(2)

        def render_row(field, label, container):
            with container:
                auto_col = mapping.get(field)
                if auto_col:
                    st.markdown(f"✅ **{label}** → `{auto_col}`")
                    sel = st.selectbox(
                        label, options=col_options,
                        index=col_options.index(auto_col) if auto_col in col_options else 0,
                        key=f"map_{field}", label_visibility="collapsed"
                    )
                else:
                    prefix = "⚠️" if field in ("segment_name", "node_id") else "❓"
                    st.markdown(f"{prefix} **{label}**")
                    sel = st.selectbox(
                        label, options=col_options, index=0,
                        key=f"map_{field}", label_visibility="collapsed"
                    )
                manual[field] = None if sel == "— не использовать —" else sel

        for f, l in fields[:mid]:
            render_row(f, l, col_l)
        for f, l in fields[mid:]:
            render_row(f, l, col_r)

    final = {**mapping, **manual}

    missing_req = [f for f in ("segment_name", "node_id") if not final.get(f)]
    if missing_req:
        st.warning(f"⚠️ Не сопоставлены обязательные поля: {', '.join(missing_req)}")

    if st.button("🚀 Начать импорт", type="primary", disabled=bool(missing_req)):
        _run_import(df, final)


def _get(row, field: str, final_mapping: dict, default="") -> str:
    col = final_mapping.get(field)
    if col and col in row.index:
        v = row[col]
        return "" if pd.isna(v) else str(v).strip()
    return default


def _run_import(df: pd.DataFrame, final: dict):
    app_state = AppState.get_instance()
    event_idx = app_state.get_current_event_idx()

    # Если текущее событие не выбрано — пробуем взять первое
    if event_idx < 0:
        events_raw = app_state.get_events_raw()
        if events_raw:
            event_idx = 0
            app_state.set_current_event_idx(0)
        else:
            st.error("Сначала создайте событие на вкладке «Редактор».")
            return

    current_event = app_state.get_event_by_index(event_idx)
    if current_event is None:
        st.error(f"Не удалось получить событие с индексом {event_idx}.")
        return

    st.info(f"Импорт в событие: **{current_event.event_id}**")

    def get(row, field, default=""):
        return _get(row, field, final, default)

    segments_created = 0
    nodes_created = 0
    errors: list[str] = []

    # Проход 1: сегменты
    segments_map: dict[str, Segment] = {}
    for idx, row in df.iterrows():
        seg_name = get(row, "segment_name")
        if not seg_name or seg_name == "nan":
            continue
        if seg_name in segments_map:
            continue
        if seg_name not in current_event.segments:
            vip = _vip_range_from_segment_name(seg_name)
            new_seg = Segment(
                name=seg_name,
                segment_info_type="VIPRange" if vip else "",
                segment_info_value=vip if vip else "",
            )
            current_event.segments[seg_name] = new_seg
            segments_created += 1
        segments_map[seg_name] = current_event.segments[seg_name]

    # Проход 2: узлы
    for idx, row in df.iterrows():
        try:
            seg_name = get(row, "segment_name")
            if not seg_name or seg_name == "nan":
                continue
            segment = segments_map.get(seg_name)
            if segment is None:
                errors.append(f"Строка {idx+2}: сегмент '{seg_name}' не найден")
                continue

            node_id_str = get(row, "node_id", "0")
            try:
                node_id = int(float(node_id_str))
            except ValueError:
                errors.append(f"Строка {idx+2}: некорректный node_id '{node_id_str}'")
                continue
            if node_id <= 0:
                errors.append(f"Строка {idx+2}: node_id не указан")
                continue

            existing_ids = {n.node_id for stage in segment.stages for n in stage.nodes}
            if node_id in existing_ids:
                errors.append(f"Строка {idx+2}: node_id {node_id} уже существует в '{seg_name}'")
                continue

            # Next node IDs
            next_str = get(row, "next_node_id", "")
            next_node_ids: list[int] = []
            if next_str and next_str != "nan":
                sep = ";" if ";" in next_str else ","
                next_node_ids = [int(float(x.strip())) for x in next_str.split(sep) if x.strip()]

            # Game list
            games_str = get(row, "game_list", "AllGames")
            game_list: list[str] = []
            if games_str and games_str != "nan":
                sep = ";" if ";" in games_str else ","
                game_list = [x.strip() for x in games_str.split(sep) if x.strip()]
            if not game_list:
                game_list = ["AllGames"]

            # MinBet — Variable с тремя колонками
            mb_var = get(row, "minbet_variable", "")
            mb_min = get(row, "minbet_min", "")
            mb_max = get(row, "minbet_max", "")
            if mb_var and mb_var not in ("nan", ""):
                try:
                    min_bet = VariableMinBet(
                        variable=float(mb_var),
                        min=float(mb_min) if mb_min and mb_min != "nan" else 0.0,
                        max=float(mb_max) if mb_max and mb_max != "nan" else float(mb_var),
                    )
                except ValueError:
                    min_bet = FixedMinBet(amount=250000.0)
            else:
                min_bet = FixedMinBet(amount=250000.0)

            # Goal — SpinpadGoal из отдельных колонок
            goal_type_str = get(row, "goal_type", "Spins").strip().lstrip()
            goal_mult = get(row, "goal_multiplier", "")
            goal_min_s = get(row, "goal_min", "")
            goal_max_s = get(row, "goal_max", "")
            try:
                if goal_mult and goal_mult not in ("nan", ""):
                    from models.goals import SpinpadGoal
                    goal = Goal(
                        type=[goal_type_str],
                        params=SpinpadGoal(
                            multiplier=float(goal_mult),
                            min=int(float(goal_min_s)) if goal_min_s and goal_min_s != "nan" else 1,
                            max=int(float(goal_max_s)) if goal_max_s and goal_max_s != "nan" else 9999,
                        )
                    )
                else:
                    goal = Goal(type=[goal_type_str], params=FixedGoal(target=20))
            except (ValueError, TypeError):
                goal = Goal(type=[goal_type_str], params=FixedGoal(target=20))

            # Rewards
            rewards: list[Reward] = []
            chips_str = get(row, "chips_amount", "")
            if chips_str and chips_str not in ("nan", "0", ""):
                try:
                    rewards.append(Reward(data=FixedReward(currency="Chips", amount=float(chips_str))))
                except ValueError:
                    pass

            chips_str_2 = get(row, "chips_amount_2", "")
            if chips_str_2 and chips_str_2 not in ("nan", "0", ""):
                try:
                    rewards.append(Reward(data=FixedReward(currency="Chips", amount=float(chips_str_2))))
                except ValueError:
                    pass

            pack_id = get(row, "pack_id", "")
            num_packs_str = get(row, "num_packs", "")
            if pack_id and pack_id not in ("nan", "") and num_packs_str and num_packs_str not in ("nan", "0", ""):
                try:
                    rewards.append(Reward(data=CollectableSellPacksReward(
                        pack_id=pack_id,
                        num_packs=int(float(num_packs_str)),
                    )))
                except ValueError:
                    pass

            if not rewards:
                rewards = [Reward(data=FixedReward(currency="Chips", amount=0.0))]

            # Прочие поля
            is_last = get(row, "is_last_node", "false").lower() in ("true", "1", "yes", "да")
            resegment = get(row, "resegment_flag", "false").lower() in ("true", "1", "yes", "да")
            mini_game = get(row, "mini_game", "FlatReward") or "FlatReward"
            btn_text = get(row, "button_action_text", "PLAY NOW!") or "PLAY NOW!"
            btn_type = get(row, "button_action_type", "")
            btn_data = get(row, "button_action_data", "")
            contribution = get(row, "contribution_level", "Node") or "Node"
            custom_texts = parse_comma_separated_list(get(row, "custom_texts", ""))
            possible_item = get(row, "possible_item_collect", "")

            node = ProgressNode(
                node_id=node_id,
                next_node_ids=next_node_ids,
                game_list=game_list,
                min_bet=min_bet,
                goal=goal,
                rewards=rewards,
                is_last_node=is_last,
                resegment_flag=resegment,
                mini_game=mini_game,
                contribution_level=contribution,
                button_action_text=btn_text,
                button_action_type=btn_type,
                button_action_data=btn_data,
                custom_texts=custom_texts,
                possible_item_collect=possible_item,
            )

            if not segment.stages:
                segment.stages = [Stage(stage_id=1)]
            segment.stages[0].nodes.append(node)
            nodes_created += 1

        except Exception as e:
            errors.append(f"Строка {idx+2}: ошибка — {e}")

    # Сохраняем изменения обратно в cfg
    app_state.update_event(event_idx, current_event)

    if nodes_created > 0 or segments_created > 0:
        st.success(f"✅ Импорт завершён: сегментов — {segments_created}, узлов — {nodes_created}")
    if errors:
        st.warning(f"⚠️ Предупреждений: {len(errors)}")
        with st.expander("Показать подробности"):
            for err in errors:
                st.write(f"- {err}")
    if nodes_created > 0:
        st.balloons()
        st.rerun()
