from abc import ABC, abstractmethod

class Serializable(ABC):
    """Базовый класс для всех объектов, которые умеют сериализоваться в словарь и обратно."""

    @abstractmethod
    def to_dict(self) -> dict:
        """Преобразует объект в словарь (для последующей JSON-сериализации)."""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict):
        """Создаёт объект из словаря."""
        pass