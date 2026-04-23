import json
import streamlit as st
import streamlit.components.v1 as components
from services.json_io import save_config_to_json
from services.state_manager import AppState


def _copy_button(text: str, key: str) -> None:
    """Рендерит кнопку 'Копировать в буфер' через JS."""
    import hashlib
    btn_id = "cpbtn_" + hashlib.md5(key.encode()).hexdigest()[:8]
    # Кодируем текст в base64 чтобы избежать любых проблем с экранированием
    import base64
    b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
    components.html(
        f"""
        <button id="{btn_id}" style="
            width:100%; padding:8px 16px; font-size:14px; cursor:pointer;
            background:#262730; color:#fafafa; border:1px solid #555; border-radius:6px;
        ">Copy to clipboard</button>
        <script>
        (function() {{
            var btn = document.getElementById("{btn_id}");
            var b64 = "{b64}";
            var text = decodeURIComponent(escape(atob(b64)));
            btn.addEventListener("click", function() {{
                navigator.clipboard.writeText(text).then(function() {{
                    btn.textContent = "Copied!";
                    setTimeout(function() {{ btn.textContent = "Copy to clipboard"; }}, 2000);
                }}).catch(function() {{
                    btn.textContent = "Error";
                    setTimeout(function() {{ btn.textContent = "Copy to clipboard"; }}, 2000);
                }});
            }});
        }})();
        </script>
        """,
        height=44,
    )


def render_export_tab():
    app_state = AppState.get_instance()
    st.header("🌳 Структура и сохранение")

    cfg = app_state.get_cfg()
    events_raw = cfg.get("Events", [])
    n_events = len(events_raw)
    st.caption(f"Событий в конфиге: {n_events}")

    # ── Скачивание ──────────────────────────────────────────────────────────
    full_json_str = save_config_to_json(cfg).decode("utf-8")

    col_dl, col_cp = st.columns(2)
    with col_dl:
        st.download_button(
            label="📥 Скачать JSON файл",
            data=full_json_str.encode("utf-8"),
            file_name="LiveEventData.json",
            mime="application/json",
            use_container_width=True,
        )
    with col_cp:
        _copy_button(full_json_str, key="copy_full")

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

        col_dl2, col_cp2 = st.columns(2)
        with col_dl2:
            st.download_button(
                label=f"📥 Скачать {filename_hint}",
                data=preview_str.encode("utf-8"),
                file_name=filename_hint,
                mime="application/json",
                use_container_width=True,
                key="export_download_fragment",
            )
        with col_cp2:
            _copy_button(preview_str, key="copy_fragment")
