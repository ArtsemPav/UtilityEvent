from dataclasses import dataclass
from typing import Union
from .base import Serializable

# ---------- Конкретные типы наград ----------
@dataclass
class FixedReward(Serializable):
    currency: str
    amount: float

    def to_dict(self) -> dict:
        return {"FixedReward": {"Currency": self.currency, "Amount": self.amount}}

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("FixedReward", {})
        return cls(currency=inner.get("Currency", "Chips"), amount=inner.get("Amount", 0.0))

@dataclass
class RtpReward(Serializable):
    currency: str
    percentage: float
    min: float
    max: float

    def to_dict(self) -> dict:
        return {"RtpReward": {"Currency": self.currency, "Percentage": self.percentage, "Min": self.min, "Max": self.max}}

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("RtpReward", {})
        return cls(
            currency=inner.get("Currency", "Chips"),
            percentage=inner.get("Percentage", 0.03),
            min=inner.get("Min", 250000.0),
            max=inner.get("Max", 10000000.0)
        )

@dataclass
class FreeplayUnlockReward(Serializable):
    game_name: str
    spins: int

    def to_dict(self) -> dict:
        return {"FreeplayUnlockReward": {"GameName": self.game_name, "Spins": self.spins}}

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("FreeplayUnlockReward", {})
        return cls(game_name=inner.get("GameName", "Buffalo"), spins=inner.get("Spins", 16))

@dataclass
class CollectableSellPacksReward(Serializable):
    pack_id: str
    num_packs: int

    def to_dict(self) -> dict:
        return {"CollectableSellPacksReward": {"PackId": self.pack_id, "NumPacks": self.num_packs}}

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("CollectableSellPacksReward", {})
        return cls(pack_id=inner.get("PackId", "sellPack50"), num_packs=inner.get("NumPacks", 4))

@dataclass
class CollectableMagicPacksReward(Serializable):
    pack_id: str
    num_packs: int

    def to_dict(self) -> dict:
        return {"CollectableMagicPacksReward": {"PackId": self.pack_id, "NumPacks": self.num_packs}}

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("CollectableMagicPacksReward", {})
        return cls(pack_id=inner.get("PackId", "magicPack50"), num_packs=inner.get("NumPacks", 1))

# ---------- Обёртка Reward ----------
RewardType = Union[FixedReward, RtpReward, FreeplayUnlockReward, CollectableSellPacksReward, CollectableMagicPacksReward]

@dataclass
class Reward(Serializable):
    data: RewardType

    def to_dict(self) -> dict:
        return self.data.to_dict()

    @classmethod
    def from_dict(cls, data: dict):
        # Определяем тип награды по наличию ключа
        if "FixedReward" in data:
            inner = FixedReward.from_dict(data)
        elif "RtpReward" in data:
            inner = RtpReward.from_dict(data)
        elif "FreeplayUnlockReward" in data:
            inner = FreeplayUnlockReward.from_dict(data)
        elif "CollectableSellPacksReward" in data:
            inner = CollectableSellPacksReward.from_dict(data)
        elif "CollectableMagicPacksReward" in data:
            inner = CollectableMagicPacksReward.from_dict(data)
        else:
            # fallback
            inner = FixedReward(currency="Chips", amount=0.0)
        return cls(data=inner)