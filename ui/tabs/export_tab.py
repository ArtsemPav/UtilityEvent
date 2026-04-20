import streamlit as st
from services.json_io import save_config_to_json
from services.state_manager import AppState

def render_export_tab():
    app_state = AppState.get_instance()
    st.header("🌳 Структура и сохранение")

    with st.expander("📄 Полный JSON", expanded=False):
        st.json(app_state.get_cfg())

    st.download_button(
        label="📥 Скачать JSON файл",
        data=save_config_to_json(app_state.get_cfg()),
        file_name="LiveEventData.json",
        mime="application/json",
        use_container_width=True
    )