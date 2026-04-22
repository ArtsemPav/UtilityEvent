import json
import streamlit as st
from services.json_io import save_config_to_json
from services.state_manager import AppState


def render_export_tab():
    app_state = AppState.get_instance()
    st.header("🌳 Структура и сохранение")

    cfg = app_state.get_cfg()
    events_raw = cfg.get("Events", [])
    n_events = len(events_raw)
    st.caption(f"Событий в конфиге: {n_events}")

    # ── Скачивание ──────────────────────────────────────────────────────────
    st.download_button(
        label="� Скачать JSON файл",
        data=save_config_to_json(cfg),
        file_name="LiveEventData.json",
        mime="application/json",
        use_container_width=True,
    )

    st.divider()

    # ── Просмотр JSON с фильтрацией ─────────────────────────────────────────
    st.subheader("🔍 Просмотр JSON")

    if n_events == 0:
        st.info("Нет событий для отображения.")
        return

    # Собираем список EventID для selectbox
    event_ids = [
        e.get("PossibleNodeEventData", {}).get("EventID", f"[{i}]")
        for i, e in enumerate(events_raw)
    ]

    col_filter, col_btn = st.columns([3, 1])
    with col_filter:
        selected_id = st.selectbox(
            "Выберите событие",
            options=["— Весь конфиг —"] + event_ids,
            key="export_filter_event_id",
        )
    with col_btn:
        st.write("")  # выравнивание по высоте
        show = st.button("👁️ Показать JSON", use_container_width=True)

    if show:
        if selected_id == "— Весь конфиг —":
            preview_data = cfg
            filename_hint = "LiveEventData.json"
        else:
            # Находим нужное событие по EventID
            matched = next(
                (e for e in events_raw
                 if e.get("PossibleNodeEventData", {}).get("EventID") == selected_id),
                None,
            )
            preview_data = {"Events": [matched], "IsFallbackConfig": cfg.get("IsFallbackConfig", False)} \
                if matched else {}
            filename_hint = f"{selected_id}.json"

        st.session_state["export_preview_json"] = json.dumps(
            preview_data, ensure_ascii=False, indent=4
        )
        st.session_state["export_preview_filename"] = filename_hint

    # Отображаем сохранённый предпросмотр
    if "export_preview_json" in st.session_state:
        preview_str = st.session_state["export_preview_json"]
        filename_hint = st.session_state.get("export_preview_filename", "fragment.json")

        with st.expander("📄 JSON", expanded=True):
            st.code(preview_str, language="json")

        # Скачать именно этот фрагмент
        st.download_button(
            label=f"📥 Скачать {filename_hint}",
            data=preview_str.encode("utf-8"),
            file_name=filename_hint,
            mime="application/json",
            use_container_width=True,
            key="export_download_fragment",
        )
