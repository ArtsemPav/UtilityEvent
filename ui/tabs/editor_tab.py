import streamlit as st
from services.state_manager import AppState
from models.event import PossibleNodeEventData, Segment, Stage, make_node_event
from models.nodes import Node
from ui.widgets.node_editor import render_node_editor
from ui.widgets.event_tree import render_event_tree
from utils.helpers import parse_comma_separated_list
from utils.constants import DEFAULT_VIP_RANGE

def render_editor_tab():
    app_state = AppState.get_instance()

    # Статусная строка — читаем только сырые данные, без десериализации
    col1, col2, col3 = st.columns(3)
    with col1:
        events_raw = app_state.get_events_raw()
        st.info(f"📊 Всего событий: {len(events_raw)}")
    with col2:
        cur_idx = app_state.get_current_event_idx()
        if cur_idx >= 0 and cur_idx < len(events_raw):
            cur_event_id = events_raw[cur_idx].get("PossibleNodeEventData", {}).get("EventID", "?")
            st.info(f"✏️ Текущее: {cur_event_id}")
        else:
            st.info("✏️ Нет текущего события")
    with col3:
        ctx = app_state.get_editing_context()
        if ctx:
            mode = f"Редактирование {ctx['type']}"
        else:
            mode = "Создание"
        st.info(f"📌 Режим: {mode}")

    st.divider()

    left_col, right_col = st.columns([2, 1])

    with left_col:
        # ШАГ 1: Событие
        ctx = app_state.get_editing_context()
        editing_event = (ctx is not None and ctx["type"] == "event")
        with st.expander("📋 ШАГ 1: Создание / редактирование события", expanded=(ctx is None or editing_event)):
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
                            )
                            app_state.add_event(new_event)
                            st.success("✅ Событие добавлено")
                        st.rerun()

            if editing_event and st.button("❌ Отменить редактирование"):
                app_state.clear_editing()
                st.rerun()

        # ШАГ 2: Сегмент
        ctx = app_state.get_editing_context()
        editing_segment = (ctx is not None and ctx["type"] == "segment")
        current_event = app_state.get_current_event()

        def has_segment_type_conflict(event: PossibleNodeEventData, new_vip_range: str, old_name: str = None) -> tuple[bool, str]:
            """
            Проверяет конфликт типов сегментов.
            Возвращает (True, сообщение) если конфликт есть, иначе (False, "").
            """
            vip_count = 0
            non_vip_count = 0
            for name, seg in event.segments.items():
                if name == old_name:
                    continue
                if seg.vip_range == "":
                    non_vip_count += 1
                else:
                    vip_count += 1

            is_new_non_vip = (new_vip_range == "")

            # Если новый сегмент без VIP
            if is_new_non_vip:
                if vip_count > 0:
                    return True, "❌ Нельзя добавить сегмент без VIP, когда уже есть VIP-сегменты."
                if non_vip_count >= 1:
                    return True, "❌ В событии уже есть сегмент без VIP. Можно иметь только один такой сегмент."
            else:
                # Новый сегмент с VIP
                if non_vip_count > 0:
                    return True, "❌ Нельзя добавить VIP-сегмент, когда уже есть сегмент без VIP."
            return False, ""

        if current_event:
            with st.expander("📁 ШАГ 2: Создание / редактирование сегмента", expanded=editing_segment):
                if editing_segment:
                    event_idx, old_name, seg_obj = app_state.get_editing_segment_copy()
                    st.write(f"✏️ Редактирование сегмента: {seg_obj.name}")
                    if seg_obj.vip_range:
                        default_segment_type = "Стандартный (с VIP)"
                    else:
                        default_segment_type = "RandomSegmentName (без VIP)"
                else:
                    seg_obj = None
                    default_segment_type = "Стандартный (с VIP)"

                segment_type_key = "segment_type_selector"
                if segment_type_key not in st.session_state:
                    st.session_state[segment_type_key] = default_segment_type

                segment_type = st.radio(
                    "Тип сегмента",
                    options=["Стандартный (с VIP)", "RandomSegmentName (без VIP)"],
                    horizontal=True,
                    key=segment_type_key
                )

                with st.form(key="segment_form"):
                    if segment_type == "Стандартный (с VIP)":
                        col_a, col_b = st.columns(2)
                        with col_a:
                            seg_name = st.text_input(
                                "Имя сегмента",
                                value=seg_obj.name if seg_obj else "VIP1_10"
                            )
                        with col_b:
                            vip_range = st.text_input(
                                "VIP Range",
                                value=seg_obj.vip_range if seg_obj and seg_obj.vip_range else DEFAULT_VIP_RANGE
                            )
                    else:
                        col_a, _ = st.columns(2)
                        with col_a:
                            seg_name = st.text_input(
                                "Имя сегмента",
                                value=seg_obj.name if seg_obj else "RandomSegmentName"
                            )
                        vip_range = ""

                    submitted = st.form_submit_button(
                        "💾 Сохранить сегмент" if editing_segment else "➕ Добавить сегмент"
                    )
                    if submitted:
                        conflict, msg = has_segment_type_conflict(
                            current_event, vip_range,
                            old_name if editing_segment else None
                        )
                        if conflict:
                            st.error(msg)
                        else:
                            if segment_type == "Стандартный (с VIP)":
                                new_seg = Segment(name=seg_name, vip_range=vip_range)
                            else:
                                new_seg = Segment(name=seg_name, vip_range="")
                            if editing_segment:
                                seg_obj.name = seg_name
                                seg_obj.vip_range = vip_range if segment_type == "Стандартный (с VIP)" else ""
                                app_state.apply_editing()
                                st.success("✅ Сегмент обновлён")
                            else:
                                app_state.add_segment(app_state.get_current_event_idx(), new_seg)
                                st.success("✅ Сегмент добавлен")
                            if segment_type_key in st.session_state:
                                del st.session_state[segment_type_key]
                            st.rerun()

                if editing_segment and st.button("❌ Отменить редактирование сегмента"):
                    if segment_type_key in st.session_state:
                        del st.session_state[segment_type_key]
                    app_state.clear_editing()
                    st.rerun()

        # ШАГ 3: Узел
        ctx = app_state.get_editing_context()
        editing_node = (ctx is not None and ctx["type"] == "node")
        current_segment = app_state.get_current_segment()
        if current_event and current_segment:
            with st.expander("🔧 ШАГ 3: Создание / редактирование ноды", expanded=editing_node):
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
                    st.rerun()

                if editing_node and st.button("❌ Отменить редактирование ноды"):
                    app_state.clear_editing()
                    st.rerun()

        # Кнопки управления
        st.divider()
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🔄 Начать новое событие", use_container_width=True):
                app_state.set_current_event_idx(-1)
                app_state.clear_editing()
                st.rerun()
        with c2:
            if st.button("➕ Добавить ещё сегмент", use_container_width=True):
                app_state.clear_editing()
                st.rerun()

    with right_col:
        st.subheader("🌳 Структура событий")
        render_event_tree()