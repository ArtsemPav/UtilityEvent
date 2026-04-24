import streamlit as st
import json
from services.state_manager import AppState
from services.json_io import load_config_from_json, validate_config
from models.event import PossibleNodeEventData, Segment, Stage, make_node_event, get_default_time_warning
from models.nodes import Node
from ui.widgets.node_editor import render_node_editor
from ui.widgets.event_tree import render_event_tree
from ui.import_tab import render_batch_import_panel
from services.json_io import load_config_from_json
from utils.helpers import parse_comma_separated_list
from utils.constants import DEFAULT_VIP_RANGE, SEGMENT_INFO_TYPES, SEGMENT_INFO_NONE
from ui.common import inject_sticky_right_column

def render_editor_tab():
    app_state = AppState.get_instance()
    inject_sticky_right_column()

    # Загрузка JSON + счётчик событий
    with st.expander("🗂️ Загрузка и валидация конфига", expanded=False):
        col_new, col_upload, col_validate = st.columns([1, 2, 2])
        with col_new:
            if st.button("🆕 Новый конфиг", use_container_width=True):
                events_raw = app_state.get_events_raw()
                if len(events_raw) == 0:
                    app_state.set_cfg({"Events": [], "IsFallbackConfig": False})
                    app_state.clear_staged()
                    app_state.set_current_event_idx(-1)
                    app_state.clear_editing()
                    st.session_state["creating_event"] = False
                    st.session_state["creating_segment"] = False
                    st.session_state["creating_node"] = False
                    st.session_state["batch_import_event_idx"] = -1
                    st.session_state.pop("editor_last_loaded_file", None)
                    st.rerun()
                else:
                    st.session_state["editor_confirm_reset"] = True
                    st.rerun()

        if st.session_state.get("editor_confirm_reset"):
            st.warning("Сбросить конфиг? Все данные будут потеряны.")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("✅ Да", key="editor_reset_yes"):
                    app_state.set_cfg({"Events": [], "IsFallbackConfig": False})
                    app_state.clear_staged()
                    app_state.set_current_event_idx(-1)
                    app_state.clear_editing()
                    st.session_state["creating_event"] = False
                    st.session_state["creating_segment"] = False
                    st.session_state["creating_node"] = False
                    st.session_state["batch_import_event_idx"] = -1
                    st.session_state.pop("editor_last_loaded_file", None)
                    del st.session_state["editor_confirm_reset"]
                    st.rerun()
            with col_no:
                if st.button("❌ Нет", key="editor_reset_no"):
                    del st.session_state["editor_confirm_reset"]
                    st.rerun()
        with col_upload:
            st.caption("Загрузка JSON конфига")
            uploaded = st.file_uploader("📂 Загрузить JSON", type=["json"], key="editor_json_uploader", label_visibility="collapsed")
            if uploaded:
                last = st.session_state.get("editor_last_loaded_file")
                if last != uploaded.name:
                    try:
                        with st.spinner("Загрузка JSON..."):
                            cfg = load_config_from_json(uploaded.read())
                        n_events = len(cfg.get("Events", []))
                        st.session_state["editor_last_loaded_file"] = uploaded.name
                        if n_events > 1:
                            # Большой конфиг — сохраняем как staged, показываем выбор события
                            app_state.set_staged_cfg(cfg)
                            st.session_state["editor_staged_file_name"] = uploaded.name
                            st.session_state.pop("editor_staged_selected_idx", None)
                            st.rerun()
                        else:
                            # Один или ноль событий — загружаем напрямую
                            app_state.set_cfg(cfg)
                            app_state.clear_staged()
                            st.success(f"✅ JSON загружен ({n_events} событий)")
                    except Exception as e:
                        st.error(f"Ошибка: {e}")

        # Выбор события из staged конфига
        staged = app_state.get_staged_cfg()
        if staged is not None:
            event_ids = app_state.get_staged_event_ids()
            st.info(f"📦 Загружен большой конфиг «{st.session_state.get('editor_staged_file_name', '')}» — {len(event_ids)} событий. Выберите событие для редактирования.")
            col_sel, col_load, col_add = st.columns([3, 1, 1])
            with col_sel:
                selected_event_id = st.selectbox(
                    "Событие для редактирования",
                    options=event_ids,
                    key="editor_staged_event_selector",
                    label_visibility="collapsed",
                )
            with col_load:
                if st.button("✏️ Открыть", use_container_width=True, key="editor_staged_load_btn"):
                    idx = event_ids.index(selected_event_id)
                    app_state.load_staged_event(idx)
                    st.session_state["editor_staged_selected_idx"] = idx
                    st.rerun()
            with col_add:
                if st.button("➕ Добавить", use_container_width=True, key="editor_staged_add_btn"):
                    st.session_state["editor_staged_creating_new"] = True
                    st.rerun()

            # Форма создания нового события
            if st.session_state.get("editor_staged_creating_new"):
                with st.form(key="editor_staged_new_event_form"):
                    st.subheader("➕ Новое событие")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        new_event_id = st.text_input("EventID", value="NewEvent")
                        new_min_level = st.number_input("MinLevel", value=1, min_value=1)
                        new_segment = st.text_input("Segment", value="Default")
                    with col_b:
                        new_content_key = st.text_input("ContentKey", value="NewEvent")
                        new_repeats = st.number_input("NumberOfRepeats", value=-1)
                    
                    col_submit, col_cancel = st.columns(2)
                    with col_submit:
                        submitted = st.form_submit_button("💾 Создать и открыть")
                    with col_cancel:
                        cancelled = st.form_submit_button("❌ Отмена")
                    
                    if submitted:
                        # Проверка на дубликат EventID
                        if new_event_id in event_ids:
                            st.error(f"❌ Событие с EventID '{new_event_id}' уже существует")
                        else:
                            new_event = make_node_event(
                                event_id=new_event_id,
                                min_level=int(new_min_level),
                                segment=new_segment,
                                asset_bundle_path=f"_events/{new_event_id}",
                                blocker_prefab_path=f"Dialogs/{new_event_id}_Dialog",
                                roundel_prefab_path=f"Roundels/{new_event_id}_Roundel",
                                event_card_prefab_path="",
                                node_completion_prefab_path=f"Dialogs/{new_event_id}_Dialog",
                                content_key=new_content_key,
                                number_of_repeats=int(new_repeats),
                                entry_types=[],
                            )
                            app_state.add_new_event_to_staged(new_event)
                            st.session_state["editor_staged_selected_idx"] = len(event_ids)
                            del st.session_state["editor_staged_creating_new"]
                            st.success(f"✅ Событие '{new_event_id}' добавлено")
                            st.rerun()
                    
                    if cancelled:
                        del st.session_state["editor_staged_creating_new"]
                        st.rerun()

            # Кнопка применить изменения обратно в staged
            if st.session_state.get("editor_staged_selected_idx") is not None:
                col_apply, col_info = st.columns([2, 3])
                with col_apply:
                    if st.button("💾 Применить изменения в исходный конфиг", use_container_width=True, key="editor_staged_apply_btn"):
                        ok = app_state.apply_event_to_staged()
                        if ok:
                            st.success("✅ Изменения применены в исходный конфиг")
                        else:
                            st.error("Не удалось применить изменения")
                with col_info:
                    loaded_id = event_ids[st.session_state["editor_staged_selected_idx"]] \
                        if st.session_state["editor_staged_selected_idx"] < len(event_ids) else "?"
                    st.caption(f"Редактируется: **{loaded_id}**  |  Всего событий в исходнике: {len(event_ids)}")
        with col_validate:
            st.caption("Загрузка JSON схемы")
            schema_file = st.file_uploader("📋 Схема для валидации", type=["json"], key="editor_schema_uploader", label_visibility="collapsed")
            if st.button("✅ Проверить валидацию", use_container_width=True, key="editor_validate_btn"):
                schema = json.loads(schema_file.read()) if schema_file else None
                # Если есть staged конфиг — валидируем его (с патчем текущего события)
                staged = app_state.get_staged_cfg()
                if staged is not None:
                    cfg_to_validate = app_state.get_staged_cfg_with_patch()
                    label = f"исходного конфига ({len(cfg_to_validate.get('Events', []))} событий)"
                else:
                    cfg_to_validate = app_state.get_cfg()
                    label = "конфига"
                valid, msg = validate_config(cfg_to_validate, schema)
                if valid:
                    st.success(f"Валиден ({label})")
                else:
                    st.error(f"Не валиден ({label}): {msg}")


    st.divider()

    right_col, left_col = st.columns([2, 3])

    with left_col:
        # Пакетный импорт
        batch_import_idx = st.session_state.get("batch_import_event_idx", -1)
        if batch_import_idx >= 0:
            events_raw = app_state.get_events_raw()
            if batch_import_idx < len(events_raw):
                event_id_label = events_raw[batch_import_idx].get("PossibleNodeEventData", {}).get("EventID", "?")
                st.subheader(f"📥 Пакетный импорт → {event_id_label}")
                if st.button("✖ Закрыть импорт", key="close_batch_import"):
                    st.session_state["batch_import_event_idx"] = -1
                    st.rerun()
                render_batch_import_panel()
            else:
                st.session_state["batch_import_event_idx"] = -1
                st.rerun()
        else:
            # ШАГ 1: Событие
            ctx = app_state.get_editing_context()
            editing_event = (ctx is not None and ctx["type"] == "event")
            creating_event = st.session_state.get("creating_event", False)
            creating_segment = st.session_state.get("creating_segment", False)
            show_step1 = (editing_event or creating_event) and not creating_segment

            if show_step1:
                with st.expander("📋 ШАГ 1: Создание / редактирование события", expanded=True):
                    if editing_event:
                        event_obj = app_state.get_editing_event_copy()
                        st.write(f"✏️ Редактирование: {event_obj.event_id}")
                    else:
                        event_obj = None

                    def is_event_id_duplicate(new_event_id: str, current_event_id: str = None) -> bool:
                        events = app_state.get_events_raw()
                        for event_dict in events:
                            existing_id = event_dict.get("PossibleNodeEventData", {}).get("EventID")
                            if existing_id == new_event_id:
                                if current_event_id is not None and existing_id == current_event_id:
                                    continue
                                return True
                        return False

                    with st.form(key="event_form"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            event_id = st.text_input(
                                "EventID",
                                value=event_obj.event_id if event_obj else "MyEvent"
                            )
                            asset_bundle = st.text_input(
                                "AssetBundlePath",
                                value=event_obj.asset_bundle_path if event_obj else "_events/MyEvent"
                            )
                            blocker = st.text_input(
                                "BlockerPrefabPath",
                                value=event_obj.blocker_prefab_path if event_obj else "Dialogs/MyEvent_Dialog"
                            )
                            node_completion = st.text_input(
                                "NodeCompletionPrefabPath",
                                value=event_obj.node_completion_prefab_path if event_obj else "Dialogs/MyEvent_Dialog"
                            )
                            event_card = st.text_input(
                                "EventCardPrefabPath",
                                value=event_obj.event_card_prefab_path if event_obj else ""
                            )
                        with col_b:
                            roundel = st.text_input(
                                "RoundelPrefabPath",
                                value=event_obj.roundel_prefab_path if event_obj else "Roundels/MyEvent_Roundel"
                            )
                            content_key = st.text_input(
                                "ContentKey",
                                value=event_obj.content_key if event_obj else "MyEvent"
                            )
                            min_level = st.number_input(
                                "MinLevel",
                                value=event_obj.min_level if event_obj else 1,
                                min_value=1
                            )
                            repeats = st.number_input(
                                "NumberOfRepeats",
                                value=event_obj.number_of_repeats if event_obj else -1
                            )
                            segment = st.text_input(
                                "Segment (основной)",
                                value=event_obj.segment if event_obj else "Default"
                            )

                        entry_types_str = st.text_input(
                            "EntryTypes (через запятую)",
                            value=",".join(event_obj.entry_types) if event_obj else ""
                        )

                        col_c1, col_c2 = st.columns(2)
                        with col_c1:
                            is_roundel_hidden = st.checkbox(
                                "IsRoundelHidden",
                                value=event_obj.is_roundel_hidden if event_obj else False
                            )
                        with col_c2:
                            show_roundel_all = st.checkbox(
                                "ShowRoundelOnAllMachines",
                                value=event_obj.show_roundel_on_all_machines if event_obj else False
                            )

                        with st.expander("💵 CashOutEvent Settings", expanded=False):
                            col_d1, col_d2, col_d3 = st.columns(3)
                            with col_d1:
                                use_node_failed = st.checkbox(
                                    "UseNodeFailedNotification",
                                    value=event_obj.use_node_failed_notification if event_obj else False
                                )
                            with col_d2:
                                is_prize_pursuit = st.checkbox(
                                    "IsPrizePursuit",
                                    value=event_obj.is_prize_pursuit if event_obj else False
                                )
                            with col_d3:
                                use_force_landscape = st.checkbox(
                                    "UseForceLandscapeOnWeb",
                                    value=event_obj.use_force_landscape_on_web if event_obj else False
                                )

                        # Расширенные параметры события
                        if st.session_state.get("show_advanced", False):
                            with st.expander("⚙️ Расширенные параметры события", expanded=False):
                                col_e1, col_e2, col_e3 = st.columns(3)
                                with col_e1:
                                    starting_currency = st.number_input(
                                        "StartingEventCurrency",
                                        value=event_obj.starting_event_currency if event_obj else 0.0,
                                        step=0.1
                                    )
                                with col_e2:
                                    is_currency_event = st.checkbox(
                                        "IsCurrencyEvent",
                                        value=event_obj.is_currency_event if event_obj else False
                                    )
                                with col_e3:
                                    time_warning = st.text_input(
                                        "TimeWarning (ISO 8601)",
                                        value=event_obj.time_warning if event_obj else get_default_time_warning()
                                    )
                        else:
                            starting_currency = event_obj.starting_event_currency if event_obj else 0.0
                            is_currency_event = event_obj.is_currency_event if event_obj else False
                            time_warning = event_obj.time_warning if event_obj else get_default_time_warning()

                        submitted = st.form_submit_button(
                            "💾 Сохранить событие" if editing_event else "➕ Добавить событие"
                        )
                        if submitted:
                            entry_types = parse_comma_separated_list(entry_types_str)
                            current_id = event_obj.event_id if editing_event else None
                            if is_event_id_duplicate(event_id, current_id):
                                st.error(f"❌ Событие с EventID '{event_id}' уже существует. Используйте уникальное имя.")
                            else:
                                if editing_event:
                                    event_obj.event_id = event_id
                                    event_obj.min_level = int(min_level)
                                    event_obj.segment = segment
                                    event_obj.asset_bundle_path = asset_bundle
                                    event_obj.blocker_prefab_path = blocker
                                    event_obj.roundel_prefab_path = roundel
                                    event_obj.event_card_prefab_path = event_card
                                    event_obj.node_completion_prefab_path = node_completion
                                    event_obj.content_key = content_key
                                    event_obj.number_of_repeats = int(repeats)
                                    event_obj.entry_types = entry_types
                                    event_obj.is_roundel_hidden = is_roundel_hidden
                                    event_obj.use_node_failed_notification = use_node_failed
                                    event_obj.is_prize_pursuit = is_prize_pursuit
                                    event_obj.use_force_landscape_on_web = use_force_landscape
                                    event_obj.show_roundel_on_all_machines = show_roundel_all
                                    event_obj.starting_event_currency = starting_currency
                                    event_obj.is_currency_event = is_currency_event
                                    event_obj.time_warning = time_warning
                                    app_state.apply_editing()
                                    st.success("✅ Событие обновлено")
                                else:
                                    new_event = make_node_event(
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
                                        entry_types=entry_types,
                                        segments=event_obj.segments if event_obj else {},
                                        is_roundel_hidden=is_roundel_hidden,
                                        use_node_failed_notification=use_node_failed,
                                        is_prize_pursuit=is_prize_pursuit,
                                        use_force_landscape_on_web=use_force_landscape,
                                        show_roundel_on_all_machines=show_roundel_all,
                                        starting_event_currency=starting_currency,
                                        is_currency_event=is_currency_event,
                                        time_warning=time_warning,
                                    )
                                    app_state.add_event(new_event)
                                    st.success("✅ Событие добавлено")
                                st.session_state["creating_event"] = False
                                st.rerun()

                    if editing_event and st.button("❌ Отменить редактирование"):
                        app_state.clear_editing()
                        st.session_state["creating_event"] = False
                        st.rerun()

            # ШАГ 2: Сегмент
            ctx = app_state.get_editing_context()
            editing_segment = (ctx is not None and ctx["type"] == "segment")
            current_event = app_state.get_current_event()

            if current_event:
                show_step2 = editing_segment or creating_segment
                if show_step2:
                    with st.expander("📁 ШАГ 2: Создание / редактирование сегмента", expanded=True):
                        if editing_segment:
                            event_idx, old_name, seg_obj = app_state.get_editing_segment_copy()
                            st.write(f"✏️ Редактирование сегмента: {seg_obj.name}")
                            default_info_type = seg_obj.segment_info_type or SEGMENT_INFO_NONE
                        else:
                            seg_obj = None
                            old_name = None
                            default_info_type = "VIPRange"

                        # Список вариантов для selectbox: типы + "без инфо"
                        info_type_options = list(SEGMENT_INFO_TYPES.keys()) + [SEGMENT_INFO_NONE]
                        info_type_labels = [SEGMENT_INFO_TYPES[k] for k in SEGMENT_INFO_TYPES] + ["Без PossibleSegmentInfo"]

                        seg_info_type_key = "segment_info_type_selector"
                        if seg_info_type_key not in st.session_state:
                            st.session_state[seg_info_type_key] = (
                                default_info_type if default_info_type in info_type_options else "VIPRange"
                            )

                        selected_idx = info_type_options.index(st.session_state[seg_info_type_key]) \
                            if st.session_state[seg_info_type_key] in info_type_options else 0

                        chosen_label = st.radio(
                            "Тип PossibleSegmentInfo",
                            options=info_type_labels,
                            index=selected_idx,
                            horizontal=True,
                            key=seg_info_type_key + "_radio",
                        )
                        chosen_type = info_type_options[info_type_labels.index(chosen_label)]
                        st.session_state[seg_info_type_key] = chosen_type

                        with st.form(key="segment_form"):
                            col_a, col_b = st.columns(2)
                            with col_a:
                                seg_name = st.text_input(
                                    "Имя сегмента",
                                    value=seg_obj.name if seg_obj else (
                                        "RandomSegmentName" if chosen_type == SEGMENT_INFO_NONE else "VIP1_10"
                                    )
                                )
                            with col_b:
                                if chosen_type != SEGMENT_INFO_NONE:
                                    # Подставляем текущее значение если тип совпадает, иначе дефолт
                                    if seg_obj and seg_obj.segment_info_type == chosen_type:
                                        default_val = seg_obj.segment_info_value
                                    elif chosen_type == "VIPRange":
                                        default_val = DEFAULT_VIP_RANGE
                                    else:
                                        default_val = ""
                                    seg_info_value = st.text_input(
                                        SEGMENT_INFO_TYPES[chosen_type],
                                        value=default_val,
                                        placeholder="например: 1-10+" if chosen_type == "VIPRange" else "например: 100-500"
                                    )
                                else:
                                    seg_info_value = ""
                                    st.caption("PossibleSegmentInfo не будет добавлен в JSON")

                            submitted = st.form_submit_button(
                                "💾 Сохранить сегмент" if editing_segment else "➕ Добавить сегмент"
                            )
                            if submitted:
                                if not seg_name.strip():
                                    st.error("❌ Имя сегмента не может быть пустым.")
                                elif chosen_type != SEGMENT_INFO_NONE and not seg_info_value.strip():
                                    st.error(f"❌ Укажите значение для {SEGMENT_INFO_TYPES[chosen_type]}.")
                                else:
                                    new_seg = Segment(
                                        name=seg_name.strip(),
                                        segment_info_type=chosen_type,
                                        segment_info_value=seg_info_value.strip(),
                                    )
                                    if editing_segment:
                                        seg_obj.name = new_seg.name
                                        seg_obj.segment_info_type = new_seg.segment_info_type
                                        seg_obj.segment_info_value = new_seg.segment_info_value
                                        app_state.apply_editing()
                                        st.success("✅ Сегмент обновлён")
                                    else:
                                        app_state.add_segment(app_state.get_current_event_idx(), new_seg)
                                        st.success("✅ Сегмент добавлен")
                                    st.session_state.pop(seg_info_type_key, None)
                                    st.session_state.pop(seg_info_type_key + "_radio", None)
                                    st.session_state["creating_segment"] = False
                                    st.rerun()

                        if st.button("❌ Отменить", key="cancel_segment"):
                            st.session_state.pop(seg_info_type_key, None)
                            st.session_state.pop(seg_info_type_key + "_radio", None)
                            app_state.clear_editing()
                            st.session_state["creating_segment"] = False
                            st.rerun()

            # ШАГ 3: Узел
            ctx = app_state.get_editing_context()
            editing_node = (ctx is not None and ctx["type"] == "node")
            creating_node = st.session_state.get("creating_node", False)
            show_step3 = editing_node or creating_node

            if show_step3:
                with st.expander("🔧 ШАГ 3: Создание / редактирование ноды", expanded=True):
                    if editing_node:
                        _, _, _, _, node_obj = app_state.get_editing_node_copy()
                        node_type = type(node_obj).__name__
                        st.write(f"✏️ Редактирование {node_type} (ID: {node_obj.node_id})")
                    else:
                        node_type = st.radio(
                            "Тип ноды",
                            options=["ProgressNode", "EntriesNode", "DummyNode"],
                            horizontal=True
                        )
                        node_obj = None

                    result_node = render_node_editor(node_type, node_obj, key_prefix="edit_node" if editing_node else "new_node")

                    if result_node is not None:
                        if editing_node:
                            ctx = app_state.get_editing_context()
                            ctx["copy"] = result_node
                            app_state.apply_editing()
                            st.success("✅ Нода обновлена")
                        else:
                            app_state.add_node_to_current_segment(result_node)
                            st.success("✅ Нода добавлена")
                        st.session_state["creating_node"] = False
                        st.rerun()

                    if st.button("❌ Отменить", key="cancel_node"):
                        app_state.clear_editing()
                        st.session_state["creating_node"] = False
                        st.rerun()

            if not show_step1 and not show_step3 and not st.session_state.get("creating_segment", False):
                st.info("Выберите элемент в дереве для редактирования.")

    with right_col:
        st.subheader("🌳 Структура событий")
        render_event_tree()