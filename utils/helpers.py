from typing import List

def parse_comma_separated_list(text: str) -> List[str]:
    """Разбирает строку с элементами через запятую в список, удаляя пробелы и пустые элементы."""
    if not text:
        return []
    return [item.strip() for item in text.split(",") if item.strip()]

def join_list_to_comma_string(items: List[str]) -> str:
    """Преобразует список строк в строку с разделителем ', '."""
    return ", ".join(items)

def process_multiline_text(text: str) -> List[str]:
    """Разбирает многострочный текст в список непустых строк."""
    if not text:
        return []
    return [line.strip() for line in text.split("\n") if line.strip()]

def format_number(value: float, precision: int = 2) -> str:
    """Форматирует число с заданной точностью."""
    return f"{value:.{precision}f}"