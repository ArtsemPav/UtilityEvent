import json
import streamlit as st
import streamlit.components.v1 as components

from services.singlepick_validator import validate_singlepick
from ui.tabs.singlepick_tab import get_singlepick_state


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


def render_singlepick_export_tab() -> None:
    state = get_singlepick_state()

    st.header("📤 Экспорт SinglePick")

    errors = validate_singlepick(state.config)
    is_empty = len(state.config.config_sets) == 0
    has_errors = len(errors) > 0

    # Счётчик
    st.caption(f"ConfigSet-ов в конфиге: {len(state.config.config_sets)}")

    if is_empty:
        st.info("Нет конфигов для экспорта. Перейдите на вкладку 🎰Редактор SinglePick и создайте конфиг.")
        st.download_button(
            "📥 Скачать SinglePickConfig.json",
            data=b"",
            file_name="SinglePickConfig.json",
            mime="application/json",
            disabled=True,
            use_container_width=True,
            key="singlepick_export_download_empty",
        )
        return

    # Ошибки валидации
    if errors:
        st.error(f"Найдено ошибок: {len(errors)}. Исправьте их перед экспортом.")
        for e in errors:
            st.warning(f"**[{e.configset_name}]** `{e.field}`: {e.message}")

    json_str = json.dumps(state.config.to_dict(), ensure_ascii=False, indent=4)

    # Кнопки скачивания и копирования
    col_dl, col_cp = st.columns(2)
    with col_dl:
        st.download_button(
            "📥 Скачать SinglePickConfig.json",
            data=json_str.encode("utf-8"),
            file_name="SinglePickConfig.json",
            mime="application/json",
            disabled=has_errors,
            use_container_width=True,
            key="singlepick_export_download",
        )
    with col_cp:
        if not has_errors:
            _copy_button(json_str)
        else:
            st.button("📋 Копировать в буфер", disabled=True, use_container_width=True)

    st.divider()

    # Предпросмотр с фильтром по ConfigSet
    st.subheader("🔍 Предпросмотр JSON")

    config_set_names = list(state.config.config_sets.keys())
    col_filter, col_btn = st.columns([3, 1])
    with col_filter:
        selected = st.selectbox(
            "Выберите ConfigSet",
            options=["— Весь конфиг —"] + config_set_names,
            key="singlepick_export_filter",
        )
    with col_btn:
        st.write("")  # выравнивание
        show = st.button("👁️ Показать JSON", use_container_width=True, key="singlepick_export_show")

    if show:
        if selected == "— Весь конфиг —":
            preview_data = state.config.to_dict()
            filename_hint = "SinglePickConfig.json"
        else:
            cs = state.config.config_sets.get(selected)
            preview_data = {"ConfigSets": {selected: cs.to_dict()}} if cs else {}
            filename_hint = f"{selected}.json"

        st.session_state["singlepick_export_preview_json"] = json.dumps(
            preview_data, ensure_ascii=False, indent=4
        )
        st.session_state["singlepick_export_preview_filename"] = filename_hint

    if "singlepick_export_preview_json" in st.session_state:
        preview_str = st.session_state["singlepick_export_preview_json"]
        filename_hint = st.session_state.get("singlepick_export_preview_filename", "fragment.json")

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
                key="singlepick_export_download_fragment",
            )
        with col_cp2:
            _copy_button(preview_str)
