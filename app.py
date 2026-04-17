import streamlit as st
from services.state_manager import AppState
from ui.tabs.validation_tab import render_validation_tab
from ui.tabs.editor_tab import render_editor_tab
from ui.tabs.export_tab import render_export_tab

st.set_page_config(page_title="LiveEvent JSON Builder", layout="wide")
st.title("🎮 LiveEvent JSON Builder")

# Инициализация состояния
AppState.init()

tab1, tab2, tab3 = st.tabs(["📁 Загрузка и валидация", "⚙️ Настройка события", "🌳 Структура и сохранение"])

with tab1:
    render_validation_tab()

with tab2:
    render_editor_tab()

with tab3:
    render_export_tab()