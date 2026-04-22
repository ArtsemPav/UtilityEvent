import json
from typing import Optional, Tuple
import jsonschema

def load_config_from_json(file_content: bytes) -> dict:
    """
    Загружает конфиг из байтового содержимого JSON-файла.
    Выполняет минимальную инициализацию обязательных полей.
    """
    # Пробуем utf-8, затем utf-8-sig (BOM), затем cp1251
    for encoding in ("utf-8", "utf-8-sig", "cp1251", "latin-1"):
        try:
            text = file_content.decode(encoding)
            break
        except (UnicodeDecodeError, LookupError):
            continue
    else:
        text = file_content.decode("latin-1")  # latin-1 никогда не падает
    data = json.loads(text)
    # Гарантируем наличие корневых ключей
    data.setdefault("Events", [])
    data.setdefault("IsFallbackConfig", False)
    return data

def save_config_to_json(cfg: dict) -> bytes:
    """Преобразует конфиг в красиво отформатированный JSON (байты)."""
    return json.dumps(cfg, ensure_ascii=False, indent=4).encode("utf-8")

def save_config_to_json_compact(cfg: dict) -> bytes:
    """Компактный JSON без отступов — быстрее для больших конфигов."""
    return json.dumps(cfg, ensure_ascii=False, separators=(',', ':')).encode("utf-8")

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