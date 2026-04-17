from dataclasses import dataclass
from .base import Serializable

@dataclass
class FixedMinBet(Serializable):
    amount: float

    def to_dict(self) -> dict:
        return {"FixedMinBet": {"MinBet": self.amount}}

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("FixedMinBet", {})
        return cls(amount=inner.get("MinBet", 250000.0))

@dataclass
class VariableMinBet(Serializable):
    variable: float
    min: float
    max: float

    def to_dict(self) -> dict:
        return {"MinBetVariable": {"Variable": self.variable, "Min": self.min, "Max": self.max}}

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("MinBetVariable", {})
        return cls(
            variable=inner.get("Variable", 0.8),
            min=inner.get("Min", 25000.0),
            max=inner.get("Max", 5000000.0)
        )