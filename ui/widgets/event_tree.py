import streamlit as st
from services.state_manager import AppState

MAX_NODES_PER_SEGMENT = 10
MAX_EVENTS_VISIBLE = 20  # пагинация событий


def render_event_tree():
    app_state = AppState.get_instance()

    # Обработка отложенного открытия ноды (после clear_editing + rerun)
    pending = st.session_state.pop("_pending_edit_node", None)
    if pending is not None:
        idx, seg_name, stage_idx, node_idx = pending
        app_state.start_editing_node(idx, seg_name, stage_idx, node_idx)
        st.rerun()

    if st.button("➕ Добавить событие", key="tree_add_event", use_container_width=True):
        app_state.set_current_event_idx(-1)
        app_state.clear_editing()
        st.session_state["creating_event"] = True
        st.rerun()

    events_raw = app_state.get_events_raw()
    if not events_raw:
        st.info("📭 Нет сохранённых событий")
        return

    total_events = len(events_raw)

    # Пагинация событий
    page_key = "tree_events_page"
    if page_key not in st.session_state:
        st.session_state[page_key] = 0

    page = st.session_state[page_key]
    start = page * MAX_EVENTS_VISIBLE
    end = min(start + MAX_EVENTS_VISIBLE, total_events)

    if total_events > MAX_EVENTS_VISIBLE:
        col_info, col_prev, col_next = st.columns([3, 1, 1])
        with col_info:
            st.caption(f"Показано {start + 1}–{end} из {total_events} событий")
        with col_prev:
            if st.button("◀", key="tree_page_prev", disabled=(page == 0)):
                st.session_state[page_key] -= 1
                st.rerun()
        with col_next:
            max_page = (total_events - 1) // MAX_EVENTS_VISIBLE
            if st.button("▶", key="tree_page_next", disabled=(page >= max_page)):
                st.session_state[page_key] += 1
                st.rerun()

    for idx in range(start, end):
        event_dict = events_raw[idx]
        event_data = event_dict["PossibleNodeEventData"]
        event_id = event_data["EventID"]
        segments = event_data.get("Segments", {})
        n_segments = len(segments)

        with st.expander(f"📦 {event_id}  · {n_segments} сегм.", expanded=False):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(f"**{event_id}**")
            with col2:
                if st.button("✏️", key=f"tree_edit_event_{idx}"):
                    app_state.start_editing_event(idx)
                    st.rerun()
            with col3:
                if st.button("📋", key=f"tree_dup_event_{idx}", help="Дублировать событие"):
                    app_state.duplicate_event(idx)
                    st.rerun()
            with col4:
                if st.button("❌", key=f"tree_del_event_{idx}"):
                    app_state.delete_event(idx)
                    st.rerun()

            if st.button("📥 Пакетный импорт", key=f"tree_batch_import_{idx}", use_container_width=True):
                app_state.set_current_event_idx(idx)
                app_state.clear_editing()
                st.session_state["creating_event"] = False
                st.session_state["creating_segment"] = False
                st.session_state["creating_node"] = False
                st.session_state["batch_import_event_idx"] = idx
                st.rerun()

            if st.button("➕ Добавить сегмент", key=f"tree_add_seg_{idx}", use_container_width=True):
                app_state.set_current_event_idx(idx)
                app_state.clear_editing()
                st.session_state["creating_event"] = False
                st.session_state["creating_segment"] = True
                st.rerun()

            segments = event_data.get("Segments", {})
            if not segments:
                st.write("   📭 Нет сегментов")
                continue

            for seg_name, seg_data in segments.items():
                seg_info = seg_data.get("PossibleSegmentInfo", {})
                # Определяем тип и значение
                info_label = "N/A"
                if seg_info:
                    for key in ("VIPRange", "AverageWagerRange", "SpinpadRange", "LevelRange"):
                        if key in seg_info:
                            info_label = f"{key}: {seg_info[key]}"
                            break

                # Считаем ноды по всем стадиям
                n_nodes = sum(
                    len(stage.get("Nodes", []))
                    for stage in seg_data.get("Stages", [])
                )

                with st.expander(f"📁 {seg_name}  ({info_label})  · {n_nodes} нод", expanded=False):
                    cols = st.columns([3, 1, 1, 1])
                    with cols[0]:
                        st.write(f"**{seg_name}**")
                    with cols[1]:
                        if st.button("✏️", key=f"tree_edit_seg_{idx}_{seg_name}"):
                            app_state.start_editing_segment(idx, seg_name)
                            st.rerun()
                    with cols[2]:
                        if st.button("📋", key=f"tree_dup_seg_{idx}_{seg_name}", help="Дублировать сегмент"):
                            app_state.duplicate_segment(idx, seg_name)
                            st.rerun()
                    with cols[3]:
                        if st.button("❌", key=f"tree_del_seg_{idx}_{seg_name}"):
                            app_state.delete_segment(idx, seg_name)
                            st.rerun()

                    if st.button("➕ Добавить ноду", key=f"tree_add_node_{idx}_{seg_name}", use_container_width=True):
                        app_state.set_current_event_idx(idx)
                        app_state.set_current_segment_name(seg_name)
                        app_state.clear_editing()
                        st.session_state["creating_event"] = False
                        st.session_state["creating_segment"] = False
                        st.session_state["creating_node"] = True
                        st.rerun()

                    stages = seg_data.get("Stages", [])
                    if not stages:
                        st.write("      📭 Нет стадий")
                        continue

                    all_nodes = []
                    for stage_idx, stage in enumerate(stages):
                        nodes = stage.get("Nodes", [])
                        for node_idx, node_dict in enumerate(nodes):
                            all_nodes.append((stage_idx, node_idx, node_dict))

                    total_nodes = len(all_nodes)
                    if total_nodes == 0:
                        st.write("      📭 Нет узлов")
                        continue

                    # Ключ для хранения состояния (показать все / не все)
                    show_all_key = f"tree_show_all_{idx}_{seg_name}"
                    if show_all_key not in st.session_state:
                        st.session_state[show_all_key] = False

                    nodes_to_show = all_nodes if st.session_state[show_all_key] else all_nodes[:MAX_NODES_PER_SEGMENT]

                    for stage_idx, node_idx, node_dict in nodes_to_show:
                        node_type = list(node_dict.keys())[0]
                        node_info = node_dict[node_type]
                        node_id = node_info.get("NodeID", "?")
                        next_ids = node_info.get("NextNodeID", [])

                        n_cols = st.columns([3, 1, 1, 1])
                        with n_cols[0]:
                            st.write(f"         🔹 {node_type} (ID: {node_id}, Next: {next_ids})")
                        with n_cols[1]:
                            if st.button("✏️", key=f"tree_edit_node_{idx}_{seg_name}_{stage_idx}_{node_idx}"):
                                # Если уже редактируем ноду — сначала сбрасываем, потом открываем новую
                                if app_state.is_editing("node"):
                                    app_state.clear_editing()
                                    # Сохраняем координаты следующей ноды для открытия после rerun
                                    st.session_state["_pending_edit_node"] = (idx, seg_name, stage_idx, node_idx)
                                else:
                                    app_state.start_editing_node(idx, seg_name, stage_idx, node_idx)
                                st.rerun()
                        with n_cols[2]:
                            if st.button("📋", key=f"tree_dup_node_{idx}_{seg_name}_{stage_idx}_{node_idx}", help="Дублировать ноду"):
                                app_state.duplicate_node(idx, seg_name, stage_idx, node_idx)
                                st.rerun()
                        with n_cols[3]:
                            if st.button("❌", key=f"tree_del_node_{idx}_{seg_name}_{stage_idx}_{node_idx}"):
                                app_state.delete_node(idx, seg_name, stage_idx, node_idx)
                                st.rerun()

                    if total_nodes > MAX_NODES_PER_SEGMENT:
                        if st.session_state[show_all_key]:
                            hide_btn_key = f"btn_hide_nodes_{idx}_{seg_name}"
                            if st.button(f"⬆️ Скрыть узлы (показано {total_nodes})", key=hide_btn_key):
                                st.session_state[show_all_key] = False
                                st.rerun()
                        else:
                            show_btn_key = f"btn_show_nodes_{idx}_{seg_name}"
                            remaining = total_nodes - MAX_NODES_PER_SEGMENT
                            if st.button(f"⬇️ Показать ещё {remaining} узлов (всего {total_nodes})", key=show_btn_key):
                                st.session_state[show_all_key] = True
                                st.rerun()