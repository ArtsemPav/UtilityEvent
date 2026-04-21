# ui/widgets/goal_widget.py
import streamlit as st
from typing import Optional
from models.goals import (
    Goal,
    FixedGoal,
    SpinpadGoal,
    ConsecutiveWinsGoal,
    TotalCoinsPerDayGoal,
    TotalCoinsPerDayWithSpinLimiterGoal,
    FixedGoalWithSpinLimiterGoal,
)

def render_goal_widget(prefix: str, existing: Optional[Goal] = None) -> Goal:
    """
    Возвращает объект Goal. Изменения применяются сразу (без отдельной кнопки).
    """
    # Определяем текущие значения из existing
    if existing is not None:
        current_goal_type = existing.type[0] if existing.type else "Spins"
        params_obj = existing.params
    else:
        current_goal_type = "Spins"
        params_obj = FixedGoal(target=20)

    # Определяем текущий тип параметров
    if isinstance(params_obj, FixedGoal):
        current_params_type = "FixedGoal"
    elif isinstance(params_obj, SpinpadGoal):
        current_params_type = "SpinpadGoal"
    elif isinstance(params_obj, ConsecutiveWinsGoal):
        current_params_type = "ConsecutiveWinsGoal"
    elif isinstance(params_obj, TotalCoinsPerDayGoal):
        current_params_type = "TotalCoinsPerDay"
    elif isinstance(params_obj, TotalCoinsPerDayWithSpinLimiterGoal):
        current_params_type = "TotalCoinsPerDayWithSpinLimiter"
    elif isinstance(params_obj, FixedGoalWithSpinLimiterGoal):
        current_params_type = "FixedGoalWithSpinLimiter"
    else:
        current_params_type = "FixedGoal"

    # Поля ввода (без ручного управления session_state)
    col1, col2 = st.columns([1, 3])
    with col1:
        goal_type = st.text_input(
            "Тип цели (Type)",
            value=current_goal_type,
            key=f"{prefix}_goal_type"
        )
    with col2:
        params_options = [
            "SpinpadGoal",
            "FixedGoal",
            "ConsecutiveWinsGoal",
            "TotalCoinsPerDay",
            "TotalCoinsPerDayWithSpinLimiter",
            "FixedGoalWithSpinLimiter"
        ]
        selected_params = st.selectbox(
            "Параметры цели",
            options=params_options,
            index=params_options.index(current_params_type) if current_params_type in params_options else 1,
            key=f"{prefix}_goal_params"
        )

    # Рендерим поля для выбранного типа параметров
    params = None
    if selected_params == "SpinpadGoal":
        c1, c2, c3 = st.columns(3)
        with c1:
            mult = st.number_input(
                "Multiplier",
                value=params_obj.multiplier if isinstance(params_obj, SpinpadGoal) else 0.5,
                min_value=0.0, max_value=10.0, step=0.1, format="%.3f",
                key=f"{prefix}_spin_mult"
            )
        with c2:
            min_v = st.number_input(
                "Min",
                value=params_obj.min if isinstance(params_obj, SpinpadGoal) else 10,
                min_value=1, step=1,
                key=f"{prefix}_spin_min"
            )
        with c3:
            max_v = st.number_input(
                "Max",
                value=params_obj.max if isinstance(params_obj, SpinpadGoal) else 150,
                min_value=1, step=1,
                key=f"{prefix}_spin_max"
            )
        params = SpinpadGoal(multiplier=float(mult), min=int(min_v), max=int(max_v))

    elif selected_params == "FixedGoal":
        target = st.number_input(
            "Target",
            value=params_obj.target if isinstance(params_obj, FixedGoal) else 20,
            min_value=1, step=1,
            key=f"{prefix}_fixed_target"
        )
        params = FixedGoal(target=int(target))

    elif selected_params == "ConsecutiveWinsGoal":
        c1, c2 = st.columns(2)
        with c1:
            streaks = st.number_input(
                "Number of Streaks",
                value=params_obj.number_of_streaks_target if isinstance(params_obj, ConsecutiveWinsGoal) else 3,
                min_value=1, step=1,
                key=f"{prefix}_cw_streaks"
            )
        with c2:
            mult = st.number_input(
                "Multiplier",
                value=params_obj.multiplier if isinstance(params_obj, ConsecutiveWinsGoal) else 0.01,
                min_value=0.0, max_value=1.0, step=0.01, format="%.3f",
                key=f"{prefix}_cw_mult"
            )
        c3, c4 = st.columns(2)
        with c3:
            min_v = st.number_input(
                "Min",
                value=params_obj.min if isinstance(params_obj, ConsecutiveWinsGoal) else 2,
                min_value=1, step=1,
                key=f"{prefix}_cw_min"
            )
        with c4:
            max_v = st.number_input(
                "Max",
                value=params_obj.max if isinstance(params_obj, ConsecutiveWinsGoal) else 5,
                min_value=1, step=1,
                key=f"{prefix}_cw_max"
            )
        params = ConsecutiveWinsGoal(
            number_of_streaks_target=int(streaks),
            multiplier=float(mult),
            min=int(min_v),
            max=int(max_v)
        )

    elif selected_params == "TotalCoinsPerDay":
        c1, c2, c3 = st.columns(3)
        with c1:
            mult = st.number_input(
                "Multiplier",
                value=params_obj.multiplier if isinstance(params_obj, TotalCoinsPerDayGoal) else 0.5,
                min_value=0.0, max_value=10.0, step=0.1, format="%.3f",
                key=f"{prefix}_tcpd_mult"
            )
        with c2:
            min_v = st.number_input(
                "Min",
                value=params_obj.min if isinstance(params_obj, TotalCoinsPerDayGoal) else 10,
                min_value=1, step=1,
                key=f"{prefix}_tcpd_min"
            )
        with c3:
            max_v = st.number_input(
                "Max",
                value=params_obj.max if isinstance(params_obj, TotalCoinsPerDayGoal) else 150,
                min_value=1, step=1,
                key=f"{prefix}_tcpd_max"
            )
        params = TotalCoinsPerDayGoal(multiplier=float(mult), min=int(min_v), max=int(max_v))

    elif selected_params == "TotalCoinsPerDayWithSpinLimiter":
        c1, c2 = st.columns(2)
        with c1:
            spin_lim = st.number_input(
                "Spin Limiter",
                value=params_obj.spin_limiter if isinstance(params_obj, TotalCoinsPerDayWithSpinLimiterGoal) else 3,
                min_value=1, step=1,
                key=f"{prefix}_tcpdsl_sl"
            )
            mult = st.number_input(
                "Multiplier",
                value=params_obj.multiplier if isinstance(params_obj, TotalCoinsPerDayWithSpinLimiterGoal) else 0.097,
                min_value=0.0, max_value=1.0, step=0.001, format="%.3f",
                key=f"{prefix}_tcpdsl_mult"
            )
        with c2:
            min_v = st.number_input(
                "Min",
                value=params_obj.min if isinstance(params_obj, TotalCoinsPerDayWithSpinLimiterGoal) else 3500000,
                min_value=1, step=1000,
                key=f"{prefix}_tcpdsl_min"
            )
            max_v = st.number_input(
                "Max",
                value=params_obj.max if isinstance(params_obj, TotalCoinsPerDayWithSpinLimiterGoal) else 50000000,
                min_value=1, step=1000,
                key=f"{prefix}_tcpdsl_max"
            )
        params = TotalCoinsPerDayWithSpinLimiterGoal(
            spin_limiter=int(spin_lim),
            multiplier=float(mult),
            min=int(min_v),
            max=int(max_v)
        )

    elif selected_params == "FixedGoalWithSpinLimiter":
        c1, c2 = st.columns(2)
        with c1:
            target = st.number_input(
                "Target",
                value=params_obj.target if isinstance(params_obj, FixedGoalWithSpinLimiterGoal) else 10,
                min_value=1, step=1,
                key=f"{prefix}_fgwsl_target"
            )
        with c2:
            spin_lim = st.number_input(
                "Spin Limiter",
                value=params_obj.spin_limiter if isinstance(params_obj, FixedGoalWithSpinLimiterGoal) else 3,
                min_value=1, step=1,
                key=f"{prefix}_fgwsl_sl"
            )
        params = FixedGoalWithSpinLimiterGoal(target=int(target), spin_limiter=int(spin_lim))

    # Возвращаем сформированную цель
    return Goal(type=[goal_type], params=params)