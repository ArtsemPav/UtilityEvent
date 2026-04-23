import streamlit as st
from typing import Optional
from models.rewards import (
    Reward,
    FixedReward,
    RtpReward,
    FreeplayUnlockReward,
    CollectableSellPacksReward,
    CollectableMagicPacksReward,
)
from utils.constants import REWARD_TYPES

def render_reward_widget(prefix: str, index: int, existing: Optional[Reward] = None) -> Reward:
    """Возвращает объект Reward."""
    # Определяем текущий тип
    current_type = "Chips"
    if existing:
        data = existing.data
        if isinstance(data, FixedReward):
            if data.currency in ["BoardGameDices", "BoardGameBuilds", "BoardGameRareBuilds"]:
                current_type = data.currency
            elif data.currency == "Chips":
                current_type = "Chips"
            elif data.currency == "Tickets":
                current_type = "MLM"
            elif data.currency == "Loyalty":
                current_type = "Loyalty Point"
            elif data.currency == "VipPoints":
                current_type = "Vip Points"
            elif data.currency == "Entries_Name":
                current_type = "Sweepstakes"
        elif isinstance(data, RtpReward):
            current_type = "VariableChips"
        elif isinstance(data, FreeplayUnlockReward):
            current_type = "FreePlays"
        elif isinstance(data, CollectableSellPacksReward):
            current_type = "Packs"
        elif isinstance(data, CollectableMagicPacksReward):
            current_type = "MagicPacks"

    col1, col2 = st.columns([1, 3])
    with col1:
        reward_type = st.selectbox(
            "Тип награды",
            options=REWARD_TYPES,
            index=REWARD_TYPES.index(current_type) if current_type in REWARD_TYPES else 0,
            key=f"{prefix}_reward_{index}_type"
        )
    with col2:
        if reward_type in ["Chips", "MLM", "Loyalty Point", "Vip Points", "Sweepstakes"]:
            currency_map = {
                "Chips": "Chips",
                "MLM": "Tickets",
                "Loyalty Point": "Loyalty",
                "Vip Points": "VipPoints",
                "Sweepstakes": "Entries_Name",
            }
            curr = currency_map[reward_type]
            default_amt = existing.data.amount if existing and isinstance(existing.data, FixedReward) else 250000.0
            amount = st.number_input(
                "Amount",
                value=float(default_amt),
                min_value=0.0,
                step=1000.0,
                format="%.2f",
                key=f"{prefix}_reward_{index}_amount"
            )
            return Reward(data=FixedReward(currency=curr, amount=float(amount)))

        elif reward_type == "VariableChips":
            c1, c2, c3 = st.columns(3)
            with c1:
                pct = st.number_input(
                    "Percentage",
                    value=existing.data.percentage if existing and isinstance(existing.data, RtpReward) else 0.03,
                    min_value=0.0, max_value=1.0, step=0.01, format="%.3f",
                    key=f"{prefix}_reward_{index}_pct"
                )
            with c2:
                min_v = st.number_input(
                    "Min",
                    value=existing.data.min if existing and isinstance(existing.data, RtpReward) else 250000.0,
                    min_value=0.0, step=10000.0, format="%.2f",
                    key=f"{prefix}_reward_{index}_min"
                )
            with c3:
                max_v = st.number_input(
                    "Max",
                    value=existing.data.max if existing and isinstance(existing.data, RtpReward) else 10000000.0,
                    min_value=0.0, step=100000.0, format="%.2f",
                    key=f"{prefix}_reward_{index}_max"
                )
            return Reward(data=RtpReward(currency="Chips", percentage=float(pct), min=float(min_v), max=float(max_v)))

        elif reward_type == "FreePlays":
            c1, c2 = st.columns(2)
            with c1:
                game = st.text_input(
                    "Game Name",
                    value=existing.data.game_name if existing and isinstance(existing.data, FreeplayUnlockReward) else "Buffalo",
                    key=f"{prefix}_reward_{index}_game"
                )
            with c2:
                spins = st.number_input(
                    "Spins",
                    value=existing.data.spins if existing and isinstance(existing.data, FreeplayUnlockReward) else 16,
                    min_value=1, step=1,
                    key=f"{prefix}_reward_{index}_spins"
                )
            return Reward(data=FreeplayUnlockReward(game_name=game, spins=int(spins)))

        elif reward_type == "Packs":
            c1, c2 = st.columns(2)
            with c1:
                pack = st.text_input(
                    "Pack ID",
                    value=existing.data.pack_id if existing and isinstance(existing.data, CollectableSellPacksReward) else "sellPack50",
                    key=f"{prefix}_reward_{index}_packid"
                )
            with c2:
                num = st.number_input(
                    "Number of Packs",
                    value=existing.data.num_packs if existing and isinstance(existing.data, CollectableSellPacksReward) else 4,
                    min_value=1, step=1,
                    key=f"{prefix}_reward_{index}_numpacks"
                )
            return Reward(data=CollectableSellPacksReward(pack_id=pack, num_packs=int(num)))

        elif reward_type == "MagicPacks":
            c1, c2 = st.columns(2)
            with c1:
                pack = st.text_input(
                    "Pack ID",
                    value=existing.data.pack_id if existing and isinstance(existing.data, CollectableMagicPacksReward) else "magicPack50",
                    key=f"{prefix}_reward_{index}_magicpackid"
                )
            with c2:
                num = st.number_input(
                    "Number of Packs",
                    value=existing.data.num_packs if existing and isinstance(existing.data, CollectableMagicPacksReward) else 1,
                    min_value=1, max_value=5, step=1,
                    key=f"{prefix}_reward_{index}_magicnumpacks"
                )
            return Reward(data=CollectableMagicPacksReward(pack_id=pack, num_packs=int(num)))

        elif reward_type in ["BoardGameDices", "BoardGameBuilds", "BoardGameRareBuilds"]:
            curr = reward_type
            default_amt = existing.data.amount if existing and isinstance(existing.data, FixedReward) else 2
            amount = st.number_input(
                "Amount",
                value=int(default_amt),
                min_value=1, step=1,
                key=f"{prefix}_reward_{index}_board_amount"
            )
            return Reward(data=FixedReward(currency=curr, amount=float(amount)))

    return Reward(data=FixedReward(currency="Chips", amount=0.0))