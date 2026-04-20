import streamlit as st
from typing import List
from models.rewards import Reward, FixedReward
from .reward_widget import render_reward_widget

def get_default_reward() -> Reward:
    """Возвращает стандартную награду (2500000 чипов)."""
    return Reward(data=FixedReward(currency="Chips", amount=2500000.0))

def render_rewards_editor(prefix: str, existing_rewards: List[Reward]) -> List[Reward]:
    """
    Полноценный редактор наград с возможностью добавления, удаления и редактирования.
    Состояние хранится в session_state по ключу f"{prefix}_rewards".
    """
    rewards_key = f"{prefix}_rewards"
    editing_key = f"{prefix}_editing_idx"
    show_add_key = f"{prefix}_show_add"

    # Инициализация состояния
    if rewards_key not in st.session_state:
        st.session_state[rewards_key] = list(existing_rewards) if existing_rewards else [get_default_reward()]
    if editing_key not in st.session_state:
        st.session_state[editing_key] = -1
    if show_add_key not in st.session_state:
        st.session_state[show_add_key] = False

    rewards = st.session_state[rewards_key]

    st.write("**Награды:**")

    # Отображение существующих наград
    delete_indices = []
    for i, reward in enumerate(rewards):
        cols = st.columns([4, 1, 1])
        with cols[0]:
            data = reward.data
            if isinstance(data, FixedReward):
                desc = f"💰 {data.amount:,.0f} {data.currency}"
            elif hasattr(data, 'percentage'):
                desc = f"📊 RTP {data.percentage*100:.1f}% Chips"
            elif hasattr(data, 'spins'):
                desc = f"🎰 {data.spins} Free Spins on {data.game_name}"
            elif hasattr(data, 'num_packs'):
                desc = f"📦 {data.num_packs}x Pack {data.pack_id}"
            else:
                desc = f"🎁 {type(data).__name__}"
            st.write(f"{i+1}. {desc}")

        with cols[1]:
            if st.button("✏️", key=f"{prefix}_edit_reward_{i}"):
                st.session_state[editing_key] = i
                st.session_state[show_add_key] = False
                st.rerun()
        with cols[2]:
            if st.button("❌", key=f"{prefix}_del_reward_{i}"):
                delete_indices.append(i)

    # Обработка удаления
    if delete_indices:
        for idx in sorted(delete_indices, reverse=True):
            del st.session_state[rewards_key][idx]
        st.rerun()

    # Кнопка добавления новой награды
    if st.button("➕ Добавить награду", key=f"{prefix}_add_reward_btn"):
        st.session_state[show_add_key] = True
        st.session_state[editing_key] = -1
        st.rerun()

    # Редактирование существующей награды
    editing_idx = st.session_state[editing_key]
    if editing_idx >= 0 and editing_idx < len(rewards):
        with st.expander(f"✏️ Редактирование награды #{editing_idx+1}", expanded=True):
            new_reward = render_reward_widget(f"{prefix}_edit", editing_idx, rewards[editing_idx])
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button("💾 Сохранить", key=f"{prefix}_save_edit_{editing_idx}"):
                    st.session_state[rewards_key][editing_idx] = new_reward
                    st.session_state[editing_key] = -1
                    st.rerun()
            with col_cancel:
                if st.button("❌ Отмена", key=f"{prefix}_cancel_edit_{editing_idx}"):
                    st.session_state[editing_key] = -1
                    st.rerun()

    # Добавление новой награды
    if st.session_state[show_add_key]:
        with st.expander("➕ Новая награда", expanded=True):
            new_reward = render_reward_widget(f"{prefix}_new", len(rewards))
            col_add, col_cancel_add = st.columns(2)
            with col_add:
                if st.button("✅ Добавить", key=f"{prefix}_confirm_add"):
                    st.session_state[rewards_key].append(new_reward)
                    st.session_state[show_add_key] = False
                    st.rerun()
            with col_cancel_add:
                if st.button("❌ Отмена", key=f"{prefix}_cancel_add"):
                    st.session_state[show_add_key] = False
                    st.rerun()

    return rewards