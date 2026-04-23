import streamlit as st
from typing import Optional
from models.singlepick import (
    SPReward,
    FixedSPReward,
    RtpSPReward,
    PurchaseSPReward,
    FreeplaySPReward,
    PacksSPReward,
)

SP_REWARD_TYPES = [
    "Chips",
    "VariableChips",
    "MLM",
    "Loyalty Point",
    "Vip Points",
    "Sweepstakes",
    "BoardGameDices",
    "BoardGameBuilds",
    "BoardGameRareBuilds",
    "FreePlays",
    "Packs",
    "PurchaseReward",
]

_CURRENCY_MAP = {
    "Chips":               "Chips",
    "MLM":                 "Tickets",
    "Loyalty Point":       "Loyalty",
    "Vip Points":          "VipPoints",
    "Sweepstakes":         "Entries_Name",
    "BoardGameDices":      "BoardGameDices",
    "BoardGameBuilds":     "BoardGameBuilds",
    "BoardGameRareBuilds": "BoardGameRareBuilds",
}

_CURRENCY_TO_TYPE = {v: k for k, v in _CURRENCY_MAP.items()}


def _detect_type(existing: Optional[SPReward]) -> str:
    if isinstance(existing, RtpSPReward):
        return "VariableChips"
    if isinstance(existing, PurchaseSPReward):
        return "PurchaseReward"
    if isinstance(existing, FreeplaySPReward):
        return "FreePlays"
    if isinstance(existing, PacksSPReward):
        return "Packs"
    if isinstance(existing, FixedSPReward):
        return _CURRENCY_TO_TYPE.get(existing.currency, "Chips")
    return "Chips"


def render_sp_reward_widget(
    prefix: str,
    index: int,
    existing: Optional[SPReward] = None,
) -> SPReward:
    current_type = _detect_type(existing)

    # Тип награды — над полями
    reward_type = st.selectbox(
        "Тип награды",
        options=SP_REWARD_TYPES,
        index=SP_REWARD_TYPES.index(current_type) if current_type in SP_REWARD_TYPES else 0,
        key=f"{prefix}_{index}_reward_type",
    )

    # ── Фиксированные валюты ──────────────────────────────────────────────
    if reward_type in _CURRENCY_MAP:
        currency = _CURRENCY_MAP[reward_type]
        is_board = reward_type in ("BoardGameDices", "BoardGameBuilds", "BoardGameRareBuilds")

        if is_board:
            default_amt = existing.amount if isinstance(existing, FixedSPReward) else 2
            amount = st.number_input(
                "Amount",
                value=int(default_amt),
                min_value=1, step=1,
                key=f"{prefix}_{index}_amount",
            )
            return FixedSPReward(currency=currency, amount=int(amount))
        else:
            default_amt = existing.amount if isinstance(existing, FixedSPReward) else 250000
            amount = st.number_input(
                "Amount",
                value=float(default_amt),
                min_value=0.0, step=1000.0, format="%.0f",
                key=f"{prefix}_{index}_amount",
            )
            return FixedSPReward(currency=currency, amount=int(amount))

    # ── VariableChips (RtpReward) ─────────────────────────────────────────
    elif reward_type == "VariableChips":
        c1, c2, c3 = st.columns(3)
        with c1:
            pct = st.number_input(
                "Percentage",
                value=existing.percentage if isinstance(existing, RtpSPReward) else 0.03,
                min_value=0.0, max_value=1.0, step=0.001, format="%.3f",
                key=f"{prefix}_{index}_pct",
            )
        with c2:
            min_v = st.number_input(
                "Min",
                value=float(existing.min) if isinstance(existing, RtpSPReward) else 250000.0,
                min_value=0.0, step=10000.0, format="%.0f",
                key=f"{prefix}_{index}_min",
            )
        with c3:
            max_v = st.number_input(
                "Max",
                value=float(existing.max) if isinstance(existing, RtpSPReward) else 10000000.0,
                min_value=0.0, step=100000.0, format="%.0f",
                key=f"{prefix}_{index}_max",
            )
        return RtpSPReward(
            currency="Chips",
            percentage=float(pct),
            min=int(min_v),
            max=int(max_v),
        )

    # ── FreePlays ─────────────────────────────────────────────────────────
    elif reward_type == "FreePlays":
        c1, c2 = st.columns(2)
        with c1:
            game = st.text_input(
                "Game Name",
                value=existing.game_name if isinstance(existing, FreeplaySPReward) else "Buffalo",
                key=f"{prefix}_{index}_game",
            )
        with c2:
            spins = st.number_input(
                "Spins",
                value=existing.spins if isinstance(existing, FreeplaySPReward) else 16,
                min_value=1, step=1,
                key=f"{prefix}_{index}_spins",
            )
        return FreeplaySPReward(game_name=game, spins=int(spins))

    # ── Packs ─────────────────────────────────────────────────────────────
    elif reward_type == "Packs":
        c1, c2 = st.columns(2)
        with c1:
            pack_id = st.text_input(
                "Pack ID",
                value=existing.pack_id if isinstance(existing, PacksSPReward) else "sellPack50",
                key=f"{prefix}_{index}_packid",
            )
        with c2:
            num_packs = st.number_input(
                "Number of Packs",
                value=existing.num_packs if isinstance(existing, PacksSPReward) else 4,
                min_value=1, step=1,
                key=f"{prefix}_{index}_numpacks",
            )
        return PacksSPReward(pack_id=pack_id, num_packs=int(num_packs))

    # ── PurchaseReward ────────────────────────────────────────────────────
    else:
        c1, c2 = st.columns(2)
        with c1:
            shop_type = st.text_input(
                "ShopType",
                value=existing.shop_type if isinstance(existing, PurchaseSPReward) else "",
                key=f"{prefix}_{index}_shop_type",
            )
        with c2:
            shop_name = st.text_input(
                "ShopName",
                value=existing.shop_name if isinstance(existing, PurchaseSPReward) else "",
                key=f"{prefix}_{index}_shop_name",
            )
        return PurchaseSPReward(shop_type=shop_type, shop_name=shop_name)
