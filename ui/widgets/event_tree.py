import streamlit as st
from services.state_manager import AppState
from models.nodes import ProgressNode, EntriesNode, DummyNode

def render_event_tree():
    """Отображает все события в виде дерева с возможностью выбора и редактирования."""
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
            else:
                for seg_name, seg_data in segments.items():
                    seg_key = f"{event_id}_{seg_name}"
                    cols = st.columns([3, 1, 1])
                    with cols[0]:
                        vip = seg_data.get("PossibleSegmentInfo", {}).get("VIPRange", "N/A")
                        st.write(f"   📁 **{seg_name}** (VIP: {vip})")
                    with cols[1]:
                        if st.button("✏️", key=f"tree_edit_seg_{idx}_{seg_name}"):
                            AppState.start_editing_segment(idx, seg_name)
                            st.rerun()
                    with cols[2]:
                        if st.button("❌", key=f"tree_del_seg_{idx}_{seg_name}"):
                            AppState.delete_segment(idx, seg_name)
                            st.rerun()

                    stages = seg_data.get("Stages", [])
                    for stage_idx, stage in enumerate(stages):
                        nodes = stage.get("Nodes", [])
                        for node_idx, node_dict in enumerate(nodes):
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
                                    AppState.delete_node_from_current_segment(stage_idx, node_idx)
                                    st.rerun()