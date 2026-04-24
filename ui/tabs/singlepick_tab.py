import copy
import json
import streamlit as st
from dataclasses import dataclass, field
from typing import Optional, Tuple

from models.singlepick import (
    SinglePickConfig, ConfigSet, PickersConfig, WheelConfig,
    RewardPick, JackpotPick, RetryPick, Pick,
    FixedJackpot, CIJackpot,
    FixedSPReward, RtpSPReward, PurchaseSPReward, SPReward,
    Wedge,
)
from services.singlepick_validator import validate_singlepick, validate_configset_name
from services.json_io import load_config_from_json, validate_config
from ui.widgets.singlepick_reward_widget import render_sp_reward_widget
from ui.widgets.singlepick_rewards_editor import render_sp_rewards_editor, get_default_sp_reward


# ── Состояние ────────────────────────────────────────────────────────────────

@dataclass
class SinglePickState:
    config: SinglePickConfig
    # Что сейчас открыто в правой панели:
    #   ("", "", -1)          — ничего
    #   ("NEW_CS", "", -1)    — форма нового ConfigSet
    #   ("cs_name", "", -1)   — настройки ConfigSet (TotalPickOnBoard и т.д.)
    #   ("cs_name", "pick", i)  — редактор пика i
    #   ("cs_name", "wedge", i) — редактор сектора i
    editing: Tuple[str, str, int]
    confirm_delete_cs: str
    confirm_type_change: bool

    # Staged-конфиг: исходный большой файл
    staged_cfg: Optional[dict] = None          # полный исходный конфиг (сырой dict)
    staged_cs_name: Optional[str] = None       # имя выбранного ConfigSet в staged_cfg


def get_singlepick_state() -> SinglePickState:
    if "singlepick_state" not in st.session_state:
        st.session_state["singlepick_state"] = SinglePickState(
            config=SinglePickConfig(config_sets={}),
            editing=("", "", -1),
            confirm_delete_cs="",
            confirm_type_change=False,
            staged_cfg=None,
            staged_cs_name=None,
        )
    return st.session_state["singlepick_state"]


def move_pick_up(picks: list, index: int) -> None:
    if 0 < index < len(picks):
        picks[index - 1], picks[index] = picks[index], picks[index - 1]


def _default_pickers_config() -> PickersConfig:
    """Создаёт PickersConfig с дефолтным набором пиков."""
    return PickersConfig(
        picks=[
            RewardPick(
                reward=[FixedSPReward(currency="Chips", amount=1000000)],
                weight=1,
                possible_max=1,
            ),
            JackpotPick(
                jackpot=CIJackpot(min=0, max=0, ci_min=0, ci_max=0),
                weight=0,
                possible_max=0,
            ),
            RetryPick(
                reward=[],
                weight=0,
                possible_max=0,
            ),
        ],
        total_pick_on_board=1,
        pick_until_win=0,
    )


def _get_staged_cs_names(state: SinglePickState) -> list:
    """Возвращает список имён ConfigSet из staged конфига."""
    if state.staged_cfg is None:
        return []
    return list(state.staged_cfg.get("ConfigSets", {}).keys())


def _load_staged_cs(state: SinglePickState, cs_name: str) -> None:
    """Загружает один ConfigSet из staged конфига в редактор."""
    if state.staged_cfg is None:
        return
    cs_raw = state.staged_cfg.get("ConfigSets", {}).get(cs_name)
    if cs_raw is None:
        return
    state.staged_cs_name = cs_name
    single_cfg = {"ConfigSets": {cs_name: copy.deepcopy(cs_raw)}}
    config = SinglePickConfig.from_dict(single_cfg)
    state.config = config
    state.editing = ("", "", -1)


def _apply_cs_to_staged(state: SinglePickState) -> bool:
    """Применяет отредактированный ConfigSet обратно в staged конфиг."""
    if state.staged_cfg is None or state.staged_cs_name is None:
        return False
    if state.staged_cs_name not in state.staged_cfg.get("ConfigSets", {}):
        return False
    cs = state.config.config_sets.get(state.staged_cs_name)
    if cs is None:
        return False
    state.staged_cfg["ConfigSets"][state.staged_cs_name] = copy.deepcopy(cs.to_dict())
    return True


def _add_cs_to_staged(state: SinglePickState, cs_name: str, cs: ConfigSet) -> None:
    """Добавляет новый ConfigSet в staged конфиг и загружает его в редактор."""
    if state.staged_cfg is None:
        state.staged_cfg = {"ConfigSets": {}}
    state.staged_cfg.setdefault("ConfigSets", {})[cs_name] = copy.deepcopy(cs.to_dict())
    state.staged_cs_name = cs_name
    state.config = SinglePickConfig(config_sets={cs_name: copy.deepcopy(cs)})
    state.editing = (cs_name, "", -1)


def _get_staged_cfg_with_patch(state: SinglePickState) -> Optional[dict]:
    """Возвращает staged конфиг с применёнными изменениями текущего ConfigSet."""
    if state.staged_cfg is None:
        return None
    patched = copy.deepcopy(state.staged_cfg)
    if state.staged_cs_name and state.staged_cs_name in state.config.config_sets:
        cs = state.config.config_sets[state.staged_cs_name]
        patched["ConfigSets"][state.staged_cs_name] = copy.deepcopy(cs.to_dict())
    return patched


# ── Тулбар ───────────────────────────────────────────────────────────────────

def _render_toolbar(state: SinglePickState) -> None:
    with st.expander("🗂️ Загрузка конфига", expanded=True):
        col_new, col_upload, col_validate = st.columns([1, 3, 2])

        with col_new:
            if st.button("🆕 Новый конфиг", use_container_width=True, key="sp_new_config"):
                if len(state.config.config_sets) == 0:
                    state.config = SinglePickConfig(config_sets={})
                    state.editing = ("", "", -1)
                    state.staged_cfg = None
                    state.staged_cs_name = None
                    st.session_state.pop("sp_last_loaded_file", None)
                    st.rerun()
                else:
                    st.session_state["sp_confirm_reset"] = True
                    st.rerun()

        if st.session_state.get("sp_confirm_reset"):
            st.warning("Сбросить конфиг? Все данные будут потеряны.")
            cy, cn = st.columns(2)
            with cy:
                if st.button("✅ Да", key="sp_reset_yes"):
                    state.config = SinglePickConfig(config_sets={})
                    state.editing = ("", "", -1)
                    state.staged_cfg = None
                    state.staged_cs_name = None
                    del st.session_state["sp_confirm_reset"]
                    st.session_state.pop("sp_last_loaded_file", None)
                    st.rerun()
            with cn:
                if st.button("❌ Нет", key="sp_reset_no"):
                    del st.session_state["sp_confirm_reset"]
                    st.rerun()

        with col_upload:
            st.caption("Загрузка JSON конфига")
            uploaded = st.file_uploader(
                "📂 Загрузить JSON", type=["json"],
                key="sp_json_uploader", label_visibility="collapsed"
            )
            if uploaded:
                last = st.session_state.get("sp_last_loaded_file")
                if last != uploaded.name:
                    try:
                        data = load_config_from_json(uploaded.read())
                        config = SinglePickConfig.from_dict(data)
                        n_cs = len(config.config_sets)
                        if n_cs > 1:
                            # Большой конфиг — сохраняем как staged
                            state.staged_cfg = data
                            state.staged_cs_name = None
                            st.session_state["sp_last_loaded_file"] = uploaded.name
                            st.session_state.pop("sp_staged_selected_cs", None)
                            st.rerun()
                        else:
                            # Один или ноль ConfigSet — загружаем напрямую
                            state.config = config
                            state.staged_cfg = None
                            state.staged_cs_name = None
                            state.editing = ("", "", -1)
                            st.session_state["sp_last_loaded_file"] = uploaded.name
                            st.success(f"✅ Загружено ConfigSet-ов: {n_cs}")
                    except ValueError as e:
                        st.error(f"Файл не является SinglePick конфигом: {e}")
                    except Exception as e:
                        st.error(f"Ошибка загрузки: {e}")

        # Выбор ConfigSet из staged конфига
        if state.staged_cfg is not None:
            cs_names = _get_staged_cs_names(state)
            st.info(f"📦 Загружен большой конфиг «{st.session_state.get('sp_last_loaded_file', '')}» — {len(cs_names)} ConfigSet-ов. Выберите ConfigSet для редактирования.")
            col_sel, col_load, col_add = st.columns([3, 1, 1])
            with col_sel:
                selected_cs = st.selectbox(
                    "ConfigSet для редактирования",
                    options=cs_names,
                    key="sp_staged_cs_selector",
                    label_visibility="collapsed",
                )
            with col_load:
                if st.button("✏️ Открыть", use_container_width=True, key="sp_staged_load_btn"):
                    _load_staged_cs(state, selected_cs)
                    st.session_state["sp_staged_selected_cs"] = selected_cs
                    st.rerun()
            with col_add:
                if st.button("➕ Добавить", use_container_width=True, key="sp_staged_add_btn"):
                    st.session_state["sp_staged_creating_new"] = True
                    st.rerun()

            # Форма создания нового ConfigSet
            if st.session_state.get("sp_staged_creating_new"):
                with st.form(key="sp_staged_new_cs_form"):
                    st.subheader("➕ Новый ConfigSet")
                    new_cs_name = st.text_input("Имя ConfigSet", value="NewConfigSet")
                    new_cs_type = st.radio("Тип", ["Pickers", "Wheel"], horizontal=True)
                    
                    col_submit, col_cancel = st.columns(2)
                    with col_submit:
                        submitted = st.form_submit_button("💾 Создать и открыть")
                    with col_cancel:
                        cancelled = st.form_submit_button("❌ Отмена")
                    
                    if submitted:
                        err = validate_configset_name(new_cs_name, cs_names)
                        if err:
                            st.error(err)
                        else:
                            content = (
                                _default_pickers_config()
                                if new_cs_type == "Pickers"
                                else WheelConfig(wedges=[])
                            )
                            new_cs = ConfigSet(content=content)
                            _add_cs_to_staged(state, new_cs_name, new_cs)
                            st.session_state["sp_staged_selected_cs"] = new_cs_name
                            del st.session_state["sp_staged_creating_new"]
                            st.success(f"✅ ConfigSet '{new_cs_name}' добавлен")
                            st.rerun()
                    
                    if cancelled:
                        del st.session_state["sp_staged_creating_new"]
                        st.rerun()

            # Кнопка применить изменения обратно в staged
            if st.session_state.get("sp_staged_selected_cs") is not None:
                col_apply, col_info = st.columns([2, 3])
                with col_apply:
                    if st.button("💾 Применить изменения в исходный конфиг", use_container_width=True, key="sp_staged_apply_btn"):
                        ok = _apply_cs_to_staged(state)
                        if ok:
                            st.success("✅ Изменения применены в исходный конфиг")
                        else:
                            st.error("Не удалось применить изменения")
                with col_info:
                    loaded_cs = st.session_state["sp_staged_selected_cs"]
                    st.caption(f"Редактируется: **{loaded_cs}**  |  Всего ConfigSet-ов в исходнике: {len(cs_names)}")

        with col_validate:
            st.caption("Загрузка JSON схемы")
            schema_file = st.file_uploader(
                "📋 Схема для валидации", type=["json"],
                key="sp_schema_uploader", label_visibility="collapsed"
            )
            if st.button("✅ Проверить валидацию", use_container_width=True, key="sp_validate_btn"):
                # Встроенная валидация через singlepick_validator
                errors = validate_singlepick(state.config)
                if errors:
                    st.error(f"Найдено ошибок: {len(errors)}")
                    for e in errors:
                        st.warning(f"**[{e.configset_name}]** `{e.field}`: {e.message}")
                else:
                    # Если загружена схема — дополнительно проверяем по JSON Schema
                    if schema_file:
                        schema = json.loads(schema_file.read())
                        # Валидируем staged конфиг с патчем если он есть
                        if state.staged_cfg is not None:
                            cfg_to_validate = _get_staged_cfg_with_patch(state)
                            label = f"исходного конфига ({len(_get_staged_cs_names(state))} ConfigSet-ов)"
                        else:
                            cfg_to_validate = state.config.to_dict()
                            label = "конфига"
                        valid, msg = validate_config(cfg_to_validate, schema)
                        if valid:
                            st.success(f"Валиден ({label}, схема и логика)")
                        else:
                            st.error(f"Не валиден по схеме ({label}): {msg}")
                    else:
                        st.success("Валиден")




# ── Дерево (левая колонка) ────────────────────────────────────────────────────

def _render_tree(state: SinglePickState) -> None:
    st.subheader("🌳 Структура")

    if st.button("➕ Добавить ConfigSet", key="sp_add_cs", use_container_width=True):
        state.editing = ("NEW_CS", "", -1)
        st.rerun()

    if not state.config.config_sets:
        st.info("📭 Нет ConfigSet-ов")
        return

    for cs_name, cs in state.config.config_sets.items():
        is_pickers = isinstance(cs.content, PickersConfig)
        icon = "🃏" if is_pickers else "🎡"
        cs_type = "Pickers" if is_pickers else "Wheel"

        with st.expander(f"{icon} {cs_name}  `{cs_type}`", expanded=True):
            # Кнопки управления ConfigSet
            col_cfg, col_dup, col_del = st.columns([3, 1, 1])
            with col_cfg:
                if st.button("⚙️ Настройки", key=f"sp_cs_settings_{cs_name}", use_container_width=True):
                    state.editing = (cs_name, "", -1)
                    st.rerun()
            with col_dup:
                if st.button("📋", key=f"sp_cs_dup_{cs_name}", use_container_width=True, help="Дублировать ConfigSet"):
                    existing = list(state.config.config_sets.keys())
                    candidate = f"{cs_name}_copy"
                    counter = 2
                    while candidate in existing:
                        candidate = f"{cs_name}_copy{counter}"
                        counter += 1
                    new_cs = copy.deepcopy(cs)
                    # Вставляем сразу после оригинала
                    items = list(state.config.config_sets.items())
                    insert_at = next(i for i, (k, _) in enumerate(items) if k == cs_name) + 1
                    items.insert(insert_at, (candidate, new_cs))
                    state.config.config_sets = dict(items)
                    st.rerun()
            with col_del:
                if st.button("❌", key=f"sp_cs_del_{cs_name}", use_container_width=True):
                    state.confirm_delete_cs = cs_name
                    st.rerun()

            # Подтверждение удаления
            if state.confirm_delete_cs == cs_name:
                st.warning(f"Удалить «{cs_name}»?")
                cy, cn = st.columns(2)
                with cy:
                    if st.button("✅ Да", key=f"sp_del_yes_{cs_name}"):
                        del state.config.config_sets[cs_name]
                        if state.editing[0] == cs_name:
                            state.editing = ("", "", -1)
                        state.confirm_delete_cs = ""
                        st.rerun()
                with cn:
                    if st.button("❌ Нет", key=f"sp_del_no_{cs_name}"):
                        state.confirm_delete_cs = ""
                        st.rerun()

            # Содержимое
            if is_pickers:
                pickers = cs.content
                st.caption(f"TotalPickOnBoard: {pickers.total_pick_on_board}  |  PickUntilWin: {pickers.pick_until_win}")

                for i, pick in enumerate(pickers.picks):
                    pick_type = type(pick).__name__
                    label = f"🔹 {i+1}. {pick_type}  W:{pick.weight}  PM:{pick.possible_max}"
                    col_lbl, col_edit, col_dup, col_up, col_dn, col_del = st.columns([5, 1, 1, 1, 1, 1])
                    with col_lbl:
                        st.write(label)
                    with col_edit:
                        if st.button("✏️", key=f"sp_{cs_name}_pick_{i}_edit"):
                            state.editing = (cs_name, "pick", i)
                            st.rerun()
                    with col_dup:
                        if st.button("📋", key=f"sp_{cs_name}_pick_{i}_dup", help="Дублировать пик"):
                            new_pick = copy.deepcopy(pick)
                            pickers.picks.insert(i + 1, new_pick)
                            st.rerun()
                    with col_up:
                        if i > 0 and st.button("↑", key=f"sp_{cs_name}_pick_{i}_up"):
                            move_pick_up(pickers.picks, i)
                            st.rerun()
                    with col_dn:
                        if i < len(pickers.picks) - 1 and st.button("↓", key=f"sp_{cs_name}_pick_{i}_dn"):
                            move_pick_up(pickers.picks, i + 1)
                            st.rerun()
                    with col_del:
                        if st.button("❌", key=f"sp_{cs_name}_pick_{i}_del"):
                            pickers.picks.pop(i)
                            if state.editing == (cs_name, "pick", i):
                                state.editing = (cs_name, "", -1)
                            st.rerun()

                # Добавить пик
                col_sel, col_add = st.columns([3, 1])
                with col_sel:
                    new_type = st.selectbox(
                        "Тип пика", ["RewardPick", "JackpotPick", "RetryPick"],
                        key=f"sp_{cs_name}_new_pick_type", label_visibility="collapsed"
                    )
                with col_add:
                    if st.button("➕", key=f"sp_{cs_name}_add_pick", use_container_width=True):
                        if new_type == "RewardPick":
                            p = RewardPick(reward=[FixedSPReward(currency="Chips", amount=1000000)], weight=1, possible_max=0)
                        elif new_type == "JackpotPick":
                            p = JackpotPick(jackpot=FixedJackpot(min=0, max=0), weight=1, possible_max=0)
                        else:
                            p = RetryPick(reward=[], weight=0, possible_max=0)
                        pickers.picks.append(p)
                        state.editing = (cs_name, "pick", len(pickers.picks) - 1)
                        st.rerun()

            else:  # Wheel
                wheel = cs.content
                for i, wedge in enumerate(wheel.wedges):
                    label = f"🔸 {i+1}. Wedge  W:{wedge.weight}  Наград:{len(wedge.reward)}"
                    col_lbl, col_edit, col_dup, col_del = st.columns([6, 1, 1, 1])
                    with col_lbl:
                        st.write(label)
                    with col_edit:
                        if st.button("✏️", key=f"sp_{cs_name}_wedge_{i}_edit"):
                            state.editing = (cs_name, "wedge", i)
                            st.rerun()
                    with col_dup:
                        if st.button("📋", key=f"sp_{cs_name}_wedge_{i}_dup", help="Дублировать сектор"):
                            new_wedge = copy.deepcopy(wedge)
                            wheel.wedges.insert(i + 1, new_wedge)
                            st.rerun()
                    with col_del:
                        if st.button("❌", key=f"sp_{cs_name}_wedge_{i}_del"):
                            wheel.wedges.pop(i)
                            if state.editing == (cs_name, "wedge", i):
                                state.editing = (cs_name, "", -1)
                            st.rerun()

                if st.button("➕ Добавить сектор", key=f"sp_{cs_name}_add_wedge", use_container_width=True):
                    wheel.wedges.append(Wedge(reward=[FixedSPReward(currency="Chips", amount=1000000)], weight=1))
                    state.editing = (cs_name, "wedge", len(wheel.wedges) - 1)
                    st.rerun()


# ── Правая панель ─────────────────────────────────────────────────────────────

def _render_editor(state: SinglePickState) -> None:
    cs_name, item_type, item_idx = state.editing

    # ── Новый ConfigSet ──
    if cs_name == "NEW_CS":
        st.subheader("➕ Новый ConfigSet")
        name_input = st.text_input("Имя ConfigSet", key="sp_new_cs_name")
        type_radio = st.radio("Тип", ["Pickers", "Wheel"], horizontal=True, key="sp_new_cs_type")
        col_s, col_c = st.columns(2)
        with col_s:
            if st.button("💾 Создать", key="sp_create_cs"):
                err = validate_configset_name(name_input, list(state.config.config_sets.keys()))
                if err:
                    st.error(err)
                else:
                    content = (
                        _default_pickers_config()
                        if type_radio == "Pickers"
                        else WheelConfig(wedges=[])
                    )
                    state.config.config_sets[name_input] = ConfigSet(content=content)
                    state.editing = (name_input, "", -1)
                    st.rerun()
        with col_c:
            if st.button("❌ Отмена", key="sp_cancel_new_cs"):
                state.editing = ("", "", -1)
                st.rerun()
        return

    if not cs_name or cs_name not in state.config.config_sets:
        st.info("Выберите элемент в дереве для редактирования.")
        return

    cs = state.config.config_sets[cs_name]

    # ── Настройки ConfigSet ──
    if item_type == "":
        st.subheader(f"⚙️ {cs_name}")

        # Смена типа
        current_type = "Pickers" if isinstance(cs.content, PickersConfig) else "Wheel"
        type_radio = st.radio(
            "Тип", ["Pickers", "Wheel"],
            index=0 if current_type == "Pickers" else 1,
            horizontal=True, key="sp_edit_cs_type"
        )

        if type_radio != current_type and not state.confirm_type_change:
            state.confirm_type_change = True
            st.rerun()

        if state.confirm_type_change:
            st.warning("Смена типа удалит все текущие данные. Продолжить?")
            cy, cn = st.columns(2)
            with cy:
                if st.button("✅ Да", key="sp_type_yes"):
                    cs.content = (
                        _default_pickers_config()
                        if type_radio == "Pickers"
                        else WheelConfig(wedges=[])
                    )
                    state.confirm_type_change = False
                    st.rerun()
            with cn:
                if st.button("❌ Нет", key="sp_type_no"):
                    state.confirm_type_change = False
                    st.rerun()
            return

        if isinstance(cs.content, PickersConfig):
            pickers = cs.content
            col1, col2 = st.columns(2)
            with col1:
                total = st.number_input(
                    "TotalPickOnBoard", value=pickers.total_pick_on_board,
                    min_value=1, step=1, key=f"sp_{cs_name}_total"
                )
                pickers.total_pick_on_board = total
            with col2:
                until_win = st.number_input(
                    "PickUntilWin", value=pickers.pick_until_win,
                    min_value=0, step=1, key=f"sp_{cs_name}_until_win"
                )
                pickers.pick_until_win = until_win
        return

    # ── Редактор пика ──
    if item_type == "pick":
        if not isinstance(cs.content, PickersConfig):
            return
        pickers = cs.content
        if item_idx < 0 or item_idx >= len(pickers.picks):
            st.warning("Пик не найден.")
            return
        pick = pickers.picks[item_idx]
        pick_type = type(pick).__name__
        st.subheader(f"✏️ {cs_name}  →  {pick_type} #{item_idx + 1}")

        if isinstance(pick, RewardPick):
            _render_reward_pick_form(state, pickers, item_idx, pick)
        elif isinstance(pick, JackpotPick):
            _render_jackpot_pick_form(state, pickers, item_idx, pick)
        elif isinstance(pick, RetryPick):
            _render_retry_pick_form(state, pickers, item_idx, pick)
        return

    # ── Редактор сектора ──
    if item_type == "wedge":
        if not isinstance(cs.content, WheelConfig):
            return
        wheel = cs.content
        if item_idx < 0 or item_idx >= len(wheel.wedges):
            st.warning("Сектор не найден.")
            return
        wedge = wheel.wedges[item_idx]
        st.subheader(f"✏️ {cs_name}  →  Wedge #{item_idx + 1}")
        _render_wedge_form(state, wheel, item_idx, wedge)


# ── Формы редактирования ──────────────────────────────────────────────────────

def _render_reward_pick_form(state: SinglePickState, pickers: PickersConfig, i: int, pick: RewardPick) -> None:
    col1, col2 = st.columns(2)
    with col1:
        pick.weight = st.number_input(
            "Weight", value=pick.weight, min_value=0, step=1,
            key=f"sp_{state.editing[0]}_pick_{i}_weight"
        )
    with col2:
        pick.possible_max = st.number_input(
            "PossibleMax", value=pick.possible_max, min_value=0, step=1,
            key=f"sp_{state.editing[0]}_pick_{i}_pmax"
        )

    # Синхронизируем session_state с текущим списком наград пика
    rewards_key = f"sp_{state.editing[0]}_pick_{i}_sp_rewards"
    if rewards_key not in st.session_state:
        st.session_state[rewards_key] = list(pick.reward)

    pick.reward = render_sp_rewards_editor(
        prefix=f"sp_{state.editing[0]}_pick_{i}",
        existing_rewards=pick.reward,
    )


def _render_jackpot_pick_form(state: SinglePickState, pickers: PickersConfig, i: int, pick: JackpotPick) -> None:
    col1, col2 = st.columns(2)
    with col1:
        pick.weight = st.number_input(
            "Weight", value=pick.weight, min_value=0, step=1,
            key=f"sp_{state.editing[0]}_pick_{i}_weight"
        )
    with col2:
        pick.possible_max = st.number_input(
            "PossibleMax", value=pick.possible_max, min_value=0, step=1,
            key=f"sp_{state.editing[0]}_pick_{i}_pmax"
        )

    cur_jtype = "FixedJackpot" if isinstance(pick.jackpot, FixedJackpot) else "CIJackpot"
    jtype = st.radio(
        "Тип джекпота", ["FixedJackpot", "CIJackpot"],
        index=0 if cur_jtype == "FixedJackpot" else 1,
        horizontal=True, key=f"sp_{state.editing[0]}_pick_{i}_jtype"
    )
    if jtype != cur_jtype:
        pick.jackpot = FixedJackpot(min=0, max=0) if jtype == "FixedJackpot" else CIJackpot(min=0, max=0, ci_min=0, ci_max=0)
        st.rerun()

    if isinstance(pick.jackpot, FixedJackpot):
        col1, col2 = st.columns(2)
        with col1:
            pick.jackpot.min = st.number_input("Min", value=pick.jackpot.min, min_value=0, step=1, key=f"sp_{state.editing[0]}_pick_{i}_jmin")
        with col2:
            pick.jackpot.max = st.number_input("Max", value=pick.jackpot.max, min_value=0, step=1, key=f"sp_{state.editing[0]}_pick_{i}_jmax")
        if pick.jackpot.min > pick.jackpot.max:
            st.error("Min не может быть больше Max")
    else:
        col1, col2 = st.columns(2)
        with col1:
            pick.jackpot.min = st.number_input("Min", value=pick.jackpot.min, min_value=0, step=1, key=f"sp_{state.editing[0]}_pick_{i}_jmin")
        with col2:
            pick.jackpot.max = st.number_input("Max", value=pick.jackpot.max, min_value=0, step=1, key=f"sp_{state.editing[0]}_pick_{i}_jmax")
        col3, col4 = st.columns(2)
        with col3:
            pick.jackpot.ci_min = st.number_input("CIMin", value=pick.jackpot.ci_min, min_value=0, step=1, key=f"sp_{state.editing[0]}_pick_{i}_cimin")
        with col4:
            pick.jackpot.ci_max = st.number_input("CIMax", value=pick.jackpot.ci_max, min_value=0, step=1, key=f"sp_{state.editing[0]}_pick_{i}_cimax")
        if pick.jackpot.min > pick.jackpot.max:
            st.error("Min не может быть больше Max")


def _render_retry_pick_form(state: SinglePickState, pickers: PickersConfig, i: int, pick: RetryPick) -> None:
    col1, col2 = st.columns(2)
    with col1:
        pick.weight = st.number_input(
            "Weight", value=pick.weight, min_value=0, step=1,
            key=f"sp_{state.editing[0]}_pick_{i}_weight"
        )
    with col2:
        pick.possible_max = st.number_input(
            "PossibleMax", value=pick.possible_max, min_value=0, step=1,
            key=f"sp_{state.editing[0]}_pick_{i}_pmax"
        )

    st.caption("Награды необязательны")
    pick.reward = render_sp_rewards_editor(
        prefix=f"sp_{state.editing[0]}_pick_{i}",
        existing_rewards=pick.reward,
    )


def _render_wedge_form(state: SinglePickState, wheel: WheelConfig, i: int, wedge: Wedge) -> None:
    wedge.weight = st.number_input(
        "Weight", value=wedge.weight, min_value=0, step=1,
        key=f"sp_{state.editing[0]}_wedge_{i}_weight"
    )

    wedge.reward = render_sp_rewards_editor(
        prefix=f"sp_{state.editing[0]}_wedge_{i}",
        existing_rewards=wedge.reward,
    )


from ui.common import inject_sticky_right_column


# ── Точка входа ───────────────────────────────────────────────────────────────

def render_singlepick_tab() -> None:
    state = get_singlepick_state()
    inject_sticky_right_column()

    _render_toolbar(state)

    st.divider()

    left_col, right_col = st.columns([2, 3])

    with left_col:
        _render_tree(state)

    with right_col:
        _render_editor(state)
