import streamlit as st
from typing import Optional, List, Dict, Any, Union
from models.event import PossibleNodeEventData, Segment, Stage
from models.nodes import Node, ProgressNode, EntriesNode, DummyNode, node_from_dict

class AppState:
    """
    Централизованное управление состоянием Streamlit-приложения.
    Все данные хранятся в st.session_state["app"].
    """

    # ---------- Инициализация ----------
    @staticmethod
    def init() -> None:
        """Инициализирует начальное состояние, если оно ещё не создано."""
        if "app" not in st.session_state:
            st.session_state.app = {
                "cfg": {"Events": [], "IsFallbackConfig": False},
                "current_event_idx": -1,
                "current_segment_name": "",
                "editing_context": None,   # см. методы start_editing_*
                "temp_data": {},           # для временных данных форм
            }

    @classmethod
    def _get_state(cls) -> dict:
        """Возвращает словарь состояния (ссылка на st.session_state.app)."""
        cls.init()
        return st.session_state.app

    # ---------- Работа с конфигом ----------
    @classmethod
    def get_cfg(cls) -> dict:
        """Возвращает полный конфиг (словарь)."""
        return cls._get_state()["cfg"]

    @classmethod
    def set_cfg(cls, cfg: dict) -> None:
        """Устанавливает новый конфиг."""
        cls._get_state()["cfg"] = cfg

    @classmethod
    def get_events_raw(cls) -> List[dict]:
        """Возвращает список событий в виде сырых словарей."""
        return cls.get_cfg().get("Events", [])

    @classmethod
    def get_event_by_index(cls, idx: int) -> Optional[PossibleNodeEventData]:
        """Возвращает событие по индексу как объект PossibleNodeEventData."""
        events = cls.get_events_raw()
        if 0 <= idx < len(events):
            return PossibleNodeEventData.from_dict(events[idx])
        return None

    @classmethod
    def update_event(cls, idx: int, event: PossibleNodeEventData) -> None:
        """Обновляет событие по индексу."""
        cfg = cls.get_cfg()
        if 0 <= idx < len(cfg["Events"]):
            cfg["Events"][idx] = event.to_dict()
            cls.set_cfg(cfg)

    @classmethod
    def add_event(cls, event: PossibleNodeEventData) -> None:
        """Добавляет новое событие и делает его текущим."""
        cfg = cls.get_cfg()
        cfg["Events"].append(event.to_dict())
        cls.set_cfg(cfg)
        cls._get_state()["current_event_idx"] = len(cfg["Events"]) - 1
        cls._get_state()["current_segment_name"] = ""

    @classmethod
    def delete_event(cls, idx: int) -> None:
        """Удаляет событие по индексу."""
        cfg = cls.get_cfg()
        if 0 <= idx < len(cfg["Events"]):
            del cfg["Events"][idx]
            state = cls._get_state()
            if state["current_event_idx"] == idx:
                state["current_event_idx"] = -1
                state["current_segment_name"] = ""
            elif state["current_event_idx"] > idx:
                state["current_event_idx"] -= 1
            cls.set_cfg(cfg)

    # ---------- Текущее выбранное событие / сегмент ----------
    @classmethod
    def get_current_event_idx(cls) -> int:
        return cls._get_state()["current_event_idx"]

    @classmethod
    def set_current_event_idx(cls, idx: int) -> None:
        cls._get_state()["current_event_idx"] = idx
        cls._get_state()["current_segment_name"] = ""

    @classmethod
    def get_current_event(cls) -> Optional[PossibleNodeEventData]:
        idx = cls.get_current_event_idx()
        return cls.get_event_by_index(idx)

    @classmethod
    def get_current_segment_name(cls) -> str:
        return cls._get_state()["current_segment_name"]

    @classmethod
    def set_current_segment_name(cls, name: str) -> None:
        cls._get_state()["current_segment_name"] = name

    @classmethod
    def get_current_segment(cls) -> Optional[Segment]:
        event = cls.get_current_event()
        if event is None:
            return None
        seg_name = cls.get_current_segment_name()
        return event.segments.get(seg_name)

    # ---------- Работа с сегментами ----------
    @classmethod
    def add_segment(cls, event_idx: int, segment: Segment) -> None:
        """Добавляет сегмент в указанное событие и делает его текущим."""
        event = cls.get_event_by_index(event_idx)
        if event is None:
            return
        event.segments[segment.name] = segment
        cls.update_event(event_idx, event)
        if event_idx == cls.get_current_event_idx():
            cls.set_current_segment_name(segment.name)

    @classmethod
    def update_segment(cls, event_idx: int, old_name: str, new_segment: Segment) -> None:
        """Обновляет или переименовывает сегмент."""
        event = cls.get_event_by_index(event_idx)
        if event is None or old_name not in event.segments:
            return
        # Удаляем старый и добавляем новый (если имя изменилось)
        del event.segments[old_name]
        event.segments[new_segment.name] = new_segment
        cls.update_event(event_idx, event)
        if event_idx == cls.get_current_event_idx() and cls.get_current_segment_name() == old_name:
            cls.set_current_segment_name(new_segment.name)

    @classmethod
    def delete_segment(cls, event_idx: int, segment_name: str) -> None:
        event = cls.get_event_by_index(event_idx)
        if event and segment_name in event.segments:
            del event.segments[segment_name]
            cls.update_event(event_idx, event)
            if event_idx == cls.get_current_event_idx() and cls.get_current_segment_name() == segment_name:
                cls.set_current_segment_name("")

    # ---------- Работа с узлами ----------
    @classmethod
    def add_node_to_current_segment(cls, node: Node) -> None:
        """Добавляет узел в первую стадию текущего сегмента."""
        event = cls.get_current_event()
        seg_name = cls.get_current_segment_name()
        if event is None or seg_name not in event.segments:
            return
        segment = event.segments[seg_name]
        if not segment.stages:
            segment.stages = [Stage(stage_id=1)]
        segment.stages[0].nodes.append(node)
        cls.update_event(cls.get_current_event_idx(), event)

    @classmethod
    def update_node_in_current_segment(cls, stage_idx: int, node_idx: int, node: Node) -> None:
        event = cls.get_current_event()
        seg_name = cls.get_current_segment_name()
        if event is None or seg_name not in event.segments:
            return
        segment = event.segments[seg_name]
        if 0 <= stage_idx < len(segment.stages) and 0 <= node_idx < len(segment.stages[stage_idx].nodes):
            segment.stages[stage_idx].nodes[node_idx] = node
            cls.update_event(cls.get_current_event_idx(), event)

    @classmethod
    def delete_node_from_current_segment(cls, stage_idx: int, node_idx: int) -> None:
        event = cls.get_current_event()
        seg_name = cls.get_current_segment_name()
        if event is None or seg_name not in event.segments:
            return
        segment = event.segments[seg_name]
        if 0 <= stage_idx < len(segment.stages) and 0 <= node_idx < len(segment.stages[stage_idx].nodes):
            del segment.stages[stage_idx].nodes[node_idx]
            cls.update_event(cls.get_current_event_idx(), event)

    # ---------- Контекст редактирования ----------
    @classmethod
    def start_editing_event(cls, idx: int) -> None:
        cls._get_state()["editing_context"] = {"type": "event", "index": idx}

    @classmethod
    def start_editing_segment(cls, event_idx: int, seg_name: str) -> None:
        cls._get_state()["editing_context"] = {
            "type": "segment",
            "event_idx": event_idx,
            "name": seg_name
        }

    @classmethod
    def start_editing_node(cls, event_idx: int, seg_name: str, stage_idx: int, node_idx: int) -> None:
        cls._get_state()["editing_context"] = {
            "type": "node",
            "event_idx": event_idx,
            "seg_name": seg_name,
            "stage_idx": stage_idx,
            "node_idx": node_idx
        }

    @classmethod
    def clear_editing(cls) -> None:
        cls._get_state()["editing_context"] = None

    @classmethod
    def get_editing_context(cls) -> Optional[Dict[str, Any]]:
        return cls._get_state()["editing_context"]

    @classmethod
    def is_editing(cls, edit_type: str = None) -> bool:
        ctx = cls.get_editing_context()
        if ctx is None:
            return False
        if edit_type:
            return ctx["type"] == edit_type
        return True

    @classmethod
    def get_editing_event(cls) -> Optional[PossibleNodeEventData]:
        ctx = cls.get_editing_context()
        if ctx and ctx["type"] == "event":
            return cls.get_event_by_index(ctx["index"])
        return None

    @classmethod
    def get_editing_segment(cls) -> Optional[tuple]:  # (event_idx, Segment)
        ctx = cls.get_editing_context()
        if ctx and ctx["type"] == "segment":
            event = cls.get_event_by_index(ctx["event_idx"])
            if event:
                seg = event.segments.get(ctx["name"])
                if seg:
                    return (ctx["event_idx"], seg)
        return None

    @classmethod
    def get_editing_node(cls) -> Optional[tuple]:  # (event_idx, seg_name, stage_idx, node_idx, Node)
        ctx = cls.get_editing_context()
        if ctx and ctx["type"] == "node":
            event = cls.get_event_by_index(ctx["event_idx"])
            if event:
                seg = event.segments.get(ctx["seg_name"])
                if seg and ctx["stage_idx"] < len(seg.stages):
                    nodes = seg.stages[ctx["stage_idx"]].nodes
                    if ctx["node_idx"] < len(nodes):
                        return (ctx["event_idx"], ctx["seg_name"], ctx["stage_idx"], ctx["node_idx"], nodes[ctx["node_idx"]])
        return None

    # ---------- Временные данные форм ----------
    @classmethod
    def set_temp(cls, key: str, value: Any) -> None:
        cls._get_state()["temp_data"][key] = value

    @classmethod
    def get_temp(cls, key: str, default: Any = None) -> Any:
        return cls._get_state()["temp_data"].get(key, default)

    @classmethod
    def clear_temp(cls) -> None:
        cls._get_state()["temp_data"] = {}