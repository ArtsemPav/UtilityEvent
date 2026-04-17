from dataclasses import dataclass, field
from typing import List, Union, Optional
from .base import Serializable

# ---------- Конкретные типы целей ----------
@dataclass
class FixedGoal(Serializable):
    target: int

    def to_dict(self) -> dict:
        return {"FixedGoal": {"Target": self.target}}

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("FixedGoal", {})
        return cls(target=inner.get("Target", 20))

@dataclass
class SpinpadGoal(Serializable):
    multiplier: float
    min: int
    max: int

    def to_dict(self) -> dict:
        return {"SpinpadGoal": {"Multiplier": self.multiplier, "Min": self.min, "Max": self.max}}

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("SpinpadGoal", {})
        return cls(
            multiplier=inner.get("Multiplier", 0.5),
            min=inner.get("Min", 10),
            max=inner.get("Max", 150)
        )

@dataclass
class ConsecutiveWinsGoal(Serializable):
    number_of_streaks_target: int
    multiplier: float
    min: int
    max: int

    def to_dict(self) -> dict:
        return {
            "ConsecutiveWinsGoal": {
                "NumberOfStreaksTarget": self.number_of_streaks_target,
                "WinsInStreakSpinPadGoal": {
                    "Multiplier": self.multiplier,
                    "Min": self.min,
                    "Max": self.max
                }
            }
        }

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("ConsecutiveWinsGoal", {})
        wins_inner = inner.get("WinsInStreakSpinPadGoal", {})
        return cls(
            number_of_streaks_target=inner.get("NumberOfStreaksTarget", 3),
            multiplier=wins_inner.get("Multiplier", 0.01),
            min=wins_inner.get("Min", 2),
            max=wins_inner.get("Max", 5)
        )

@dataclass
class TotalCoinsPerDayGoal(Serializable):
    multiplier: float
    min: int
    max: int

    def to_dict(self) -> dict:
        return {"TotalCoinsPerDay": {"Multiplier": self.multiplier, "Min": self.min, "Max": self.max}}

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("TotalCoinsPerDay", {})
        return cls(
            multiplier=inner.get("Multiplier", 0.5),
            min=inner.get("Min", 10),
            max=inner.get("Max", 150)
        )

@dataclass
class TotalCoinsPerDayWithSpinLimiterGoal(Serializable):
    spin_limiter: int
    multiplier: float
    min: int
    max: int

    def to_dict(self) -> dict:
        return {
            "TotalCoinsPerDayWithSpinLimiter": {
                "SpinLimiter": self.spin_limiter,
                "Multiplier": self.multiplier,
                "Min": self.min,
                "Max": self.max
            }
        }

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("TotalCoinsPerDayWithSpinLimiter", {})
        return cls(
            spin_limiter=inner.get("SpinLimiter", 3),
            multiplier=inner.get("Multiplier", 0.097),
            min=inner.get("Min", 3500000),
            max=inner.get("Max", 50000000)
        )

@dataclass
class FixedGoalWithSpinLimiterGoal(Serializable):
    target: int
    spin_limiter: int

    def to_dict(self) -> dict:
        return {
            "FixedGoalWithSpinLimiter": {
                "Target": self.target,
                "SpinLimiter": self.spin_limiter
            }
        }

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("FixedGoalWithSpinLimiter", {})
        return cls(
            target=inner.get("Target", 10),
            spin_limiter=inner.get("SpinLimiter", 3)
        )

# ---------- Обёртка Goal ----------
GoalParams = Union[
    FixedGoal,
    SpinpadGoal,
    ConsecutiveWinsGoal,
    TotalCoinsPerDayGoal,
    TotalCoinsPerDayWithSpinLimiterGoal,
    FixedGoalWithSpinLimiterGoal,
]

@dataclass
class Goal(Serializable):
    type: List[str]  # например ["Spins"]
    params: GoalParams

    def to_dict(self) -> dict:
        result = {"Type": self.type}
        result.update(self.params.to_dict())
        return result

    @classmethod
    def from_dict(cls, data: dict):
        goal_type = data.get("Type", ["Spins"])
        params_data = {k: v for k, v in data.items() if k != "Type"}

        # Определяем тип параметров по наличию ключа
        if "FixedGoal" in params_data:
            params = FixedGoal.from_dict(params_data)
        elif "SpinpadGoal" in params_data:
            params = SpinpadGoal.from_dict(params_data)
        elif "ConsecutiveWinsGoal" in params_data:
            params = ConsecutiveWinsGoal.from_dict(params_data)
        elif "TotalCoinsPerDay" in params_data:
            params = TotalCoinsPerDayGoal.from_dict(params_data)
        elif "TotalCoinsPerDayWithSpinLimiter" in params_data:
            params = TotalCoinsPerDayWithSpinLimiterGoal.from_dict(params_data)
        elif "FixedGoalWithSpinLimiter" in params_data:
            params = FixedGoalWithSpinLimiterGoal.from_dict(params_data)
        else:
            # fallback
            params = FixedGoal(target=20)
        return cls(type=goal_type, params=params)