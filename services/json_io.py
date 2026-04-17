import json
from typing import Optional, Tuple
import jsonschema

def load_config_from_json(file_content: bytes) -> dict:
    """
    Загружает конфиг из байтового содержимого JSON-файла.
    Выполняет минимальную инициализацию обязательных полей.
    """
    data = json.loads(file_content.decode("utf-8"))
    # Гарантируем наличие корневых ключей
    data.setdefault("Events", [])
    data.setdefault("IsFallbackConfig", False)
    return data

def save_config_to_json(cfg: dict) -> bytes:
    """Преобразует конфиг в красиво отформатированный JSON (байты)."""
    return json.dumps(cfg, ensure_ascii=False, indent=4).encode("utf-8")

def validate_config(cfg: dict, schema: Optional[dict]) -> Tuple[bool, str]:
    """
    Проверяет конфиг на соответствие JSON Schema.
    Возвращает (True, "") при успехе или (False, error_message) при ошибке.
    """
    if schema is None:
        return False, "Схема не загружена"
    try:
        jsonschema.validate(instance=cfg, schema=schema)
        return True, ""
    except jsonschema.ValidationError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Ошибка валидации: {e}"