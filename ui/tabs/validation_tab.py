import streamlit as st
from services.json_io import load_config_from_json, validate_config
from services.state_manager import AppState

def render_validation_tab():
    st.header("Загрузка и валидация JSON")
    col1, col2 = st.columns(2)
    with col1:
        uploaded = st.file_uploader("Загрузить JSON", type=["json"])
        if uploaded:
            try:
                cfg = load_config_from_json(uploaded.read())
                AppState.set_cfg(cfg)
                st.success("JSON загружен")
            except Exception as e:
                st.error(f"Ошибка: {e}")

        schema_file = st.file_uploader("Загрузить схему", type=["json"])
        schema = None
        if schema_file:
            schema = json.load(schema_file)
        if st.button("Проверить валидацию"):
            if validate_config(AppState.get_cfg(), schema):
                st.success("Валиден")
            else:
                st.error("Не валиден")

    with col2:
        if st.button("Создать новый конфиг"):
            AppState.set_cfg({"Events": [], "IsFallbackConfig": False})
            st.success("Создан")