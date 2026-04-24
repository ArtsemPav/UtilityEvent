# LiveEvent JSON Builder — Документация

## Обзор приложения

**LiveEvent JSON Builder** — Streamlit-приложение для создания, редактирования и экспорта конфигураций LiveEvent и SinglePick в формате JSON. Предназначено для управления игровыми событиями с поддержкой сегментации игроков, узлов прогрессии, целей и наград.

### Запуск

```bash
streamlit run app.py
```

Или через `StartApp.bat`.

---

## Структура проекта

```
app.py                        # Точка входа
models/                       # Модели данных
  base.py                     # Базовые абстрактные классы
  event.py                    # Структура события (Event, Segment, Stage)
  nodes.py                    # Типы узлов (ProgressNode, EntriesNode, DummyNode)
  rewards.py                  # Типы наград
  goals.py                    # Типы целей
  minbet.py                   # Типы минимальных ставок
  singlepick.py               # Структура SinglePick конфига
services/                     # Бизнес-логика
  state_manager.py            # Управление состоянием приложения (AppState)
  json_io.py                  # Загрузка и сохранение JSON
  builders.py                 # Фабричные функции для создания объектов
  singlepick_validator.py     # Валидация SinglePick конфигов
ui/                           # Пользовательский интерфейс
  common.py                   # Общие UI-утилиты
  import_tab.py               # Пакетный импорт из CSV/Excel
  tabs/                       # Основные вкладки приложения
    editor_tab.py             # Редактор LiveEvent
    export_tab.py             # Экспорт LiveEvent
    singlepick_tab.py         # Редактор SinglePick
    singlepick_export_tab.py  # Экспорт SinglePick
    validation_tab.py         # Валидация по JSON Schema
  widgets/                    # Переиспользуемые виджеты
    event_tree.py             # Дерево событий
    node_editor.py            # Редактор узлов
    minbet_widget.py          # Редактор MinBet
    goal_widget.py            # Редактор целей
    reward_widget.py          # Редактор одной награды
    rewards_editor.py         # Редактор списка наград
    singlepick_reward_widget.py      # Редактор SinglePick награды
    singlepick_rewards_editor.py     # Редактор списка SinglePick наград
utils/                        # Утилиты
  constants.py                # Константы и дефолтные значения
  helpers.py                  # Вспомогательные функции
  validators.py               # Функции валидации данных
```

---

## app.py — Точка входа

Инициализирует Streamlit-приложение и создаёт 5 основных вкладок:

| Вкладка | Описание |
|---------|----------|
| ✏️ Редактор LiveEvent | Создание и редактирование событий |
| 💾 Экспорт LiveEvent | Скачивание и предпросмотр JSON |
| 🎰 Редактор SinglePick | Управление конфигами SinglePick |
| 📤 Экспорт SinglePick | Экспорт SinglePick конфигов |
| ⚙️ Настройки | Переключение расширенных параметров |

Использует `AppState.get_instance()` для получения синглтона состояния приложения.

---
## Модели данных (models/)

### models/base.py

Базовые абстрактные классы для всех объектов данных.

**Класс `Serializable` (ABC)**

Абстрактный базовый класс, от которого наследуются все модели.

| Метод | Описание |
|-------|----------|
| `to_dict() -> dict` | Сериализация объекта в словарь для JSON |
| `from_dict(data: dict)` | Десериализация объекта из словаря |

---

### models/event.py

Структуры данных для описания игрового события.

**Класс `Stage`**

Стадия события, содержащая список узлов.

| Поле | Тип | Описание |
|------|-----|----------|
| `stage_id` | `int` | Идентификатор стадии |
| `nodes` | `List[Node]` | Список узлов в стадии |

**Класс `Segment`**

Сегмент события — группа игроков с определёнными характеристиками.

| Поле | Тип | Описание |
|------|-----|----------|
| `name` | `str` | Имя сегмента |
| `segment_info_type` | `str` | Тип сегментации: `VIPRange`, `AverageWagerRange`, `SpinpadRange`, `LevelRange` |
| `segment_info_value` | `str` | Значение диапазона, например `"1-10+"` |
| `stages` | `List[Stage]` | Список стадий в сегменте |

**Класс `PossibleNodeEventData`**

Основная структура события.

| Поле | Тип | Описание |
|------|-----|----------|
| `event_id` | `str` | Уникальный идентификатор события |
| `min_level` | `int` | Минимальный уровень игрока |
| `segment` | `str` | Основной сегмент |
| `asset_bundle_path` | `str` | Путь к ассет-бандлу |
| `blocker_prefab_path` | `str` | Путь к префабу блокера |
| `roundel_prefab_path` | `str` | Путь к префабу раундела |
| `content_key` | `str` | Ключ контента |
| `number_of_repeats` | `int` | Количество повторений (-1 = бесконечно) |
| `entry_types` | `List[str]` | Типы входов |
| `segments` | `Dict[str, Segment]` | Словарь сегментов |
| `is_roundel_hidden` | `bool` | Скрыть раундел |
| `use_node_failed_notification` | `bool` | Уведомление о провале узла |
| `is_prize_pursuit` | `bool` | Режим Prize Pursuit |
| `use_force_landscape_on_web` | `bool` | Принудительный ландшафтный режим |
| `show_roundel_on_all_machines` | `bool` | Показывать раундел на всех машинах |
| `starting_event_currency` | `float` | Начальная валюта события |
| `is_currency_event` | `bool` | Является ли событие валютным |
| `time_warning` | `str` | Время предупреждения в формате ISO 8601 |

---

### models/nodes.py

Типы узлов прогрессии события.

**Класс `ProgressNode`**

Основной узел прогрессии — игрок выполняет цель и получает награду.

| Поле | Тип | Описание |
|------|-----|----------|
| `node_id` | `int` | Уникальный ID узла |
| `next_node_ids` | `List[int]` | IDs следующих узлов |
| `game_list` | `List[str]` | Список игр для этого узла |
| `min_bet` | `FixedMinBet \| VariableMinBet` | Минимальная ставка |
| `goal` | `Goal` | Цель узла |
| `rewards` | `List[Reward]` | Список наград |
| `is_last_node` | `bool` | Является ли узел последним |
| `mini_game` | `str` | Тип мини-игры (например, `FlatReward`) |
| `button_action_text` | `str` | Текст кнопки действия |
| `button_action_type` | `str` | Тип действия кнопки |
| `button_action_data` | `str` | Данные действия кнопки |
| `custom_texts` | `List[str]` | Пользовательские тексты |
| `possible_item_collect` | `str` | Возможный предмет для сбора |
| `hide_loading_screen` | `bool` | Скрыть экран загрузки |
| `prize_box_index` | `int` | Индекс коробки с призом |

**Класс `EntriesNode`**

Узел сбора входов.

| Поле | Тип | Описание |
|------|-----|----------|
| `node_id` | `int` | Уникальный ID узла |
| `game_list` | `List[str]` | Список игр |
| `min_bet` | `FixedMinBet \| VariableMinBet` | Минимальная ставка |
| `goal_types` | `List[str]` | Типы целей |
| `entry_types` | `List[str]` | Типы входов |
| `button_action_text/type/data` | `str` | Параметры кнопки |

**Класс `DummyNode`**

Фиктивный узел для ветвления и выбора.

| Поле | Тип | Описание |
|------|-----|----------|
| `node_id` | `int` | Уникальный ID узла |
| `next_node_ids` | `List[int]` | IDs следующих узлов |
| `default_node_id` | `int` | ID узла по умолчанию |
| `rewards` | `List[Reward]` | Награды |
| `is_choice_event` | `bool` | Является ли событием выбора |

**Функция `node_from_dict(data: dict) -> Node`**

Фабрика для создания узла нужного типа на основе данных словаря.

---

### models/rewards.py

Типы наград для узлов.

| Класс | Поля | Описание |
|-------|------|----------|
| `FixedReward` | `currency: str`, `amount: float` | Фиксированная награда в валюте |
| `RtpReward` | `currency: str`, `percentage: float`, `min: float`, `max: float` | Награда на основе RTP |
| `FreeplayUnlockReward` | `game_name: str`, `spins: int` | Разблокировка фриспинов |
| `CollectableSellPacksReward` | `pack_id: str`, `num_packs: int` | Награда пакетами для продажи |
| `CollectableMagicPacksReward` | `pack_id: str`, `num_packs: int` | Магические пакеты |

**Класс `Reward`**

Обёртка для любого типа награды.

| Поле | Тип | Описание |
|------|-----|----------|
| `data` | `RewardType` | Конкретный объект награды |

---

### models/goals.py

Типы целей для узлов.

| Класс | Поля | Описание |
|-------|------|----------|
| `FixedGoal` | `target: int` | Фиксированное целевое значение |
| `SpinpadGoal` | `multiplier: float`, `min: int`, `max: int` | Цель на основе спинпада |
| `ConsecutiveWinsGoal` | `number_of_streaks_target: int`, `multiplier: float`, `min: int`, `max: int` | Цель на серии побед |
| `TotalCoinsPerDayGoal` | `multiplier: float`, `min: int`, `max: int` | Общие монеты в день |
| `TotalCoinsPerDayWithSpinLimiterGoal` | `spin_limiter: int`, `multiplier: float`, `min: int`, `max: int` | Монеты в день с лимитом спинов |
| `FixedGoalWithSpinLimiterGoal` | `target: int`, `spin_limiter: int` | Фиксированная цель с лимитом спинов |

**Класс `Goal`**

Обёртка для цели узла.

| Поле | Тип | Описание |
|------|-----|----------|
| `type` | `List[str]` | Тип цели: `Spins`, `Coins`, `Wins` и др. |
| `params` | `GoalParams` | Конкретные параметры цели |

---

### models/minbet.py

Типы минимальных ставок.

| Класс | Поля | Описание |
|-------|------|----------|
| `FixedMinBet` | `amount: float` | Фиксированная ставка |
| `VariableMinBet` | `variable: float`, `min: float`, `max: float` | Переменная ставка с диапазоном |

---

### models/singlepick.py

Структуры данных для конфигурации SinglePick (пикеры и колесо).

**Типы наград SinglePick:**

| Класс | Описание |
|-------|----------|
| `FixedSPReward` | Фиксированная награда |
| `RtpSPReward` | Награда на основе RTP |
| `PurchaseSPReward` | Награда за покупку |
| `FreeplaySPReward` | Фриспины |
| `PacksSPReward` | Пакеты |

**Типы джекпотов:**

| Класс | Описание |
|-------|----------|
| `FixedJackpot` | Фиксированный джекпот |
| `CIJackpot` | CI-джекпот |

**Типы пиков:**

| Класс | Описание |
|-------|----------|
| `RewardPick` | Пик с наградой |
| `JackpotPick` | Пик с джекпотом |
| `RetryPick` | Пик повтора |

**Класс `Wedge`** — сектор колеса (содержит награды и вес).

**Класс `PickersConfig`**

| Поле | Тип | Описание |
|------|-----|----------|
| `picks` | `list` | Список пиков |
| `total_pick_on_board` | `int` | Всего пиков на доске |
| `pick_until_win` | `int` | Количество пиков до победы |

**Класс `WheelConfig`**

| Поле | Тип | Описание |
|------|-----|----------|
| `wedges` | `list` | Список секторов колеса |

**Класс `ConfigSet`** — набор конфигов (Pickers или Wheel).

**Класс `SinglePickConfig`**

| Поле | Тип | Описание |
|------|-----|----------|
| `config_sets` | `dict` | Словарь наборов конфигов |

---
## Сервисы (services/)

### services/state_manager.py

Управление состоянием приложения через синглтон `AppState`, хранящийся в `st.session_state`.

**Класс `AppState`**

#### Инициализация

| Метод | Описание |
|-------|----------|
| `get_instance() -> AppState` | Получить или создать экземпляр AppState |

#### Работа с конфигом

| Метод | Описание |
|-------|----------|
| `get_cfg() -> dict` | Получить текущий конфиг |
| `set_cfg(cfg: dict)` | Установить конфиг |
| `get_events_raw() -> list` | Получить список событий из конфига |
| `get_event_by_index(idx: int) -> dict` | Получить событие по индексу (с кэшированием) |
| `update_event(idx: int, event: dict)` | Обновить событие по индексу |
| `add_event(event: dict)` | Добавить новое событие |
| `delete_event(idx: int)` | Удалить событие по индексу |

#### Работа с сегментами

| Метод | Описание |
|-------|----------|
| `add_segment(event_idx, segment)` | Добавить сегмент в событие |
| `update_segment(event_idx, seg_name, segment)` | Обновить сегмент |
| `delete_segment(event_idx, seg_name)` | Удалить сегмент |
| `get_current_segment() -> Segment` | Получить текущий выбранный сегмент |

#### Работа с узлами

| Метод | Описание |
|-------|----------|
| `add_node_to_current_segment(node)` | Добавить узел в текущий сегмент |
| `update_node_in_current_segment(node_idx, node)` | Обновить узел |
| `delete_node_from_current_segment(node_idx)` | Удалить узел |

#### Дублирование

| Метод | Описание |
|-------|----------|
| `duplicate_event(idx: int)` | Создать копию события с суффиксом `_copy` |
| `duplicate_segment(event_idx, seg_name)` | Дублировать сегмент |
| `duplicate_node(event_idx, seg_name, stage_idx, node_idx)` | Дублировать узел |

#### Контекст редактирования

| Метод | Описание |
|-------|----------|
| `start_editing_event(idx)` | Начать редактирование события |
| `start_editing_segment(event_idx, seg_name)` | Начать редактирование сегмента |
| `start_editing_node(event_idx, seg_name, stage_idx, node_idx)` | Начать редактирование узла |
| `apply_editing()` | Применить изменения из контекста редактирования |
| `clear_editing()` | Отменить редактирование |
| `get_editing_context() -> dict` | Получить текущий контекст редактирования |

#### Staged-конфиг (для больших файлов)

| Метод | Описание |
|-------|----------|
| `set_staged_cfg(cfg: dict)` | Сохранить исходный большой конфиг |
| `load_staged_event(event_id: str)` | Загрузить одно событие из staged конфига |
| `apply_event_to_staged(event_id: str, event: dict)` | Применить изменения события обратно в staged |
| `get_staged_cfg_with_patch() -> dict` | Получить staged конфиг с патчем текущего события |

---

### services/json_io.py

Функции для работы с JSON-файлами.

| Функция | Параметры | Возвращает | Описание |
|---------|-----------|------------|----------|
| `load_config_from_json(file_content: bytes) -> dict` | Байты файла | Словарь конфига | Загружает конфиг из байтов, поддерживает кодировки utf-8, utf-8-sig, cp1251 |
| `save_config_to_json(cfg: dict) -> bytes` | Словарь конфига | Байты JSON | Сохраняет конфиг в красиво отформатированный JSON |
| `save_config_to_json_compact(cfg: dict) -> bytes` | Словарь конфига | Байты JSON | Сохраняет конфиг в компактный JSON без отступов |
| `validate_config(cfg: dict, schema: dict) -> Tuple[bool, str]` | Конфиг и схема | `(is_valid, error_message)` | Валидирует конфиг по JSON Schema |

---

### services/builders.py

Фабричные функции для удобного создания объектов моделей.

#### MinBet

| Функция | Описание |
|---------|----------|
| `build_fixed_minbet(amount: float) -> FixedMinBet` | Создать фиксированную ставку |
| `build_variable_minbet(variable, min, max) -> VariableMinBet` | Создать переменную ставку |

#### Goal

| Функция | Описание |
|---------|----------|
| `build_fixed_goal(target: int) -> Goal` | Создать фиксированную цель |
| `build_spinpad_goal(multiplier, min, max) -> Goal` | Создать цель на основе спинпада |

#### Reward

| Функция | Описание |
|---------|----------|
| `build_fixed_chips_reward(amount: float) -> Reward` | Создать фиксированную награду в чипах |
| `build_rtp_chips_reward(percentage, min, max) -> Reward` | Создать RTP-награду в чипах |

#### Node

| Функция | Описание |
|---------|----------|
| `build_progress_node(**kwargs) -> ProgressNode` | Создать узел прогрессии |
| `build_entries_node(**kwargs) -> EntriesNode` | Создать узел входов |
| `build_dummy_node(**kwargs) -> DummyNode` | Создать фиктивный узел |

#### Event

| Функция | Описание |
|---------|----------|
| `build_node_event(**kwargs) -> PossibleNodeEventData` | Создать структуру события |

---

### services/singlepick_validator.py

Валидация конфигов SinglePick.

| Функция | Описание |
|---------|----------|
| `validate_configset_name(name: str) -> bool` | Проверить корректность имени ConfigSet |
| `is_percentage_valid(value: float) -> bool` | Проверить, что значение кратно 0.01 |
| `validate_singlepick(config: SinglePickConfig) -> List[ValidationError]` | Полная валидация конфига SinglePick, возвращает список ошибок |

---

## UI компоненты (ui/)

### ui/common.py

Общие UI-утилиты для Streamlit.

| Функция | Описание |
|---------|----------|
| `inject_sticky_right_column()` | Делает правую колонку sticky при прокрутке страницы |
| `confirm_button(label, key, confirm_label)` | Кнопка с двухшаговым подтверждением |
| `styled_info(message: str)` | Стилизованное информационное сообщение |
| `styled_error(message: str)` | Стилизованное сообщение об ошибке |
| `format_key(*parts) -> str` | Генерация уникальных ключей для виджетов Streamlit |

---

### ui/import_tab.py

Пакетный импорт данных из CSV или Excel файлов.

| Функция | Описание |
|---------|----------|
| `_load_with_header_detection(file) -> DataFrame` | Загрузить файл с автоматическим определением строки заголовка |
| `auto_map_columns(df: DataFrame) -> dict` | Автоматически сопоставить колонки файла с полями модели по синонимам |
| `_run_import(df, mapping, app_state)` | Выполнить импорт данных из DataFrame в текущее событие |
| `render_import_tab(app_state)` | Отрендерить вкладку импорта |

**Поддерживаемые форматы:** CSV (с автоопределением кодировки), Excel (.xlsx, .xls).

---

## Вкладки (ui/tabs/)

### ui/tabs/editor_tab.py

Главный редактор LiveEvent. Реализует пошаговый процесс создания конфигурации.

**Функция `render_editor_tab(app_state: AppState)`**

Рендерит вкладку редактора. Включает:

1. **Загрузка** — загрузка JSON-файла, выбор события из staged конфига
2. **Шаг 1: Событие** — создание или редактирование события (`PossibleNodeEventData`)
3. **Шаг 2: Сегмент** — создание или редактирование сегмента (`Segment`)
4. **Шаг 3: Узел** — создание или редактирование узла (через `render_node_editor`)
5. **Дерево событий** — навигация по иерархии через `render_event_tree`

Поддерживает:
- Staged-конфиг для работы с большими файлами (много событий)
- Пакетный импорт из CSV/Excel
- Дублирование событий, сегментов и узлов

---

### ui/tabs/export_tab.py

Экспорт конфигурации LiveEvent в JSON.

**Функция `render_export_tab(app_state: AppState)`**

| Возможность | Описание |
|-------------|----------|
| Валидация | Проверка конфига перед экспортом |
| Скачивание | Кнопка загрузки JSON-файла |
| Копирование | Копирование JSON в буфер обмена через JavaScript |
| Предпросмотр | Просмотр JSON с фильтром по конкретному событию |

---

### ui/tabs/singlepick_tab.py

Редактор конфигурации SinglePick.

**Класс `SinglePickState`** (dataclass)

| Поле | Тип | Описание |
|------|-----|----------|
| `config` | `SinglePickConfig` | Текущий конфиг |
| `editing` | `Tuple[str, str, int]` | Что редактируется: (cs_name, item_type, item_idx) |
| `staged_cfg` | `dict` | Исходный большой конфиг |

**Внутренние функции:**

| Функция | Описание |
|---------|----------|
| `_render_toolbar(state)` | Панель загрузки файла и валидации |
| `_render_tree(state)` | Дерево ConfigSet-ов с пиками и секторами |
| `_render_editor(state)` | Редактор выбранного элемента |
| `_render_reward_pick_form(pick, key)` | Форма редактирования RewardPick |
| `_render_jackpot_pick_form(pick, key)` | Форма редактирования JackpotPick |
| `_render_retry_pick_form(pick, key)` | Форма редактирования RetryPick |
| `_render_wedge_form(wedge, key)` | Форма редактирования сектора колеса |

**Функция `render_singlepick_tab()`** — точка входа для рендера вкладки.

---

### ui/tabs/singlepick_export_tab.py

Экспорт конфигурации SinglePick в JSON.

**Функция `render_singlepick_export_tab()`**

| Возможность | Описание |
|-------------|----------|
| Валидация | Встроенная проверка через `validate_singlepick()` |
| Скачивание | Кнопка загрузки JSON-файла |
| Копирование | Копирование JSON в буфер обмена |
| Предпросмотр | Просмотр с фильтром по ConfigSet |

---

### ui/tabs/validation_tab.py

Валидация JSON-файлов по схеме.

**Функция `render_validation_tab()`**

Позволяет загрузить JSON-файл и JSON Schema, после чего выполняет валидацию через `validate_config()` и отображает результат.

---

## Виджеты (ui/widgets/)

### ui/widgets/event_tree.py

Дерево навигации по событиям, сегментам и узлам.

**Функция `render_event_tree(app_state: AppState)`**

Отображает иерархическое дерево: Событие → Сегмент → Стадия → Узел.

| Особенность | Описание |
|-------------|----------|
| Пагинация событий | Показывает до 20 событий (MAX_EVENTS_VISIBLE) |
| Пагинация узлов | Показывает до 10 узлов на сегмент (MAX_NODES_PER_SEGMENT) |
| Кнопки | Редактирование, дублирование, удаление для каждого элемента |
| Отложенное открытие | Поддержка открытия узла после `clear_editing` |

---

### ui/widgets/node_editor.py

Универсальный редактор узлов всех типов.

#### Система снимков (snapshots)

Используется для безопасного редактирования — позволяет откатить изменения.

| Функция | Описание |
|---------|----------|
| `set_node_snapshot(node, key)` | Сохранить снимок узла в session_state |
| `_get_snapshot(key) -> Node` | Получить сохранённый снимок |
| `_clear_widget_keys(key)` | Сбросить ключи виджетов для перерисовки |

#### Формы редактирования

| Функция | Описание |
|---------|----------|
| `render_progress_node_form(node, key, show_advanced) -> ProgressNode` | Форма для ProgressNode |
| `render_entries_node_form(node, key, show_advanced) -> EntriesNode` | Форма для EntriesNode |
| `render_dummy_node_form(node, key, show_advanced) -> DummyNode` | Форма для DummyNode |
| `render_node_editor(node, key, show_advanced) -> Node` | Универсальный рендерер — автоматически выбирает нужную форму |

Поддерживает расширенные параметры (`show_advanced`), управляемые через вкладку ⚙️ Настройки.

---

### ui/widgets/minbet_widget.py

Редактор минимальной ставки.

**Функция `render_minbet_widget(minbet, key) -> MinBet`**

Отображает выбор между `FixedMinBet` и `VariableMinBet` с соответствующими полями ввода. Возвращает обновлённый объект ставки.

---

### ui/widgets/goal_widget.py

Редактор цели узла.

**Функция `render_goal_widget(goal, key) -> Goal`**

Отображает выбор типа цели и динамически показывает поля в зависимости от выбранного типа. Поддерживает все типы целей: `FixedGoal`, `SpinpadGoal`, `ConsecutiveWinsGoal`, `TotalCoinsPerDayGoal`, `TotalCoinsPerDayWithSpinLimiterGoal`, `FixedGoalWithSpinLimiterGoal`.

---

### ui/widgets/reward_widget.py

Редактор одной награды.

**Функция `render_reward_widget(reward, key) -> Reward`**

Отображает форму для одной награды с динамическими полями в зависимости от типа. Поддерживает все типы наград: `FixedReward`, `RtpReward`, `FreeplayUnlockReward`, `CollectableSellPacksReward`, `CollectableMagicPacksReward`.

---

### ui/widgets/rewards_editor.py

Редактор списка наград.

| Функция | Описание |
|---------|----------|
| `get_default_reward() -> Reward` | Возвращает стандартную награду (2 500 000 чипов) |
| `render_rewards_editor(rewards, key) -> List[Reward]` | Полный редактор списка наград с добавлением, удалением и редактированием |

---

### ui/widgets/singlepick_reward_widget.py

Редактор награды SinglePick.

**Функция `render_sp_reward_widget(reward, key) -> SPReward`**

Форма для SinglePick-награды. Поддерживает типы: `Chips` (FixedSPReward), `VariableChips` (RtpSPReward), `FreePlays` (FreeplaySPReward), `Packs` (PacksSPReward), `PurchaseReward` (PurchaseSPReward). Автоматически определяет тип из существующей награды.

---

### ui/widgets/singlepick_rewards_editor.py

Редактор списка наград SinglePick.

| Функция | Описание |
|---------|----------|
| `get_default_sp_reward() -> SPReward` | Возвращает стандартную SinglePick-награду |
| `render_sp_rewards_editor(rewards, key) -> List[SPReward]` | Полный редактор списка SinglePick-наград |

---

## Утилиты (utils/)

### utils/constants.py

Константы и дефолтные значения приложения.

| Группа | Примеры |
|--------|---------|
| Дефолтные значения событий | `DEFAULT_EVENT_ID`, `DEFAULT_MIN_LEVEL` |
| Дефолтные значения узлов | `DEFAULT_NODE_ID`, `DEFAULT_GAME_LIST` |
| Типы наград | `REWARD_TYPES`, `CURRENCY_TYPES` |
| Типы целей | `GOAL_TYPES` |
| Диапазоны значений | `MIN_BET_MIN_VALUE`, `MAX_NODE_ID` |
| Имена файлов | `DEFAULT_EXPORT_FILENAME` |

---

### utils/helpers.py

Вспомогательные функции для обработки данных.

| Функция | Описание |
|---------|----------|
| `parse_comma_separated_list(text: str) -> List[str]` | Разбор строки с запятыми в список |
| `join_list_to_comma_string(lst: List[str]) -> str` | Объединение списка в строку через запятую |
| `process_multiline_text(text: str) -> List[str]` | Разбор многострочного текста в список |
| `format_number(value: float) -> str` | Форматирование числа для отображения |

---

### utils/validators.py

Функции валидации данных перед сохранением.

| Функция | Описание |
|---------|----------|
| `validate_event_id(event_id: str) -> Tuple[bool, str]` | Проверка корректности EventID |
| `validate_node_id(node_id: int) -> Tuple[bool, str]` | Проверка корректности NodeID |
| `validate_game_list(game_list: List[str]) -> Tuple[bool, str]` | Проверка списка игр |
| `validate_min_bet(min_bet) -> Tuple[bool, str]` | Проверка минимальной ставки |
| `validate_goal(goal) -> Tuple[bool, str]` | Проверка цели узла |
| `validate_rewards(rewards) -> Tuple[bool, str]` | Проверка списка наград |
| `validate_segment_name(name: str) -> Tuple[bool, str]` | Проверка имени сегмента |
| `validate_vip_range(value: str) -> Tuple[bool, str]` | Проверка формата VIP-диапазона |

Все функции возвращают кортеж `(is_valid: bool, error_message: str)`.

---

## Поток данных

```
Загрузка JSON
    └─> load_config_from_json()
    └─> AppState.set_cfg()

Редактирование
    └─> UI виджеты
    └─> AppState (кэширование событий)
    └─> AppState.update_event()

Экспорт
    └─> AppState.get_cfg()
    └─> save_config_to_json()
    └─> JSON файл / буфер обмена

Валидация
    └─> cfg + schema
    └─> validate_config()
    └─> результат
```

---

## Ключевые особенности

**Staged-конфиг** — при работе с большими файлами (много событий) приложение загружает только одно событие в рабочую память, а остальные хранит в staged конфиге. При экспорте изменения патчатся обратно.

**Кэширование событий** — события кэшируются в `AppState` для оптимизации производительности при частых обращениях.

**Система снимков** — перед редактированием узла сохраняется его снимок, что позволяет безопасно отменить изменения.

**Пакетный импорт** — поддержка загрузки данных из CSV и Excel с автоматическим сопоставлением колонок по синонимам.

**Дублирование** — события, сегменты и узлы можно дублировать с автоматической генерацией уникальных имён (суффикс `_copy`).

**Расширенные параметры** — редкие поля скрыты по умолчанию и включаются через вкладку ⚙️ Настройки.

**Sticky UI** — правая колонка с редактором остаётся видимой при прокрутке длинного дерева событий.
