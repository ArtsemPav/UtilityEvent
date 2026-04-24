import json
import streamlit as st
import streamlit.components.v1 as components
from services.json_io import save_config_to_json
from services.state_manager import AppState
from utils.validators import validate_event_id


def _copy_button(text: str) -> None:
    """Рендерит кнопку 'Копировать в буфер' через JS."""
    import hashlib
    import base64
    btn_id = "cpbtn_" + hashlib.md5(text[:64].encode()).hexdigest()[:8]
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


def _validate_liveevent(cfg: dict) -> list[str]:
    """Базовая валидация конфига LiveEvent. Возвращает список ошибок."""
    errors = []
    events_raw = cfg.get("Events", [])
    seen_ids = []
    for i, event in enumerate(events_raw):
        event_id = event.get("PossibleNodeEventData", {}).get("EventID", "")
        errs = validate_event_id(event_id)
        for e in errs:
            errors.append(f"Событие #{i+1}: {e}")
        if event_id and event_id in seen_ids:
            errors.append(f"Событие #{i+1}: дублирующийся EventID «{event_id}»")
        if event_id:
            seen_ids.append(event_id)
    return errors


def render_export_tab():
    app_state = AppState.get_instance()
    st.header("💾 Экспорт LiveEvent")

    cfg = app_state.get_cfg()
    events_raw = cfg.get("Events", [])
    n_events = len(events_raw)
    is_empty = n_events == 0

    st.caption(f"Событий в конфиге: {n_events}")

    if is_empty:
        st.info("Нет событий для экспорта. Перейдите на вкладку ✏️Редактор LiveEvent и создайте конфиг.")
        st.download_button(
            "📥 Скачать LiveEventData.json",
            data=b"",
            file_name="LiveEventData.json",
            mime="application/json",
            disabled=True,
            use_container_width=True,
            key="liveevent_export_download_empty",
        )
        return

    # Валидация
    errors = _validate_liveevent(cfg)
    has_errors = len(errors) > 0

    if errors:
        st.error(f"Найдено ошибок: {len(errors)}. Исправьте их перед экспортом.")
        for e in errors:
            st.warning(e)

    full_json_str = save_config_to_json(cfg).decode("utf-8")

    # Кнопки скачивания и копирования
    col_dl, col_cp = st.columns(2)
    with col_dl:
        st.download_button(
            label="📥 Скачать LiveEventData.json",
            data=full_json_str.encode("utf-8"),
            file_name="LiveEventData.json",
            mime="application/json",
            disabled=has_errors,
            use_container_width=True,
            key="liveevent_export_download",
        )
    with col_cp:
        if not has_errors:
            _copy_button(full_json_str)
        else:
            st.button("📋 Копировать в буфер", disabled=True, use_container_width=True)

    st.divider()

    # Предпросмотр с фильтром по событию
    st.subheader("🔍 Предпросмотр JSON")

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
        show = st.button("👁️ Показать JSON", use_container_width=True, key="liveevent_export_show")

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
            _copy_button(preview_str)
