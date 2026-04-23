from dataclasses import dataclass, field
from typing import Union
from .base import Serializable


# ---------- SPReward ----------

@dataclass
class FixedSPReward(Serializable):
    currency: str
    amount: int

    def to_dict(self) -> dict:
        return {"FixedReward": {"Currency": self.currency, "Amount": self.amount}}

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("FixedReward", {})
        return cls(currency=inner.get("Currency", "Chips"), amount=inner.get("Amount", 0))


@dataclass
class RtpSPReward(Serializable):
    currency: str
    percentage: float
    min: int
    max: int

    def to_dict(self) -> dict:
        return {"RtpReward": {"Currency": self.currency, "Percentage": self.percentage, "Min": self.min, "Max": self.max}}

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("RtpReward", {})
        return cls(
            currency=inner.get("Currency", "Chips"),
            percentage=inner.get("Percentage", 0.01),
            min=inner.get("Min", 0),
            max=inner.get("Max", 0),
        )


@dataclass
class PurchaseSPReward(Serializable):
    shop_type: str

    def to_dict(self) -> dict:
        return {"PurchaseReward": {"ShopType": self.shop_type}}

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("PurchaseReward", {})
        return cls(shop_type=inner.get("ShopType", ""))


@dataclass
class FreeplaySPReward(Serializable):
    game_name: str
    spins: int

    def to_dict(self) -> dict:
        return {"FreeplayUnlockReward": {"GameName": self.game_name, "Spins": self.spins}}

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("FreeplayUnlockReward", {})
        return cls(game_name=inner.get("GameName", "Buffalo"), spins=inner.get("Spins", 16))


@dataclass
class PacksSPReward(Serializable):
    pack_id: str
    num_packs: int

    def to_dict(self) -> dict:
        return {"CollectableSellPacksReward": {"PackId": self.pack_id, "NumPacks": self.num_packs}}

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("CollectableSellPacksReward", {})
        return cls(pack_id=inner.get("PackId", "sellPack50"), num_packs=inner.get("NumPacks", 4))


SPReward = Union[FixedSPReward, RtpSPReward, PurchaseSPReward, FreeplaySPReward, PacksSPReward]


def _sp_reward_from_dict(data: dict) -> SPReward:
    """Определяет тип SPReward по ключу и десериализует."""
    if "FixedReward" in data:
        return FixedSPReward.from_dict(data)
    elif "RtpReward" in data:
        return RtpSPReward.from_dict(data)
    elif "PurchaseReward" in data:
        return PurchaseSPReward.from_dict(data)
    elif "FreeplayUnlockReward" in data:
        return FreeplaySPReward.from_dict(data)
    elif "CollectableSellPacksReward" in data:
        return PacksSPReward.from_dict(data)
    else:
        return FixedSPReward(currency="Chips", amount=0)


# ---------- Jackpot ----------

@dataclass
class FixedJackpot(Serializable):
    min: int
    max: int

    def to_dict(self) -> dict:
        return {"FixedJackpot": {"Min": self.min, "Max": self.max}}

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("FixedJackpot", {})
        return cls(min=inner.get("Min", 0), max=inner.get("Max", 0))


@dataclass
class CIJackpot(Serializable):
    min: int
    max: int
    ci_min: int
    ci_max: int

    def to_dict(self) -> dict:
        return {"CIJackpot": {"Min": self.min, "Max": self.max, "CIMin": self.ci_min, "CIMax": self.ci_max}}

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("CIJackpot", {})
        return cls(
            min=inner.get("Min", 0),
            max=inner.get("Max", 0),
            ci_min=inner.get("CIMin", 0),
            ci_max=inner.get("CIMax", 0),
        )


def _jackpot_from_dict(data: dict) -> Union[FixedJackpot, CIJackpot]:
    """Определяет тип джекпота по ключу и десериализует."""
    if "CIJackpot" in data:
        return CIJackpot.from_dict(data)
    else:
        return FixedJackpot.from_dict(data)


# ---------- Pick ----------

@dataclass
class RewardPick(Serializable):
    reward: list
    weight: int
    possible_max: int

    def to_dict(self) -> dict:
        return {
            "RewardPick": {
                "Reward": [r.to_dict() for r in self.reward],
                "Weight": self.weight,
                "PossibleMax": self.possible_max,
            }
        }

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("RewardPick", {})
        return cls(
            reward=[_sp_reward_from_dict(r) for r in inner.get("Reward", [])],
            weight=inner.get("Weight", 1),
            possible_max=inner.get("PossibleMax", 0),
        )


@dataclass
class JackpotPick(Serializable):
    jackpot: Union[FixedJackpot, CIJackpot]
    weight: int
    possible_max: int

    def to_dict(self) -> dict:
        # Содержимое джекпота встраивается напрямую в JackpotPick
        jackpot_dict = self.jackpot.to_dict()
        inner = {**jackpot_dict, "Weight": self.weight, "PossibleMax": self.possible_max}
        return {"JackpotPick": inner}

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("JackpotPick", {})
        jackpot = _jackpot_from_dict(inner)
        return cls(
            jackpot=jackpot,
            weight=inner.get("Weight", 1),
            possible_max=inner.get("PossibleMax", 0),
        )


@dataclass
class RetryPick(Serializable):
    reward: list
    weight: int
    possible_max: int

    def to_dict(self) -> dict:
        return {
            "RetryPick": {
                "Reward": [r.to_dict() for r in self.reward],
                "Weight": self.weight,
                "PossibleMax": self.possible_max,
            }
        }

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("RetryPick", {})
        return cls(
            reward=[_sp_reward_from_dict(r) for r in inner.get("Reward", [])],
            weight=inner.get("Weight", 0),
            possible_max=inner.get("PossibleMax", 0),
        )


Pick = Union[RewardPick, JackpotPick, RetryPick]


def _pick_from_dict(data: dict) -> Pick:
    """Определяет тип Pick по ключу и десериализует."""
    if "RewardPick" in data:
        return RewardPick.from_dict(data)
    elif "JackpotPick" in data:
        return JackpotPick.from_dict(data)
    elif "RetryPick" in data:
        return RetryPick.from_dict(data)
    else:
        return RewardPick(reward=[], weight=1, possible_max=0)


# ---------- Wedge ----------

@dataclass
class Wedge(Serializable):
    reward: list
    weight: int

    def to_dict(self) -> dict:
        # Wedge сериализуется как RewardPick без PossibleMax
        return {
            "RewardPick": {
                "Reward": [r.to_dict() for r in self.reward],
                "Weight": self.weight,
            }
        }

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("RewardPick", {})
        return cls(
            reward=[_sp_reward_from_dict(r) for r in inner.get("Reward", [])],
            weight=inner.get("Weight", 1),
        )


# ---------- PickersConfig ----------

@dataclass
class PickersConfig(Serializable):
    picks: list
    total_pick_on_board: int
    pick_until_win: int

    def to_dict(self) -> dict:
        return {
            "Picks": [p.to_dict() for p in self.picks],
            "TotalPickOnBoard": self.total_pick_on_board,
            "PickUntilWin": self.pick_until_win,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            picks=[_pick_from_dict(p) for p in data.get("Picks", [])],
            total_pick_on_board=data.get("TotalPickOnBoard", 0),
            pick_until_win=data.get("PickUntilWin", 0),
        )


# ---------- WheelConfig ----------

@dataclass
class WheelConfig(Serializable):
    wedges: list

    def to_dict(self) -> dict:
        return {"Wedges": [w.to_dict() for w in self.wedges]}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(wedges=[Wedge.from_dict(w) for w in data.get("Wedges", [])])


# ---------- ConfigSet ----------

@dataclass
class ConfigSet(Serializable):
    content: Union[PickersConfig, WheelConfig]

    def to_dict(self) -> dict:
        if isinstance(self.content, PickersConfig):
            return {"Pickers": self.content.to_dict()}
        else:
            return {"Wheel": self.content.to_dict()}

    @classmethod
    def from_dict(cls, data: dict):
        if "Pickers" in data:
            content = PickersConfig.from_dict(data["Pickers"])
        elif "Wheel" in data:
            content = WheelConfig.from_dict(data["Wheel"])
        else:
            content = PickersConfig(picks=[], total_pick_on_board=0, pick_until_win=0)
        return cls(content=content)


# ---------- SinglePickConfig ----------

@dataclass
class SinglePickConfig(Serializable):
    config_sets: dict

    def to_dict(self) -> dict:
        return {"ConfigSets": {name: cs.to_dict() for name, cs in self.config_sets.items()}}

    @classmethod
    def from_dict(cls, data: dict):
        if "ConfigSets" not in data:
            raise ValueError("Missing 'ConfigSets' key")
        config_sets = {
            name: ConfigSet.from_dict(cs_data)
            for name, cs_data in data["ConfigSets"].items()
        }
        return cls(config_sets=config_sets)
