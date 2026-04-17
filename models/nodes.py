from dataclasses import dataclass, field
from typing import List, Optional, Union
from .base import Serializable
from .minbet import FixedMinBet, VariableMinBet
from .goals import Goal
from .rewards import Reward

# ---------- ProgressNode ----------
@dataclass
class ProgressNode(Serializable):
    node_id: int
    next_node_ids: List[int]
    game_list: List[str]
    min_bet: Union[FixedMinBet, VariableMinBet]
    goal: Goal
    rewards: List[Reward]
    is_last_node: bool = False
    resegment_flag: bool = False
    mini_game: str = "FlatReward"
    contribution_level: str = "Node"
    button_action_type: str = ""
    button_action_data: str = ""
    button_action_text: str = "PLAY NOW!"
    custom_texts: List[str] = field(default_factory=list)
    possible_item_collect: str = ""
    hide_loading_screen: bool = False
    prize_box_index: int = -1

    def to_dict(self) -> dict:
        result = {
            "ProgressNode": {
                "NodeID": self.node_id,
                "NextNodeID": self.next_node_ids,
                "GameList": self.game_list,
                "MinBet": self.min_bet.to_dict(),
                "Goal": self.goal.to_dict(),
                "Rewards": [r.to_dict() for r in self.rewards],
                "IsLastNode": self.is_last_node,
                "ResegmentFlag": self.resegment_flag,
                "MiniGame": self.mini_game,
                "ContributionLevel": self.contribution_level,
                "ButtonActionType": self.button_action_type,
                "ButtonActionData": self.button_action_data,
                "ButtonActionText": self.button_action_text,
                "CustomTexts": self.custom_texts,
                "HideLoadingScreenForReward": self.hide_loading_screen,
            }
        }
        if self.possible_item_collect:
            result["ProgressNode"]["PossibleItemCollect"] = self.possible_item_collect
        if self.prize_box_index > 0:
            result["ProgressNode"]["PrizeBoxIndex"] = self.prize_box_index
        return result

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("ProgressNode", {})
        # MinBet
        min_bet_data = inner.get("MinBet", {})
        if "FixedMinBet" in min_bet_data:
            min_bet = FixedMinBet.from_dict(min_bet_data)
        else:
            min_bet = VariableMinBet.from_dict(min_bet_data)
        # Goal
        goal = Goal.from_dict(inner.get("Goal", {}))
        # Rewards
        rewards = [Reward.from_dict(r) for r in inner.get("Rewards", [])]
        return cls(
            node_id=inner.get("NodeID", 1),
            next_node_ids=inner.get("NextNodeID", [2]),
            game_list=inner.get("GameList", ["AllGames"]),
            min_bet=min_bet,
            goal=goal,
            rewards=rewards,
            is_last_node=inner.get("IsLastNode", False),
            resegment_flag=inner.get("ResegmentFlag", False),
            mini_game=inner.get("MiniGame", "FlatReward"),
            contribution_level=inner.get("ContributionLevel", "Node"),
            button_action_type=inner.get("ButtonActionType", ""),
            button_action_data=inner.get("ButtonActionData", ""),
            button_action_text=inner.get("ButtonActionText", "PLAY NOW!"),
            custom_texts=inner.get("CustomTexts", []),
            possible_item_collect=inner.get("PossibleItemCollect", ""),
            hide_loading_screen=inner.get("HideLoadingScreenForReward", False),
            prize_box_index=inner.get("PrizeBoxIndex", -1),
        )

# ---------- EntriesNode ----------
@dataclass
class EntriesNode(Serializable):
    node_id: int
    game_list: List[str]
    min_bet: Union[FixedMinBet, VariableMinBet]
    goal_types: List[str]
    entry_types: List[str]
    resegment_flag: bool = False
    button_action_type: str = ""
    button_action_data: str = ""
    button_action_text: str = "PLAY NOW!"
    custom_texts: List[str] = field(default_factory=list)
    possible_item_collect: str = "Default"
    prize_box_index: int = -1

    def to_dict(self) -> dict:
        result = {
            "EntriesNode": {
                "NodeID": self.node_id,
                "GameList": self.game_list,
                "MinBet": self.min_bet.to_dict(),
                "GoalType": self.goal_types,
                "ResegmentFlag": self.resegment_flag,
                "ButtonActionType": self.button_action_type,
                "ButtonActionData": self.button_action_data,
                "ButtonActionText": self.button_action_text,
                "CustomTexts": self.custom_texts,
                "PossibleItemCollect": self.possible_item_collect,
                "EntryTypes": self.entry_types,
            }
        }
        if self.prize_box_index > 0:
            result["EntriesNode"]["PrizeBoxIndex"] = self.prize_box_index
        return result

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("EntriesNode", {})
        min_bet_data = inner.get("MinBet", {})
        if "FixedMinBet" in min_bet_data:
            min_bet = FixedMinBet.from_dict(min_bet_data)
        else:
            min_bet = VariableMinBet.from_dict(min_bet_data)
        return cls(
            node_id=inner.get("NodeID", 1),
            game_list=inner.get("GameList", ["AllGames"]),
            min_bet=min_bet,
            goal_types=inner.get("GoalType", ["Spins"]),
            entry_types=inner.get("EntryTypes", ["MyEvent"]),
            resegment_flag=inner.get("ResegmentFlag", False),
            button_action_type=inner.get("ButtonActionType", ""),
            button_action_data=inner.get("ButtonActionData", ""),
            button_action_text=inner.get("ButtonActionText", "PLAY NOW!"),
            custom_texts=inner.get("CustomTexts", []),
            possible_item_collect=inner.get("PossibleItemCollect", "Default"),
            prize_box_index=inner.get("PrizeBoxIndex", -1),
        )

# ---------- DummyNode ----------
@dataclass
class DummyNode(Serializable):
    node_id: int
    next_node_ids: List[int]
    default_node_id: int
    rewards: List[Reward]
    is_last_node: bool = False
    resegment_flag: bool = False
    mini_game: str = "FlatReward"
    contribution_level: str = "Node"
    button_action_type: str = ""
    button_action_data: str = ""
    button_action_text: str = ""
    custom_texts: List[str] = field(default_factory=list)
    is_choice_event: bool = True
    hide_loading_screen: bool = False
    prize_box_index: int = -1

    def to_dict(self) -> dict:
        result = {
            "DummyNode": {
                "NodeID": self.node_id,
                "NextNodeID": self.next_node_ids,
                "DefaultNodeID": self.default_node_id,
                "Rewards": [r.to_dict() for r in self.rewards],
                "IsLastNode": self.is_last_node,
                "ResegmentFlag": self.resegment_flag,
                "MiniGame": self.mini_game,
                "ContributionLevel": self.contribution_level,
                "ButtonActionType": self.button_action_type,
                "ButtonActionData": self.button_action_data,
                "ButtonActionText": self.button_action_text,
                "CustomTexts": self.custom_texts,
                "IsChoiceEvent": self.is_choice_event,
                "HideLoadingScreenForReward": self.hide_loading_screen,
            }
        }
        if self.prize_box_index > 0:
            result["DummyNode"]["PrizeBoxIndex"] = self.prize_box_index
        return result

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("DummyNode", {})
        rewards = [Reward.from_dict(r) for r in inner.get("Rewards", [])]
        return cls(
            node_id=inner.get("NodeID", 1),
            next_node_ids=inner.get("NextNodeID", [11, 21, 31]),
            default_node_id=inner.get("DefaultNodeID", 1),
            rewards=rewards,
            is_last_node=inner.get("IsLastNode", False),
            resegment_flag=inner.get("ResegmentFlag", False),
            mini_game=inner.get("MiniGame", "FlatReward"),
            contribution_level=inner.get("ContributionLevel", "Node"),
            button_action_type=inner.get("ButtonActionType", ""),
            button_action_data=inner.get("ButtonActionData", ""),
            button_action_text=inner.get("ButtonActionText", ""),
            custom_texts=inner.get("CustomTexts", []),
            is_choice_event=inner.get("IsChoiceEvent", True),
            hide_loading_screen=inner.get("HideLoadingScreenForReward", False),
            prize_box_index=inner.get("PrizeBoxIndex", -1),
        )

# ---------- Union тип и фабрика ----------
Node = Union[ProgressNode, EntriesNode, DummyNode]

def node_from_dict(data: dict) -> Node:
    """Создаёт узел нужного типа из словаря."""
    if "ProgressNode" in data:
        return ProgressNode.from_dict(data)
    elif "EntriesNode" in data:
        return EntriesNode.from_dict(data)
    elif "DummyNode" in data:
        return DummyNode.from_dict(data)
    else:
        raise ValueError(f"Unknown node type in data: {data.keys()}")