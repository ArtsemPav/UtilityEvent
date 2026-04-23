import streamlit as st
from services.state_manager import AppState
from ui.tabs.validation_tab import render_validation_tab
from ui.tabs.editor_tab import render_editor_tab
from ui.tabs.export_tab import render_export_tab
from ui.tabs.singlepick_tab import render_singlepick_tab
from ui.tabs.singlepick_export_tab import render_singlepick_export_tab
from ui.import_tab import render_import_tab

st.set_page_config(page_title="LiveEvent JSON Builder", layout="wide")
st.title("🎮 LiveEvent JSON Builder")

app_state = AppState.get_instance()

if app_state.get_current_event_idx() == -1 and len(app_state.get_events_raw()) > 0:
    app_state.set_current_event_idx(0)

tab_editor, tab_export, tab_singlepick, tab_singlepick_export = st.tabs([
    "✏️ Редактор LiveEvent ",
    "💾 Экспорт LiveEvent",
    "🎰 Редактор SinglePick",
    "📤 Экспорт SinglePick",
])

with tab_editor:
    render_editor_tab()

with tab_export:
    render_export_tab()

with tab_singlepick:
    render_singlepick_tab()

with tab_singlepick_export:
    render_singlepick_export_tab()
