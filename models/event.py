from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .base import Serializable
from .nodes import Node, node_from_dict

def get_default_time_warning() -> str:
    """Возвращает текущую дату + 1 месяц в формате ISO 8601 (UTC)."""
    future = datetime.utcnow() + timedelta(days=30)
    return future.strftime("%Y-%m-%dT%H:%M:%SZ")

@dataclass
class Stage(Serializable):
    stage_id: int
    nodes: List[Node] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"StageID": self.stage_id, "Nodes": [n.to_dict() for n in self.nodes]}

    @classmethod
    def from_dict(cls, data: dict):
        nodes = [node_from_dict(n) for n in data.get("Nodes", [])]
        return cls(stage_id=data.get("StageID", 1), nodes=nodes)

@dataclass
class Segment(Serializable):
    name: str
    vip_range: str = "1-10+"
    stages: List[Stage] = field(default_factory=lambda: [Stage(stage_id=1)])

    def to_dict(self) -> dict:
        return {
            self.name: {
                "Stages": [s.to_dict() for s in self.stages],
                "PossibleSegmentInfo": {"VIPRange": self.vip_range}
            }
        }

    @classmethod
    def from_dict(cls, name: str, data: dict):
        inner = data.get(name, {})
        stages = [Stage.from_dict(s) for s in inner.get("Stages", [])]
        vip = inner.get("PossibleSegmentInfo", {}).get("VIPRange", "1-10+")
        return cls(name=name, vip_range=vip, stages=stages)

@dataclass
class PossibleNodeEventData(Serializable):
    event_id: str
    min_level: int
    segment: str  # основной сегмент
    asset_bundle_path: str
    blocker_prefab_path: str
    roundel_prefab_path: str
    event_card_prefab_path: str
    node_completion_prefab_path: str
    content_key: str
    number_of_repeats: int
    entry_types: List[str] = field(default_factory=list)
    segments: Dict[str, Segment] = field(default_factory=dict)
    is_roundel_hidden: bool = False
    use_node_failed_notification: bool = False
    is_prize_pursuit: bool = False
    use_force_landscape_on_web: bool = False
    show_roundel_on_all_machines: bool = False
    # Скрытые поля (автоматически заполняются)
    starting_event_currency: float = 0.0
    is_currency_event: bool = False
    time_warning: str = field(default_factory=get_default_time_warning)

    def to_dict(self) -> dict:
        segments_dict = {}
        for seg in self.segments.values():
            segments_dict.update(seg.to_dict())
        return {
            "PossibleNodeEventData": {
                "EventID": self.event_id,
                "MinLevel": self.min_level,
                "Segment": self.segment,
                "AssetBundlePath": self.asset_bundle_path,
                "BlockerPrefabPath": self.blocker_prefab_path,
                "RoundelPrefabPath": self.roundel_prefab_path,
                "EventCardPrefabPath": self.event_card_prefab_path,
                "NodeCompletionPrefabPath": self.node_completion_prefab_path,
                "ContentKey": self.content_key,
                "NumberOfRepeats": self.number_of_repeats,
                "StartingEventCurrency": self.starting_event_currency,
                "IsCurrencyEvent": self.is_currency_event,
                "TimeWarning": self.time_warning,
                "EntryTypes": self.entry_types,
                "Segments": segments_dict,
                "IsRoundelHidden": self.is_roundel_hidden,
                "UseNodeFailedNotification": self.use_node_failed_notification,
                "IsPrizePursuit": self.is_prize_pursuit,
                "UseForceLandscapeOnWeb": self.use_force_landscape_on_web,
                "ShowRoundelOnAllMachines": self.show_roundel_on_all_machines,
            }
        }

    @classmethod
    def from_dict(cls, data: dict):
        inner = data.get("PossibleNodeEventData", {})
        segments_raw = inner.get("Segments", {})
        segments = {}
        for seg_name, seg_data in segments_raw.items():
            segments[seg_name] = Segment.from_dict(seg_name, {seg_name: seg_data})
        return cls(
            event_id=inner.get("EventID", "MyEvent"),
            min_level=inner.get("MinLevel", 1),
            segment=inner.get("Segment", "Default"),
            asset_bundle_path=inner.get("AssetBundlePath", "_events/MyEvent"),
            blocker_prefab_path=inner.get("BlockerPrefabPath", "Dialogs/MyEvent_Dialog"),
            roundel_prefab_path=inner.get("RoundelPrefabPath", "Roundels/MyEvent_Roundel"),
            event_card_prefab_path=inner.get("EventCardPrefabPath", ""),
            node_completion_prefab_path=inner.get("NodeCompletionPrefabPath", "Dialogs/MyEvent_Dialog"),
            content_key=inner.get("ContentKey", "MyEvent"),
            number_of_repeats=inner.get("NumberOfRepeats", -1),
            entry_types=inner.get("EntryTypes", []),
            segments=segments,
            is_roundel_hidden=inner.get("IsRoundelHidden", False),
            use_node_failed_notification=inner.get("UseNodeFailedNotification", False),
            is_prize_pursuit=inner.get("IsPrizePursuit", False),
            use_force_landscape_on_web=inner.get("UseForceLandscapeOnWeb", False),
            show_roundel_on_all_machines=inner.get("ShowRoundelOnAllMachines", False),
            starting_event_currency=inner.get("StartingEventCurrency", 0.0),
            is_currency_event=inner.get("IsCurrencyEvent", False),
            time_warning=inner.get("TimeWarning", get_default_time_warning()),
        )

def make_node_event(
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
    segments: Optional[Dict[str, Segment]] = None,
    is_roundel_hidden: bool = False,
    use_node_failed_notification: bool = False,
    is_prize_pursuit: bool = False,
    use_force_landscape_on_web: bool = False,
    show_roundel_on_all_machines: bool = False,
) -> PossibleNodeEventData:
    """Удобная функция для создания события с автоматическим заполнением скрытых полей."""
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