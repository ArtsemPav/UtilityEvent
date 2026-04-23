import streamlit as st
import copy
from typing import Optional, List, Dict, Any, Union
from models.event import PossibleNodeEventData, Segment, Stage
from models.nodes import Node, ProgressNode, EntriesNode, DummyNode, node_from_dict

class AppState:
    """
    Централизованное управление состоянием приложения.
    Экземпляр хранится в st.session_state['app_state'].
    """

    def __init__(self):
        self.cfg = {"Events": [], "IsFallbackConfig": False}
        self.current_event_idx = -1
        self.current_segment_name = ""
        self.editing_context = None   # будет хранить копии редактируемых объектов
        self.temp_data = {}
        self._event_cache: Dict[int, PossibleNodeEventData] = {}  # кэш десериализованных событий

    @classmethod
    def get_instance(cls):
        """Возвращает экземпляр AppState из session_state, создаёт при необходимости."""
        if "app_state" not in st.session_state:
            st.session_state.app_state = cls()
        return st.session_state.app_state

    # --- Работа с конфигом ---
    def get_cfg(self) -> dict:
        return self.cfg

    def set_cfg(self, cfg: dict) -> None:
        self.cfg = cfg
        self._event_cache.clear()  # сбрасываем кэш при загрузке нового конфига

    def get_events_raw(self) -> List[dict]:
        return self.cfg.get("Events", [])

    def get_event_by_index(self, idx: int) -> Optional[PossibleNodeEventData]:
        events = self.get_events_raw()
        if 0 <= idx < len(events):
            if idx not in self._event_cache:
                self._event_cache[idx] = PossibleNodeEventData.from_dict(events[idx])
            return self._event_cache[idx]
        return None

    def _invalidate_event_cache(self, idx: int) -> None:
        """Инвалидирует кэш для конкретного события."""
        self._event_cache.pop(idx, None)

    def update_event(self, idx: int, event: PossibleNodeEventData) -> None:
        if 0 <= idx < len(self.cfg["Events"]):
            self.cfg["Events"][idx] = event.to_dict()
            self._invalidate_event_cache(idx)  # сбрасываем кэш после обновления

    def add_event(self, event: PossibleNodeEventData) -> None:
        self.cfg["Events"].append(event.to_dict())
        self.current_event_idx = len(self.cfg["Events"]) - 1
        self.current_segment_name = ""
        # кэш для нового индекса не нужен — он будет создан при первом обращении

    def delete_event(self, idx: int) -> None:
        if 0 <= idx < len(self.cfg["Events"]):
            del self.cfg["Events"][idx]
            # Перестраиваем кэш: сдвигаем индексы после удалённого
            new_cache: Dict[int, PossibleNodeEventData] = {}
            for k, v in self._event_cache.items():
                if k < idx:
                    new_cache[k] = v
                elif k > idx:
                    new_cache[k - 1] = v
                # k == idx — удаляем из кэша
            self._event_cache = new_cache

            if self.current_event_idx == idx:
                self.current_event_idx = -1
                self.current_segment_name = ""
            elif self.current_event_idx > idx:
                self.current_event_idx -= 1
            if self.editing_context and self.editing_context.get("event_idx") == idx:
                self.clear_editing()

    # --- Текущее выбранное событие / сегмент ---
    def get_current_event_idx(self) -> int:
        return self.current_event_idx

    def set_current_event_idx(self, idx: int) -> None:
        self.current_event_idx = idx
        self.current_segment_name = ""

    def get_current_event(self) -> Optional[PossibleNodeEventData]:
        return self.get_event_by_index(self.current_event_idx)

    def get_current_segment_name(self) -> str:
        return self.current_segment_name

    def set_current_segment_name(self, name: str) -> None:
        self.current_segment_name = name

    def get_current_segment(self) -> Optional[Segment]:
        event = self.get_current_event()
        if event is None:
            return None
        return event.segments.get(self.current_segment_name)

    # --- Работа с сегментами ---
    def add_segment(self, event_idx: int, segment: Segment) -> None:
        event = self.get_event_by_index(event_idx)
        if event is None:
            return
        event.segments[segment.name] = segment
        self.update_event(event_idx, event)
        if event_idx == self.current_event_idx:
            self.current_segment_name = segment.name

    def update_segment(self, event_idx: int, old_name: str, new_segment: Segment) -> None:
        event = self.get_event_by_index(event_idx)
        if event is None or old_name not in event.segments:
            return
        del event.segments[old_name]
        event.segments[new_segment.name] = new_segment
        self.update_event(event_idx, event)
        if event_idx == self.current_event_idx and self.current_segment_name == old_name:
            self.current_segment_name = new_segment.name

    def delete_segment(self, event_idx: int, segment_name: str) -> None:
        event = self.get_event_by_index(event_idx)
        if event and segment_name in event.segments:
            del event.segments[segment_name]
            self.update_event(event_idx, event)
            if event_idx == self.current_event_idx and self.current_segment_name == segment_name:
                self.current_segment_name = ""

    # --- Работа с узлами (вспомогательные методы) ---
    def _ensure_stage_exists(self, segment: Segment, stage_idx: int = 0) -> None:
        if not segment.stages:
            segment.stages = [Stage(stage_id=1)]
        if stage_idx >= len(segment.stages):
            for i in range(len(segment.stages), stage_idx + 1):
                segment.stages.append(Stage(stage_id=i+1))

    def add_node_to_current_segment(self, node: Node) -> None:
        event = self.get_current_event()
        seg_name = self.current_segment_name
        if event is None or seg_name not in event.segments:
            return
        segment = event.segments[seg_name]
        self._ensure_stage_exists(segment)
        segment.stages[0].nodes.append(node)
        self.update_event(self.current_event_idx, event)

    def update_node_in_current_segment(self, stage_idx: int, node_idx: int, node: Node) -> None:
        event = self.get_current_event()
        seg_name = self.current_segment_name
        if event is None or seg_name not in event.segments:
            return
        segment = event.segments[seg_name]
        if 0 <= stage_idx < len(segment.stages) and 0 <= node_idx < len(segment.stages[stage_idx].nodes):
            segment.stages[stage_idx].nodes[node_idx] = node
            self.update_event(self.current_event_idx, event)

    def delete_node_from_current_segment(self, stage_idx: int, node_idx: int) -> None:
        event = self.get_current_event()
        seg_name = self.current_segment_name
        if event is None or seg_name not in event.segments:
            return
        segment = event.segments[seg_name]
        if 0 <= stage_idx < len(segment.stages) and 0 <= node_idx < len(segment.stages[stage_idx].nodes):
            del segment.stages[stage_idx].nodes[node_idx]
            self.update_event(self.current_event_idx, event)

    def delete_node(self, event_idx: int, seg_name: str, stage_idx: int, node_idx: int) -> None:
        event = self.get_event_by_index(event_idx)
        if event is None or seg_name not in event.segments:
            return
        segment = event.segments[seg_name]
        if 0 <= stage_idx < len(segment.stages) and 0 <= node_idx < len(segment.stages[stage_idx].nodes):
            del segment.stages[stage_idx].nodes[node_idx]
            self.update_event(event_idx, event)

    # --- Дублирование ---
    def duplicate_event(self, idx: int) -> None:
        """Создаёт копию события с суффиксом _copy (или _copy2, _copy3, ...) к EventID."""
        events = self.get_events_raw()
        if not (0 <= idx < len(events)):
            return
        new_raw = copy.deepcopy(events[idx])
        base_id = new_raw["PossibleNodeEventData"]["EventID"]
        # Генерируем уникальный EventID
        existing_ids = {e["PossibleNodeEventData"]["EventID"] for e in events}
        candidate = f"{base_id}_copy"
        counter = 2
        while candidate in existing_ids:
            candidate = f"{base_id}_copy{counter}"
            counter += 1
        new_raw["PossibleNodeEventData"]["EventID"] = candidate
        new_event = PossibleNodeEventData.from_dict(new_raw)
        self.cfg["Events"].insert(idx + 1, new_event.to_dict())
        # Сдвигаем кэш для индексов > idx
        new_cache: Dict[int, PossibleNodeEventData] = {}
        for k, v in self._event_cache.items():
            if k <= idx:
                new_cache[k] = v
            else:
                new_cache[k + 1] = v
        self._event_cache = new_cache
        if self.current_event_idx > idx:
            self.current_event_idx += 1

    def duplicate_segment(self, event_idx: int, seg_name: str) -> None:
        """Создаёт копию сегмента с суффиксом _copy (или _copy2, ...) к имени."""
        event = self.get_event_by_index(event_idx)
        if event is None or seg_name not in event.segments:
            return
        existing_names = set(event.segments.keys())
        candidate = f"{seg_name}_copy"
        counter = 2
        while candidate in existing_names:
            candidate = f"{seg_name}_copy{counter}"
            counter += 1
        new_seg = copy.deepcopy(event.segments[seg_name])
        new_seg.name = candidate
        event.segments[candidate] = new_seg
        self.update_event(event_idx, event)

    def duplicate_node(self, event_idx: int, seg_name: str, stage_idx: int, node_idx: int) -> None:
        """Вставляет копию ноды сразу после оригинала."""
        event = self.get_event_by_index(event_idx)
        if event is None or seg_name not in event.segments:
            return
        segment = event.segments[seg_name]
        if not (0 <= stage_idx < len(segment.stages)):
            return
        nodes = segment.stages[stage_idx].nodes
        if not (0 <= node_idx < len(nodes)):
            return
        new_node = node_from_dict(copy.deepcopy(nodes[node_idx].to_dict()))
        nodes.insert(node_idx + 1, new_node)
        self.update_event(event_idx, event)

    # --- Контекст редактирования (храним копии объектов) ---
    def start_editing_event(self, idx: int) -> None:
        event = self.get_event_by_index(idx)
        if event:
            raw = self.cfg["Events"][idx]
            event_copy = PossibleNodeEventData.from_dict(copy.deepcopy(raw))
            self.editing_context = {"type": "event", "index": idx, "copy": event_copy}
            self.current_event_idx = idx

    def start_editing_segment(self, event_idx: int, seg_name: str) -> None:
        events = self.get_events_raw()
        if 0 <= event_idx < len(events):
            seg_raw = events[event_idx].get("PossibleNodeEventData", {}).get("Segments", {}).get(seg_name)
            if seg_raw is not None:
                seg_copy = Segment.from_dict(seg_name, {seg_name: copy.deepcopy(seg_raw)})
                self.editing_context = {
                    "type": "segment",
                    "event_idx": event_idx,
                    "name": seg_name,
                    "copy": seg_copy
                }
                # Устанавливаем текущее событие и сегмент
                self.current_event_idx = event_idx
                self.current_segment_name = seg_name

    def start_editing_node(self, event_idx: int, seg_name: str, stage_idx: int, node_idx: int) -> None:
        events = self.get_events_raw()
        if 0 <= event_idx < len(events):
            try:
                node_raw = (events[event_idx]["PossibleNodeEventData"]["Segments"]
                            [seg_name]["Stages"][stage_idx]["Nodes"][node_idx])
                node_copy = node_from_dict(copy.deepcopy(node_raw))
                self.editing_context = {
                    "type": "node",
                    "event_idx": event_idx,
                    "seg_name": seg_name,
                    "stage_idx": stage_idx,
                    "node_idx": node_idx,
                    "copy": node_copy
                }
                # Устанавливаем текущее событие и сегмент чтобы ШАГ 3 стал видимым
                self.current_event_idx = event_idx
                self.current_segment_name = seg_name
            except (KeyError, IndexError):
                pass

    def clear_editing(self) -> None:
        self.editing_context = None
        # Сбрасываем идентификаторы загруженных нод чтобы форма перезагрузилась
        for key in list(st.session_state.keys()):
            if key.startswith("_node_loaded_id_") or key.startswith("_node_snapshot_"):
                del st.session_state[key]

    def get_editing_context(self) -> Optional[Dict[str, Any]]:
        return self.editing_context

    def is_editing(self, edit_type: str = None) -> bool:
        ctx = self.editing_context
        if ctx is None:
            return False
        if edit_type:
            return ctx["type"] == edit_type
        return True

    def get_editing_event_copy(self) -> Optional[PossibleNodeEventData]:
        ctx = self.editing_context
        if ctx and ctx["type"] == "event":
            return ctx.get("copy")
        return None

    def get_editing_segment_copy(self) -> Optional[tuple]:
        ctx = self.editing_context
        if ctx and ctx["type"] == "segment":
            return (ctx["event_idx"], ctx["name"], ctx.get("copy"))
        return None

    def get_editing_node_copy(self) -> Optional[tuple]:
        ctx = self.editing_context
        if ctx and ctx["type"] == "node":
            return (ctx["event_idx"], ctx["seg_name"], ctx["stage_idx"], ctx["node_idx"], ctx.get("copy"))
        return None

    def apply_editing(self) -> None:
        """Применяет изменения из редактируемой копии к реальным данным."""
        ctx = self.editing_context
        if not ctx:
            return
        if ctx["type"] == "event":
            self.update_event(ctx["index"], ctx["copy"])
        elif ctx["type"] == "segment":
            event = self.get_event_by_index(ctx["event_idx"])
            if event:
                old_name = ctx["name"]
                new_seg = ctx["copy"]
                if old_name != new_seg.name:
                    del event.segments[old_name]
                event.segments[new_seg.name] = new_seg
                self.update_event(ctx["event_idx"], event)
        elif ctx["type"] == "node":
            event = self.get_event_by_index(ctx["event_idx"])
            if event and ctx["seg_name"] in event.segments:
                segment = event.segments[ctx["seg_name"]]
                if 0 <= ctx["stage_idx"] < len(segment.stages) and 0 <= ctx["node_idx"] < len(segment.stages[ctx["stage_idx"]].nodes):
                    segment.stages[ctx["stage_idx"]].nodes[ctx["node_idx"]] = ctx["copy"]
                    self.update_event(ctx["event_idx"], event)
        self.clear_editing()

    # --- Временные данные форм ---
    def set_temp(self, key: str, value: Any) -> None:
        self.temp_data[key] = value

    def get_temp(self, key: str, default: Any = None) -> Any:
        return self.temp_data.get(key, default)

    def clear_temp(self) -> None:
        self.temp_data = {}