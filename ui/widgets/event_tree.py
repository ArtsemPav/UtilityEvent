# ui/widgets/event_tree.py
import streamlit as st
from services.state_manager import AppState

# Максимальное количество узлов для отображения в одном сегменте
MAX_NODES_PER_SEGMENT = 10


def render_event_tree():
    """Отображает все события в виде дерева с ленивой загрузкой узлов."""
    events_raw = AppState.get_events_raw()
    if not events_raw:
        st.info("📭 Нет сохранённых событий")
        return

    for idx, event_dict in enumerate(events_raw):
        event_data = event_dict["PossibleNodeEventData"]
        event_id = event_data["EventID"]

        with st.expander(f"📦 Событие: {event_id}", expanded=False):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{event_id}**")
            with col2:
                if st.button("✏️", key=f"tree_edit_event_{idx}"):
                    AppState.start_editing_event(idx)
                    st.rerun()
            with col3:
                if st.button("❌", key=f"tree_del_event_{idx}"):
                    AppState.delete_event(idx)
                    st.rerun()

            segments = event_data.get("Segments", {})
            if not segments:
                st.write("   📭 Нет сегментов")
                continue

            # Показываем сегменты (каждый в своём expander'е)
            for seg_name, seg_data in segments.items():
                seg_key = f"{event_id}_{seg_name}"
                vip_info = seg_data.get("PossibleSegmentInfo", {})
                vip_range = vip_info.get("VIPRange", "N/A") if vip_info else "N/A"

                with st.expander(f"📁 Сегмент: {seg_name} (VIP: {vip_range})", expanded=False):
                    cols = st.columns([3, 1, 1])
                    with cols[0]:
                        st.write(f"**{seg_name}**")
                    with cols[1]:
                        if st.button("✏️", key=f"tree_edit_seg_{idx}_{seg_name}"):
                            AppState.start_editing_segment(idx, seg_name)
                            st.rerun()
                    with cols[2]:
                        if st.button("❌", key=f"tree_del_seg_{idx}_{seg_name}"):
                            AppState.delete_segment(idx, seg_name)
                            st.rerun()

                    stages = seg_data.get("Stages", [])
                    if not stages:
                        st.write("      📭 Нет стадий")
                        continue

                    # Собираем все узлы из всех стадий
                    all_nodes = []
                    for stage_idx, stage in enumerate(stages):
                        nodes = stage.get("Nodes", [])
                        for node_idx, node_dict in enumerate(nodes):
                            all_nodes.append((stage_idx, node_idx, node_dict))

                    total_nodes = len(all_nodes)
                    if total_nodes == 0:
                        st.write("      📭 Нет узлов")
                        continue

                    # Определяем, сколько узлов показывать
                    show_all_key = f"tree_show_all_{idx}_{seg_name}"
                    if show_all_key not in st.session_state:
                        st.session_state[show_all_key] = False

                    nodes_to_show = all_nodes if st.session_state[show_all_key] else all_nodes[:MAX_NODES_PER_SEGMENT]

                    # Отображаем узлы
                    for stage_idx, node_idx, node_dict in nodes_to_show:
                        node_type = list(node_dict.keys())[0]
                        node_info = node_dict[node_type]
                        node_id = node_info.get("NodeID", "?")
                        next_ids = node_info.get("NextNodeID", [])

                        n_cols = st.columns([3, 1, 1])
                        with n_cols[0]:
                            st.write(f"         🔹 {node_type} (ID: {node_id}, Next: {next_ids})")
                        with n_cols[1]:
                            if st.button("✏️", key=f"tree_edit_node_{idx}_{seg_name}_{stage_idx}_{node_idx}"):
                                AppState.start_editing_node(idx, seg_name, stage_idx, node_idx)
                                st.rerun()
                        with n_cols[2]:
                            if st.button("❌", key=f"tree_del_node_{idx}_{seg_name}_{stage_idx}_{node_idx}"):
                                # Удаление узла
                                event = AppState.get_event_by_index(idx)
                                if event and seg_name in event.segments:
                                    segment = event.segments[seg_name]
                                    if stage_idx < len(segment.stages) and node_idx < len(segment.stages[stage_idx].nodes):
                                        del segment.stages[stage_idx].nodes[node_idx]
                                        AppState.update_event(idx, event)
                                        st.rerun()

                    # Кнопка "Показать ещё" / "Скрыть"
                    if total_nodes > MAX_NODES_PER_SEGMENT:
                        if st.session_state[show_all_key]:
                            if st.button(f"⬆️ Скрыть узлы (показано {total_nodes})", key=f"tree_hide_nodes_{idx}_{seg_name}"):
                                st.session_state[show_all_key] = False
                                st.rerun()
                        else:
                            remaining = total_nodes - MAX_NODES_PER_SEGMENT
                            if st.button(f"⬇️ Показать ещё {remaining} узлов (всего {total_nodes})", key=f"tree_show_all_{idx}_{seg_name}"):
                                st.session_state[show_all_key] = True
                                st.rerun()