import streamlit as st
from services.json_io import save_config_to_json
from services.state_manager import AppState

def render_export_tab():
    st.header("🌳 Структура и сохранение")

    with st.expander("📄 Полный JSON", expanded=False):
        st.json(AppState.get_cfg())

    st.download_button(
        label="📥 Скачать JSON файл",
        data=save_config_to_json(AppState.get_cfg()),
        file_name="LiveEventData.json",
        mime="application/json",
        use_container_width=True
    )