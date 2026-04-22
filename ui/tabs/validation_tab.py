import streamlit as st
import json
from services.json_io import load_config_from_json, validate_config
from services.state_manager import AppState

def render_validation_tab():
    app_state = AppState.get_instance()
    st.header("Загрузка и валидация JSON")
    col1, col2 = st.columns(2)
    with col1:
        uploaded = st.file_uploader("Загрузить JSON", type=["json"])
        if uploaded:
            try:
                with st.spinner("Загрузка JSON..."):
                    cfg = load_config_from_json(uploaded.read())
                    app_state.set_cfg(cfg)
                n_events = len(cfg.get("Events", []))
                st.success(f"JSON загружен ({n_events} событий)")
            except Exception as e:
                st.error(f"Ошибка: {e}")

        schema_file = st.file_uploader("Загрузить схему", type=["json"])
        schema = None
        if schema_file:
            schema = json.load(schema_file)
        if st.button("Проверить валидацию"):
            valid, msg = validate_config(app_state.get_cfg(), schema)
            if valid:
                st.success("Валиден")
            else:
                st.error(f"Не валиден: {msg}")

    with col2:
        if st.button("Создать новый конфиг"):
            app_state.set_cfg({"Events": [], "IsFallbackConfig": False})
            st.success("Создан")