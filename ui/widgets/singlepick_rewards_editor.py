import streamlit as st
from typing import List
from models.singlepick import (
    SPReward,
    FixedSPReward,
    RtpSPReward,
    PurchaseSPReward,
    FreeplaySPReward,
    PacksSPReward,
)
from .singlepick_reward_widget import render_sp_reward_widget


def _reward_desc(reward: SPReward) -> str:
    """Краткое описание награды для отображения в списке."""
    if isinstance(reward, FixedSPReward):
        return f"💰 {reward.amount:,} {reward.currency}"
    elif isinstance(reward, RtpSPReward):
        return f"📊 RTP {reward.percentage * 100:.1f}%  {reward.min:,} – {reward.max:,}  {reward.currency}"
    elif isinstance(reward, FreeplaySPReward):
        return f"🎰 {reward.spins} Free Spins on {reward.game_name}"
    elif isinstance(reward, PacksSPReward):
        return f"📦 {reward.num_packs}x Pack {reward.pack_id}"
    elif isinstance(reward, PurchaseSPReward):
        return f"🎁 Purchase  {reward.shop_type}"
    return f"🎁 {type(reward).__name__}"


def get_default_sp_reward() -> SPReward:
    return FixedSPReward(currency="Chips", amount=1000000)


def render_sp_rewards_editor(prefix: str, existing_rewards: List[SPReward]) -> List[SPReward]:
    """
    Редактор списка наград SinglePick.
    Аналог render_rewards_editor из rewards_editor.py.
    Состояние хранится в session_state по ключу f"{prefix}_sp_rewards".
    """
    rewards_key  = f"{prefix}_sp_rewards"
    editing_key  = f"{prefix}_sp_editing_idx"
    show_add_key = f"{prefix}_sp_show_add"

    # Инициализация — только при первом вызове или если список пришёл снаружи
    if rewards_key not in st.session_state:
        st.session_state[rewards_key] = list(existing_rewards) if existing_rewards else []
    if editing_key not in st.session_state:
        st.session_state[editing_key] = -1
    if show_add_key not in st.session_state:
        st.session_state[show_add_key] = False

    rewards: List[SPReward] = st.session_state[rewards_key]

    st.write("**Награды:**")

    # ── Список существующих наград ────────────────────────────────────────
    delete_indices = []
    for i, reward in enumerate(rewards):
        cols = st.columns([4, 1, 1])
        with cols[0]:
            st.write(f"{i + 1}. {_reward_desc(reward)}")
        with cols[1]:
            if st.button("✏️", key=f"{prefix}_sp_edit_{i}"):
                st.session_state[editing_key] = i
                st.session_state[show_add_key] = False
                st.rerun()
        with cols[2]:
            if st.button("❌", key=f"{prefix}_sp_del_{i}"):
                delete_indices.append(i)

    if delete_indices:
        for idx in sorted(delete_indices, reverse=True):
            del st.session_state[rewards_key][idx]
        # Сбросить индекс редактирования если удалили редактируемую
        if st.session_state[editing_key] in delete_indices:
            st.session_state[editing_key] = -1
        st.rerun()

    # ── Кнопка добавления ─────────────────────────────────────────────────
    if st.button("➕ Добавить награду", key=f"{prefix}_sp_add_btn"):
        st.session_state[show_add_key] = True
        st.session_state[editing_key] = -1
        st.rerun()

    # ── Редактирование существующей награды ───────────────────────────────
    editing_idx = st.session_state[editing_key]
    if 0 <= editing_idx < len(rewards):
        with st.expander(f"✏️ Редактирование награды #{editing_idx + 1}", expanded=True):
            new_reward = render_sp_reward_widget(
                prefix=f"{prefix}_sp_edit",
                index=editing_idx,
                existing=rewards[editing_idx],
            )
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button("💾 Сохранить", key=f"{prefix}_sp_save_edit_{editing_idx}"):
                    st.session_state[rewards_key][editing_idx] = new_reward
                    st.session_state[editing_key] = -1
                    st.rerun()
            with col_cancel:
                if st.button("❌ Отмена", key=f"{prefix}_sp_cancel_edit_{editing_idx}"):
                    st.session_state[editing_key] = -1
                    st.rerun()

    # ── Добавление новой награды ──────────────────────────────────────────
    if st.session_state[show_add_key]:
        with st.expander("➕ Новая награда", expanded=True):
            new_reward = render_sp_reward_widget(
                prefix=f"{prefix}_sp_new",
                index=len(rewards),
            )
            col_add, col_cancel = st.columns(2)
            with col_add:
                if st.button("✅ Добавить", key=f"{prefix}_sp_confirm_add"):
                    st.session_state[rewards_key].append(new_reward)
                    st.session_state[show_add_key] = False
                    st.rerun()
            with col_cancel:
                if st.button("❌ Отмена", key=f"{prefix}_sp_cancel_add"):
                    st.session_state[show_add_key] = False
                    st.rerun()

    return rewards
