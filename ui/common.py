import streamlit as st

def confirm_button(label: str, key: str, message: str = "Вы уверены?") -> bool:
    """
    Кнопка с подтверждением через встроенный диалог.
    Возвращает True, если пользователь подтвердил действие.
    """
    if st.button(label, key=key):
        # Streamlit не имеет встроенного диалога подтверждения,
        # можно использовать session_state для имитации.
        st.session_state[f"confirm_{key}"] = True
        st.rerun()

    if st.session_state.get(f"confirm_{key}"):
        st.warning(message)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Да", key=f"{key}_yes"):
                del st.session_state[f"confirm_{key}"]
                return True
        with col2:
            if st.button("❌ Нет", key=f"{key}_no"):
                del st.session_state[f"confirm_{key}"]
                return False
    return False

def styled_info(text: str):
    """Информационное сообщение с кастомным стилем."""
    st.markdown(f"<div style='background-color:#e6f3ff;padding:8px;border-radius:5px;'>{text}</div>", unsafe_allow_html=True)

def styled_error(text: str):
    """Сообщение об ошибке с кастомным стилем."""
    st.markdown(f"<div style='background-color:#ffe6e6;padding:8px;border-radius:5px;color:#cc0000;'>{text}</div>", unsafe_allow_html=True)

def format_key(prefix: str, index: int) -> str:
    """Генерирует уникальный ключ для виджета."""
    return f"{prefix}_{index}"