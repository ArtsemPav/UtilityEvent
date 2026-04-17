import streamlit as st
from typing import Optional, Union
from models.minbet import FixedMinBet, VariableMinBet

def render_minbet_widget(
    prefix: str,
    existing: Optional[Union[FixedMinBet, VariableMinBet]] = None
) -> Union[FixedMinBet, VariableMinBet]:
    """Возвращает объект FixedMinBet или VariableMinBet."""
    current_type = "Fixed"
    if existing is not None:
        current_type = "Fixed" if isinstance(existing, FixedMinBet) else "Variable"

    st.write("**Тип MinBet:**")
    minbet_type = st.radio(
        "Выберите тип",
        options=["Fixed", "Variable"],
        index=0 if current_type == "Fixed" else 1,
        key=f"{prefix}_minbet_type",
        horizontal=True,
        label_visibility="collapsed"
    )

    if minbet_type == "Fixed":
        default_val = existing.amount if isinstance(existing, FixedMinBet) else 250000.0
        fixed_val = st.number_input(
            "Fixed MinBet",
            value=float(default_val),
            min_value=0.0,
            step=10000.0,
            format="%.2f",
            key=f"{prefix}_fixed"
        )
        return FixedMinBet(amount=float(fixed_val))
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            default_var = existing.variable if isinstance(existing, VariableMinBet) else 0.8
            var = st.number_input(
                "Variable",
                value=float(default_var),
                min_value=0.0,
                max_value=10.0,
                step=0.1,
                format="%.2f",
                key=f"{prefix}_var"
            )
        with col2:
            default_min = existing.min if isinstance(existing, VariableMinBet) else 25000.0
            min_v = st.number_input(
                "Min",
                value=float(default_min),
                min_value=0.0,
                step=1000.0,
                format="%.2f",
                key=f"{prefix}_min"
            )
        with col3:
            default_max = existing.max if isinstance(existing, VariableMinBet) else 5000000.0
            max_v = st.number_input(
                "Max",
                value=float(default_max),
                min_value=0.0,
                step=10000.0,
                format="%.2f",
                key=f"{prefix}_max"
            )
        return VariableMinBet(variable=float(var), min=float(min_v), max=float(max_v))