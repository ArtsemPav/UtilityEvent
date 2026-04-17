from typing import List, Optional, Union
from models.minbet import FixedMinBet, VariableMinBet
from models.goals import Goal, FixedGoal, SpinpadGoal, ConsecutiveWinsGoal, TotalCoinsPerDayGoal, TotalCoinsPerDayWithSpinLimiterGoal, FixedGoalWithSpinLimiterGoal
from models.rewards import Reward, FixedReward, RtpReward, FreeplayUnlockReward, CollectableSellPacksReward
from models.nodes import ProgressNode, EntriesNode, DummyNode
from models.event import PossibleNodeEventData, Segment, Stage

# ---------- MinBet ----------
def build_fixed_minbet(amount: float) -> FixedMinBet:
    return FixedMinBet(amount=amount)

def build_variable_minbet(variable: float, min_val: float, max_val: float) -> VariableMinBet:
    return VariableMinBet(variable=variable, min=min_val, max=max_val)

# ---------- Goals ----------
def build_fixed_goal(target: int) -> Goal:
    return Goal(type=["Spins"], params=FixedGoal(target=target))

def build_spinpad_goal(multiplier: float, min_val: int, max_val: int) -> Goal:
    return Goal(type=["Spins"], params=SpinpadGoal(multiplier=multiplier, min=min_val, max=max_val))

# ... аналогичные функции для остальных типов целей

# ---------- Rewards ----------
def build_fixed_chips_reward(amount: float) -> Reward:
    return Reward(data=FixedReward(currency="Chips", amount=amount))

def build_rtp_chips_reward(percentage: float, min_val: float, max_val: float) -> Reward:
    return Reward(data=RtpReward(currency="Chips", percentage=percentage, min=min_val, max=max_val))

# ... остальные типы

# ---------- Nodes ----------
def build_progress_node(
    node_id: int,
    next_node_ids: List[int],
    game_list: List[str],
    min_bet: Union[FixedMinBet, VariableMinBet],
    goal: Goal,
    rewards: List[Reward],
    is_last_node: bool = False,
    mini_game: str = "FlatReward",
    button_action_text: str = "PLAY NOW!",
    button_action_type: str = "",
    button_action_data: str = "",
    custom_texts: List[str] = None,
    possible_item_collect: str = "",
    hide_loading_screen: bool = False,
    prize_box_index: int = -1,
) -> ProgressNode:
    return ProgressNode(
        node_id=node_id,
        next_node_ids=next_node_ids,
        game_list=game_list,
        min_bet=min_bet,
        goal=goal,
        rewards=rewards,
        is_last_node=is_last_node,
        mini_game=mini_game,
        button_action_text=button_action_text,
        button_action_type=button_action_type,
        button_action_data=button_action_data,
        custom_texts=custom_texts or [],
        possible_item_collect=possible_item_collect,
        hide_loading_screen=hide_loading_screen,
        prize_box_index=prize_box_index,
    )

# Аналогично для EntriesNode и DummyNode

# ---------- Event ----------
def build_node_event(
    event_id: str,
    min_level: int,
    segment: str,
    asset_bundle_path: str,
    blocker_prefab_path: str,
    roundel_prefab_path: str,
    event_card_prefab_path: str,
    node_completion_prefab_path: str,
    content_key: str,
    number_of_repeats: int,
    entry_types: List[str],
    segments: Optional[dict] = None,
    is_roundel_hidden: bool = False,
    use_node_failed_notification: bool = False,
    is_prize_pursuit: bool = False,
    use_force_landscape_on_web: bool = False,
    show_roundel_on_all_machines: bool = False,
) -> PossibleNodeEventData:
    return PossibleNodeEventData(
        event_id=event_id,
        min_level=min_level,
        segment=segment,
        asset_bundle_path=asset_bundle_path,
        blocker_prefab_path=blocker_prefab_path,
        roundel_prefab_path=roundel_prefab_path,
        event_card_prefab_path=event_card_prefab_path,
        node_completion_prefab_path=node_completion_prefab_path,
        content_key=content_key,
        number_of_repeats=number_of_repeats,
        entry_types=entry_types,
        segments=segments or {},
        is_roundel_hidden=is_roundel_hidden,
        use_node_failed_notification=use_node_failed_notification,
        is_prize_pursuit=is_prize_pursuit,
        use_force_landscape_on_web=use_force_landscape_on_web,
        show_roundel_on_all_machines=show_roundel_on_all_machines,
    )