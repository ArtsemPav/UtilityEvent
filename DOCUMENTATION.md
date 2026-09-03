# LiveEvent JSON Builder — Документация

> Документ описывает фактическое состояние кода. Разделы
> [«Неиспользуемый код»](#неиспользуемый-код) и [«Известные ограничения»](#известные-ограничения)
> перечисляют места, где код расходится с ожиданиями или со спецификацией.

## Обзор приложения

**LiveEvent JSON Builder** — Streamlit-приложение для создания, редактирования и экспорта конфигураций
**LiveEvent** и **SinglePick** в формате JSON. Две схемы независимы: у них разные корневые ключи,
разные модели данных и разное состояние в `st.session_state`.

### Запуск

```bash
streamlit run app.py
```

Или через [StartApp.bat](StartApp.bat) (`python3 -m streamlit run app.py`).

### Зависимости

Перечислены в [requirements.txt](requirements.txt):

```bash
python -m pip install -r requirements.txt
```

| Пакет | Где используется |
|---|---|
| `streamlit` | всё приложение, включая `streamlit.components.v1` для кнопок «копировать в буфер» |
| `jsonschema` | `services/json_io.py` — валидация по JSON Schema |
| `pandas` | `ui/import_tab.py` — чтение CSV/Excel |
| `openpyxl` | требуется `pandas.read_excel` для `.xlsx` (транзитивно) |

`.devcontainer/devcontainer.json` доустанавливает `streamlit` и, при наличии, `requirements.txt`;
приложение поднимается на порту 8501.

---

## Структура проекта

```
app.py                              # Точка входа, 5 вкладок
models/                             # Модели данных (dataclass + to_dict/from_dict)
  base.py                           # Serializable (ABC)
  event.py                          # Stage, Segment, PossibleNodeEventData, make_node_event
  nodes.py                          # ProgressNode, EntriesNode, DummyNode, node_from_dict
  rewards.py                        # 5 типов наград + обёртка Reward
  goals.py                          # 6 типов параметров цели + обёртка Goal
  minbet.py                         # FixedMinBet, VariableMinBet
  singlepick.py                     # Полная иерархия SinglePick
services/
  state_manager.py                  # AppState — состояние вкладок LiveEvent
  json_io.py                        # Загрузка/сохранение JSON, валидация по схеме
  singlepick_validator.py           # Логическая валидация SinglePick
  builders.py                       # Фабрики (НЕ используются, частичная заглушка)
ui/
  common.py                         # inject_sticky_right_column + неиспользуемые утилиты
  import_tab.py                     # Пакетный импорт из CSV/Excel
  tabs/
    editor_tab.py                   # Редактор LiveEvent
    export_tab.py                   # Экспорт LiveEvent
    singlepick_tab.py               # Редактор SinglePick (+ своё состояние SinglePickState)
    singlepick_export_tab.py        # Экспорт SinglePick
    validation_tab.py               # Валидация по схеме (НЕ подключена в app.py)
  widgets/
    event_tree.py                   # Дерево событий LiveEvent
    node_editor.py                  # Формы всех типов узлов + система снимков
    minbet_widget.py                # Редактор MinBet
    goal_widget.py                  # Редактор цели
    reward_widget.py                # Редактор одной награды LiveEvent
    rewards_editor.py               # Редактор списка наград LiveEvent
    singlepick_reward_widget.py     # Редактор одной награды SinglePick
    singlepick_rewards_editor.py    # Редактор списка наград SinglePick
utils/
  constants.py                      # Константы и дефолтные значения
  helpers.py                        # Парсинг/форматирование строк
  validators.py                     # Функции валидации (возвращают List[str])
requirements.txt                    # Зависимости приложения
schema/
  LiveEventData_V10.json            # JSON Schema конфига LiveEvent (для вкладки валидации)
.kiro/specs/singlepick-tab/         # Спецификация вкладки SinglePick (requirements/design/tasks)
```

---

## Формат JSON

### LiveEvent

```json
{
  "Events": [
    {
      "PossibleNodeEventData": {
        "EventID": "MyEvent",
        "AssetBundlePath": "_events/MyEvent",
        "BlockerPrefabPath": "Dialogs/MyEvent_Dialog",
        "RoundelPrefabPath": "Roundels/MyEvent_Roundel",
        "EventCardPrefabPath": "",
        "NodeCompletionPrefabPath": "Dialogs/MyEvent_Dialog",
        "ContentKey": "MyEvent",
        "MinLevel": 1,
        "NumberOfRepeats": -1,
        "IsCurrencyEvent": false,
        "StartingEventCurrency": 0.0,
        "TimeWarning": "2026-10-01T00:00:00Z",
        "ManualClaim": false,
        "ShowPopupOnEmptyReward": false,
        "EntryTypes": [],
        "Segment": "Default",
        "Segments": {
          "VIP1_10": {
            "Stages": [
              {
                "StageID": 1,
                "Nodes": [
                  {
                    "ProgressNode": {
                      "NodeID": 1,
                      "NextNodeID": [2],
                      "GameList": ["AllGames"],
                      "MinBet": { "FixedMinBet": { "MinBet": 250000.0 } },
                      "Goal": { "Type": ["Spins"], "FixedGoal": { "Target": 20 } },
                      "Rewards": [{ "FixedReward": { "Currency": "Chips", "Amount": 2500000.0 } }],
                      "IsLastNode": false,
                      "ResegmentFlag": false,
                      "MiniGame": "FlatReward",
                      "ContributionLevel": "Node",
                      "ButtonActionType": "",
                      "ButtonActionData": "",
                      "ButtonActionText": "PLAY NOW!",
                      "CustomTexts": [],
                      "PossibleItemCollect": "Default"
                    }
                  }
                ]
              }
            ],
            "PossibleSegmentInfo": { "VIPRange": "1-10+" }
          }
        }
      }
    }
  ],
  "IsFallbackConfig": false
}
```

### SinglePick

```json
{
  "ConfigSets": {
    "MyConfigSet": {
      "Pickers": {
        "Picks": [
          { "RewardPick": { "Reward": [{ "FixedReward": { "Currency": "Chips", "Amount": 1000000 } }], "Weight": 1, "PossibleMax": 1 } },
          { "JackpotPick": { "CIJackpot": { "Min": 0, "Max": 0, "CIMin": 0, "CIMax": 0 }, "Weight": 0, "PossibleMax": 0 } },
          { "RetryPick": { "Reward": [], "Weight": 0, "PossibleMax": 0 } }
        ],
        "TotalPickOnBoard": 1,
        "PickUntilWin": 0
      }
    },
    "MyWheel": {
      "Wheel": {
        "Wedges": [
          { "RewardPick": { "Reward": [{ "FixedReward": { "Currency": "Chips", "Amount": 1000000 } }], "Weight": 1 } }
        ]
      }
    }
  }
}
```

---

## app.py — Точка входа

Настраивает страницу (`layout="wide"`), получает `AppState.get_instance()` и, если событий больше нуля,
а текущий индекс равен `-1`, выставляет `current_event_idx = 0`. Затем создаёт 5 вкладок:

| Вкладка | Функция рендера |
|---|---|
| ✏️ Редактор LiveEvent | `render_editor_tab()` |
| 💾 Экспорт LiveEvent | `render_export_tab()` |
| 🎰 Редактор SinglePick | `render_singlepick_tab()` |
| 📤 Экспорт SinglePick | `render_singlepick_export_tab()` |
| ⚙️ Настройки | инлайн: `st.toggle("🔧 Расширенные параметры", key="show_advanced")` |

Все функции рендера вызываются **без аргументов** — состояние они получают сами
(`AppState.get_instance()` / `get_singlepick_state()`).

Флаг `st.session_state["show_advanced"]` читают формы события и узлов, скрывая под ним редкие поля.
Под ним же собраны все необязательные по схеме флаги, которые попадают в JSON только когда включены:
`IsRoundelHidden`, `ShowRoundelOnAllMachines`, `IsPrizePursuit`, `UseNodeFailedNotification`,
`UseForceLandscapeOnWeb` (уровень события) и `HideLoadingScreenForReward` (уровень узла).
Когда тумблер выключен, значения не теряются — они берутся из редактируемого объекта или из дефолтов.

---

## Модели данных (models/)

### models/base.py

**Класс `Serializable` (ABC)** — базовый класс всех моделей.

| Метод | Описание |
|---|---|
| `to_dict() -> dict` | Сериализация в словарь для JSON |
| `from_dict(data: dict)` | Классметод десериализации |

> `Segment.from_dict(name, data)` принимает два аргумента и не соответствует сигнатуре базового класса.

---

### models/event.py

**`get_default_time_warning() -> str`** — `datetime.utcnow() + 30 дней` в формате `"%Y-%m-%dT%H:%M:%SZ"`.

**Класс `Stage`** → `{"StageID": ..., "Nodes": [...]}`

| Поле | Тип | По умолчанию |
|---|---|---|
| `stage_id` | `int` | — |
| `nodes` | `List[Node]` | `[]` |

**Класс `Segment`** → `{<name>: {"Stages": [...], "PossibleSegmentInfo": {<type>: <value>}}}`

| Поле | Тип | По умолчанию |
|---|---|---|
| `name` | `str` | — |
| `segment_info_type` | `str` | `"VIPRange"` |
| `segment_info_value` | `str` | `"1-10+"` |
| `stages` | `List[Stage]` | `[Stage(stage_id=1)]` |

- Допустимые типы: `VIPRange`, `AverageWagerRange`, `SpinpadRange`, `LevelRange` или `""` (нет инфо).
- `PossibleSegmentInfo` попадает в JSON **только если** и тип, и значение непусты.
- Свойство `vip_range` — обратная совместимость: возвращает значение, если тип `VIPRange`, иначе `""`.
- `from_dict(name, data)` ожидает `data` вида `{name: inner}`.

**Класс `PossibleNodeEventData`** → `{"PossibleNodeEventData": {...}}`

| Поле | Ключ JSON | Тип | Дефолт при `from_dict` |
|---|---|---|---|
| `event_id` | `EventID` | `str` | `"MyEvent"` |
| `min_level` | `MinLevel` | `int` | `1` |
| `segment` | `Segment` | `str` | `"Default"` |
| `asset_bundle_path` | `AssetBundlePath` | `str` | `"_events/MyEvent"` |
| `blocker_prefab_path` | `BlockerPrefabPath` | `str` | `"Dialogs/MyEvent_Dialog"` |
| `roundel_prefab_path` | `RoundelPrefabPath` | `str` | `"Roundels/MyEvent_Roundel"` |
| `event_card_prefab_path` | `EventCardPrefabPath` | `str` | `""` |
| `node_completion_prefab_path` | `NodeCompletionPrefabPath` | `str` | `"Dialogs/MyEvent_Dialog"` |
| `content_key` | `ContentKey` | `str` | `"MyEvent"` |
| `number_of_repeats` | `NumberOfRepeats` | `int` | `-1` (бесконечно) |
| `entry_types` | `EntryTypes` | `List[str]` | `[]` |
| `segments` | `Segments` | `Dict[str, Segment]` | `{}` |
| `is_roundel_hidden` | `IsRoundelHidden` | `bool` | `False` — **пишется только если `True`** |
| `use_node_failed_notification` | `UseNodeFailedNotification` | `bool` | `False` — **пишется только если `True`** |
| `is_prize_pursuit` | `IsPrizePursuit` | `bool` | `False` — **пишется только если `True`** |
| `use_force_landscape_on_web` | `UseForceLandscapeOnWeb` | `bool` | `False` — **пишется только если `True`** |
| `show_roundel_on_all_machines` | `ShowRoundelOnAllMachines` | `bool` | `False` — **пишется только если `True`** |
| `manual_claim` | `ManualClaim` | `bool` | `False` — обязательное по схеме V10 |
| `show_popup_on_empty_reward` | `ShowPopupOnEmptyReward` | `bool` | `False` — обязательное по схеме V10 |
| `starting_event_currency` | `StartingEventCurrency` | `float` | `0.0` |
| `is_currency_event` | `IsCurrencyEvent` | `bool` | `False` |
| `time_warning` | `TimeWarning` | `str` | `get_default_time_warning()` |

Три последних поля — «скрытые»: в UI доступны только при включённом тумблере «Расширенные параметры».

**`make_node_event(...) -> PossibleNodeEventData`** — фабрика, которую использует редактор.
Принимает все поля события; `segments` по умолчанию `None` → `{}`, `time_warning=None` → дефолт.

---

### models/nodes.py

`Node = Union[ProgressNode, EntriesNode, DummyNode]`.
**`node_from_dict(data)`** выбирает класс по корневому ключу и бросает `ValueError` для неизвестного типа.

**Класс `ProgressNode`** → `{"ProgressNode": {...}}`

| Поле | Ключ JSON | Тип | Дефолт |
|---|---|---|---|
| `node_id` | `NodeID` | `int` | — |
| `next_node_ids` | `NextNodeID` | `List[int]` | — |
| `game_list` | `GameList` | `List[str]` | — |
| `min_bet` | `MinBet` | `FixedMinBet \| VariableMinBet` | — |
| `goal` | `Goal` | `Goal` | — |
| `rewards` | `Rewards` | `List[Reward]` | — |
| `is_last_node` | `IsLastNode` | `bool` | `False` |
| `resegment_flag` | `ResegmentFlag` | `bool` | `False` |
| `mini_game` | `MiniGame` | `str` | `"FlatReward"` |
| `contribution_level` | `ContributionLevel` | `str` | `"Node"` |
| `button_action_type` | `ButtonActionType` | `str` | `""` |
| `button_action_data` | `ButtonActionData` | `str` | `""` |
| `button_action_text` | `ButtonActionText` | `str` | `"PLAY NOW!"` |
| `custom_texts` | `CustomTexts` | `List[str]` | `[]` |
| `possible_item_collect` | `PossibleItemCollect` | `str` | `""` — **пишется только если непусто** |
| `hide_loading_screen` | `HideLoadingScreenForReward` | `bool` | `False` — **пишется только если `True`** |
| `prize_box_index` | `PrizeBoxIndex` | `int` | `-1` — **пишется только если `> 0`** |

**Класс `EntriesNode`** → `{"EntriesNode": {...}}`

| Поле | Ключ JSON | Тип | Дефолт |
|---|---|---|---|
| `node_id` | `NodeID` | `int` | — |
| `game_list` | `GameList` | `List[str]` | — |
| `min_bet` | `MinBet` | `FixedMinBet \| VariableMinBet` | — |
| `goal_types` | `GoalType` | `List[str]` | — |
| `entry_types` | `EntryTypes` | `List[str]` | — |
| `resegment_flag` | `ResegmentFlag` | `bool` | `False` |
| `button_action_type/data/text` | `ButtonAction*` | `str` | `""` / `""` / `"PLAY NOW!"` |
| `custom_texts` | `CustomTexts` | `List[str]` | `[]` |
| `possible_item_collect` | `PossibleItemCollect` | `str` | `"Default"` — пишется всегда |
| `prize_box_index` | `PrizeBoxIndex` | `int` | `-1` — **пишется только если `> 0`** |

У `EntriesNode` нет `Goal`, `Rewards`, `NextNodeID` и `IsLastNode`.

**Класс `DummyNode`** → `{"DummyNode": {...}}`

| Поле | Ключ JSON | Тип | Дефолт |
|---|---|---|---|
| `node_id` | `NodeID` | `int` | — |
| `next_node_ids` | `NextNodeID` | `List[int]` | `[11, 21, 31]` при `from_dict` |
| `default_node_id` | `DefaultNodeID` | `int` | — |
| `rewards` | `Rewards` | `List[Reward]` | — |
| `is_last_node` | `IsLastNode` | `bool` | `False` |
| `resegment_flag` | `ResegmentFlag` | `bool` | `False` |
| `mini_game` | `MiniGame` | `str` | `"FlatReward"` |
| `contribution_level` | `ContributionLevel` | `str` | `"Node"` |
| `button_action_type/data/text` | `ButtonAction*` | `str` | `""` |
| `custom_texts` | `CustomTexts` | `List[str]` | `[]` |
| `is_choice_event` | `IsChoiceEvent` | `bool` | `True` |
| `hide_loading_screen` | `HideLoadingScreenForReward` | `bool` | `False` — **пишется только если `True`** |
| `prize_box_index` | `PrizeBoxIndex` | `int` | `-1` — **пишется только если `> 0`** |

---

### models/rewards.py

`RewardType = Union[FixedReward, RtpReward, FreeplayUnlockReward, CollectableSellPacksReward, CollectableMagicPacksReward]`

| Класс | Поля | JSON |
|---|---|---|
| `FixedReward` | `currency: str`, `amount: float` | `{"FixedReward": {"Currency", "Amount"}}` |
| `RtpReward` | `currency: str`, `percentage: float`, `min: float`, `max: float` | `{"RtpReward": {"Currency", "Percentage", "Min", "Max"}}` |
| `FreeplayUnlockReward` | `game_name: str`, `spins: int` | `{"FreeplayUnlockReward": {"GameName", "Spins"}}` |
| `CollectableSellPacksReward` | `pack_id: str`, `num_packs: int` | `{"CollectableSellPacksReward": {"PackId", "NumPacks"}}` |
| `CollectableMagicPacksReward` | `pack_id: str`, `num_packs: int` | `{"CollectableMagicPacksReward": {"PackId", "NumPacks"}}` |

**Класс `Reward`** — обёртка с единственным полем `data: RewardType`.
`to_dict()` делегирует вложенному объекту (лишнего уровня не добавляет),
`from_dict()` определяет тип по ключу; при неизвестном ключе — фолбэк `FixedReward(Chips, 0.0)`.

---

### models/goals.py

| Класс | Поля | Корневой ключ JSON |
|---|---|---|
| `FixedGoal` | `target: int` | `FixedGoal` → `{"Target"}` |
| `SpinpadGoal` | `multiplier: float`, `min: int`, `max: int` | `SpinpadGoal` → `{"Multiplier", "Min", "Max"}` |
| `ConsecutiveWinsGoal` | `wins_in_streak_target: int`, `multiplier: float`, `min: int`, `max: int` | `ConsecutiveWinsGoal` → `{"WinsInStreakTarget", "NumberOfStreaksSpinPadGoal": {"Multiplier", "Min", "Max"}}` |
| `TotalCoinsPerDayGoal` | `multiplier: float`, `min: int`, `max: int` | `TotalCoinsPerDay` → `{"Multiplier", "Min", "Max"}` |
| `TotalCoinsPerDayWithSpinLimiterGoal` | `spin_limiter: int`, `multiplier: float`, `min: int`, `max: int` | `TotalCoinsPerDayWithSpinLimiter` |
| `FixedGoalWithSpinLimiterGoal` | `target: int`, `spin_limiter: int` | `FixedGoalWithSpinLimiter` |

**Класс `Goal`**

| Поле | Тип | Описание |
|---|---|---|
| `type` | `List[str]` | Значение ключа `Type`, например `["Spins"]` |
| `params` | `GoalParams` | Один из шести классов выше |

`to_dict()` возвращает **плоский** словарь: `{"Type": [...], "<ИмяПараметров>": {...}}`.
`from_dict()` берёт `Type`, а тип параметров определяет по остальным ключам; фолбэк — `FixedGoal(target=20)`.

---

### models/minbet.py

| Класс | Поля | JSON |
|---|---|---|
| `FixedMinBet` | `amount: float` | `{"FixedMinBet": {"MinBet": ...}}` |
| `VariableMinBet` | `variable: float`, `min: float`, `max: float` | `{"MinBetVariable": {"Variable", "Min", "Max"}}` |

Выбор класса при разборе: если в словаре есть ключ `FixedMinBet` — `FixedMinBet`, иначе `VariableMinBet`.

---

### models/singlepick.py

**Награды** — `SPReward = Union[FixedSPReward, RtpSPReward, PurchaseSPReward, FreeplaySPReward, PacksSPReward]`

| Класс | Поля | JSON |
|---|---|---|
| `FixedSPReward` | `currency: str`, `amount: int` | `{"FixedReward": {"Currency", "Amount"}}` |
| `RtpSPReward` | `currency: str`, `percentage: float`, `min: int`, `max: int` | `{"RtpReward": {...}}` |
| `PurchaseSPReward` | `shop_type: str`, `shop_name: str` | `{"PurchaseReward": {"ShopType", "ShopName"}}` |
| `FreeplaySPReward` | `game_name: str`, `spins: int` | `{"FreeplayUnlockReward": {...}}` |
| `PacksSPReward` | `pack_id: str`, `num_packs: int` | `{"CollectableSellPacksReward": {...}}` |

`_sp_reward_from_dict(data)` — диспетчер по ключу, фолбэк `FixedSPReward(Chips, 0)`.

**Джекпоты**

| Класс | Поля | JSON |
|---|---|---|
| `FixedJackpot` | `min`, `max` | `{"FixedJackpot": {"Min", "Max"}}` |
| `CIJackpot` | `min`, `max`, `ci_min`, `ci_max` | `{"CIJackpot": {"Min", "Max", "CIMin", "CIMax"}}` |

`_jackpot_from_dict(data)`: ключ `CIJackpot` → `CIJackpot`, иначе `FixedJackpot`.

**Пики** — `Pick = Union[RewardPick, JackpotPick, RetryPick]`, диспетчер `_pick_from_dict`.

| Класс | Поля | Особенности сериализации |
|---|---|---|
| `RewardPick` | `reward: list`, `weight: int`, `possible_max: int` | `{"RewardPick": {"Reward": [...], "Weight", "PossibleMax"}}` |
| `JackpotPick` | `jackpot`, `weight`, `possible_max` | Словарь джекпота **встраивается** внутрь `JackpotPick` рядом с `Weight`/`PossibleMax` |
| `RetryPick` | `reward: list`, `weight: int`, `possible_max: int` | Как `RewardPick`; список наград может быть пустым |

**Класс `Wedge`** (`reward: list`, `weight: int`) — сектор колеса.
Сериализуется под ключом **`RewardPick`**, но **без** `PossibleMax`.

**Контейнеры**

| Класс | Поля | JSON |
|---|---|---|
| `PickersConfig` | `picks: list`, `total_pick_on_board: int`, `pick_until_win: int` | `{"Picks", "TotalPickOnBoard", "PickUntilWin"}` |
| `WheelConfig` | `wedges: list` | `{"Wedges": [...]}` |
| `ConfigSet` | `content: PickersConfig \| WheelConfig` | `{"Pickers": {...}}` либо `{"Wheel": {...}}` |
| `SinglePickConfig` | `config_sets: dict` | `{"ConfigSets": {name: {...}}}` |

`SinglePickConfig.from_dict()` бросает `ValueError("Missing 'ConfigSets' key")`, если корневого ключа нет —
на этом редактор отличает SinglePick-файл от постороннего.

---

## Сервисы (services/)

### services/state_manager.py

**Класс `AppState`** — состояние вкладок LiveEvent. Экземпляр лежит в `st.session_state["app_state"]`.

Поля: `cfg`, `current_event_idx` (`-1` = не выбрано), `current_segment_name`, `editing_context`,
`temp_data`, `_event_cache`, `staged_cfg`, `staged_event_idx`.

#### Инициализация и конфиг

| Метод | Описание |
|---|---|
| `get_instance()` | Классметод: достаёт или создаёт экземпляр в `session_state` |
| `get_cfg() -> dict` | Текущий рабочий конфиг |
| `set_cfg(cfg)` | Заменяет конфиг и **сбрасывает кэш событий** |
| `get_events_raw() -> List[dict]` | `cfg["Events"]` как сырые словари |
| `get_event_by_index(idx) -> PossibleNodeEventData \| None` | Десериализует событие с кэшированием в `_event_cache` |
| `update_event(idx, event: PossibleNodeEventData)` | Пишет `event.to_dict()` в конфиг и инвалидирует кэш |
| `add_event(event)` | Добавляет в конец, делает событие текущим, сбрасывает имя сегмента |
| `delete_event(idx)` | Удаляет, пересчитывает индексы кэша и `current_event_idx`, при необходимости `clear_editing()` |

#### Текущий выбор

`get_current_event_idx()`, `set_current_event_idx(idx)` (сбрасывает имя сегмента),
`get_current_event()`, `get_current_segment_name()`, `set_current_segment_name(name)`,
`get_current_segment() -> Segment | None`.

#### Сегменты

| Метод | Описание |
|---|---|
| `add_segment(event_idx, segment)` | Добавляет и делает текущим (если событие текущее) |
| `update_segment(event_idx, old_name, new_segment)` | Удаляет старый ключ, добавляет новый, синхронизирует `current_segment_name` |
| `delete_segment(event_idx, segment_name)` | Удаляет сегмент |

#### Узлы

| Метод | Описание |
|---|---|
| `_ensure_stage_exists(segment, stage_idx=0)` | Создаёт отсутствующие стадии (`stage_id` = индекс + 1) |
| `add_node_to_current_segment(node)` | Всегда добавляет в **стадию 0** |
| `update_node_in_current_segment(stage_idx, node_idx, node)` | Замена узла в текущем сегменте |
| `delete_node_from_current_segment(stage_idx, node_idx)` | Удаление из текущего сегмента |
| `delete_node(event_idx, seg_name, stage_idx, node_idx)` | Удаление по полным координатам (используется деревом) |

#### Дублирование

| Метод | Описание |
|---|---|
| `duplicate_event(idx)` | Вставляет копию после оригинала, `EventID` → `_copy` / `_copy2` / … |
| `duplicate_segment(event_idx, seg_name)` | Копия с именем `_copy` / `_copy2` / … |
| `duplicate_node(event_idx, seg_name, stage_idx, node_idx)` | Копия сразу после оригинала (через `to_dict` → `node_from_dict`) |

#### Контекст редактирования

Редактирование идёт по глубокой копии; `editing_context` — словарь с ключом `type`
(`"event"` / `"segment"` / `"node"`), координатами и объектом `copy`.

| Метод | Описание |
|---|---|
| `start_editing_event(idx)` | Кладёт копию события, делает его текущим |
| `start_editing_segment(event_idx, seg_name)` | Кладёт копию сегмента, выставляет текущее событие и сегмент |
| `start_editing_node(event_idx, seg_name, stage_idx, node_idx)` | Кладёт копию узла; при `KeyError`/`IndexError` тихо ничего не делает |
| `clear_editing()` | Сбрасывает контекст и удаляет из `session_state` все ключи `_node_loaded_id_*` и `_node_snapshot_*` |
| `get_editing_context() -> dict \| None` | Текущий контекст |
| `is_editing(edit_type=None) -> bool` | Идёт ли редактирование (опционально — заданного типа) |
| `get_editing_event_copy()` | `PossibleNodeEventData` или `None` |
| `get_editing_segment_copy()` | `(event_idx, name, Segment)` или `None` |
| `get_editing_node_copy()` | `(event_idx, seg_name, stage_idx, node_idx, Node)` или `None` |
| `apply_editing()` | Переносит копию в реальные данные (для сегмента корректно обрабатывает переименование) и вызывает `clear_editing()` |

#### Staged-конфиг

| Метод | Описание |
|---|---|
| `set_staged_cfg(cfg)` | Сохраняет исходный большой конфиг, `staged_event_idx = -1` |
| `get_staged_cfg() -> dict \| None` | Исходный конфиг |
| `get_staged_event_ids() -> List[str]` | Список `EventID` (при отсутствии — `[i]`) |
| `load_staged_event(event_idx: int)` | Кладёт в рабочий конфиг **одно** событие, `current_event_idx = 0`, `clear_editing()` |
| `apply_event_to_staged() -> bool` | Возвращает отредактированное событие в исходный конфиг |
| `get_staged_cfg_with_patch() -> dict \| None` | Копия исходного конфига с наложенным текущим событием |
| `clear_staged()` | Сбрасывает staged-режим |
| `add_new_event_to_staged(event)` | Добавляет новое событие в staged (создав его при необходимости) и открывает в редакторе |

Индекс события передаётся числом, а не `event_id`; вкладка получает индекс через `event_ids.index(...)`.

#### Временные данные

`set_temp(key, value)`, `get_temp(key, default=None)`, `clear_temp()` — заготовка, в UI не используется.

---

### services/json_io.py

| Функция | Описание |
|---|---|
| `load_config_from_json(file_content: bytes) -> dict` | Декодирует, перебирая `utf-8`, `utf-8-sig`, `cp1251`, `latin-1`; парсит JSON; гарантирует ключи `Events` и `IsFallbackConfig` через `setdefault` |
| `save_config_to_json(cfg) -> bytes` | `json.dumps(..., ensure_ascii=False, indent=4)` в UTF-8 |
| `save_config_to_json_compact(cfg) -> bytes` | Компактный дамп без отступов (в UI не вызывается) |
| `validate_config(cfg, schema: Optional[dict]) -> Tuple[bool, str]` | JSON Schema через `jsonschema`. **Если `schema is None`, возвращает `(False, "Схема не загружена")`** |

`load_config_from_json` добавляет ключи LiveEvent даже к SinglePick-файлу — для SinglePick смысл имеет
только парсинг, а тип определяется дальше через `SinglePickConfig.from_dict`.

---

### services/singlepick_validator.py

| Объект | Описание |
|---|---|
| `ValidationError` | dataclass: `configset_name`, `field`, `message` |
| `validate_configset_name(name, existing_names: list[str]) -> str \| None` | Сообщение об ошибке (пустое имя / дубликат) либо `None` |
| `is_percentage_valid(percentage: float) -> bool` | Допускает **до 3 знаков** после запятой (реальные конфиги содержат значения вроде `0.028`) |
| `validate_singlepick(config) -> list[ValidationError]` | Полная логическая проверка |

Проверки в `validate_singlepick`:

- имя ConfigSet непусто;
- `PickersConfig.picks` непуст;
- `WheelConfig.wedges` непуст;
- в каждом `JackpotPick`: `min <= max`;
- в каждом `RtpSPReward` (внутри `RewardPick`, `RetryPick`, `Wedge`): корректный `Percentage`.

---

### services/builders.py

Набор фабрик (`build_fixed_minbet`, `build_variable_minbet`, `build_fixed_goal`, `build_spinpad_goal`,
`build_fixed_chips_reward`, `build_rtp_chips_reward`, `build_progress_node`, `build_node_event`).

> **Модуль нигде не импортируется** и реализован не полностью: вместо части функций стоят комментарии
> «*аналогичные функции для остальных типов*». Приложение создаёт события через `make_node_event`
> из `models/event.py`, а узлы — напрямую конструкторами dataclass'ов.
> `build_node_event` к тому же не принимает `starting_event_currency`, `is_currency_event`, `time_warning`.

---

## UI (ui/)

### ui/common.py

| Функция | Статус | Описание |
|---|---|---|
| `inject_sticky_right_column()` | используется | Инжектит CSS: **последняя** колонка `stHorizontalBlock` становится `position: sticky` с прокруткой |
| `confirm_button(label, key, message="Вы уверены?")` | не используется | Двухшаговое подтверждение; вкладки реализуют подтверждение вручную через `session_state` |
| `styled_info(text)` / `styled_error(text)` | не используется | HTML-плашки |
| `format_key(prefix, index)` | не используется | `f"{prefix}_{index}"` |

---

### ui/import_tab.py — пакетный импорт CSV/Excel

| Функция | Описание |
|---|---|
| `FIELD_SYNONYMS` | Словарь: поле модели → список синонимов заголовка (24 поля, включая русские варианты) |
| `_normalize(s)` | `strip().lower()`, `-` и пробел → `_` |
| `_vip_range_from_segment_name(seg_name)` | `Vip2_5` → `"2-5"`; при несовпадении — `""` |
| `auto_map_columns(df_columns: list[str]) -> dict[str, str \| None]` | Сопоставляет поля модели с реальными колонками по синонимам |
| `_find_header_row(df_raw) -> int` | Первая строка, где ≥ 3 ячейки совпали с синонимами; иначе `0` |
| `_load_with_header_detection(uploaded_file) -> DataFrame` | Читает CSV (автоподбор кодировки, `sep=None`) или Excel, ставит найденную строку заголовком, **дедуплицирует** повторяющиеся заголовки (`ChipsAmount` → `ChipsAmount_2`), выбрасывает полностью пустые строки |
| `_read_file(uploaded_file)` | Устаревший вариант чтения без определения заголовка — **не используется** |
| `render_import_tab()` | Обёртка: заголовок + `render_batch_import_panel(key="import_tab")`. **В `app.py` не вызывается** |
| `render_batch_import_panel(key="editor_tab")` | Основная панель: справка, загрузка файла, предпросмотр, ручная правка маппинга в 2 колонки, кнопка «Начать импорт» |
| `_get(row, field, final_mapping, default="")` | Безопасное чтение ячейки как строки |
| `_run_import(df, final)` | Двухпроходный импорт |

**Логика `_run_import`:**

1. Целевое событие — текущее; если не выбрано, берётся первое, а при отсутствии событий выводится ошибка.
2. **Проход 1** — сегменты: уникальные значения `segment_name`; отсутствующие создаются,
   `VIPRange` подставляется из имени, если распознан.
3. **Проход 2** — узлы: создаются только `ProgressNode` и всегда добавляются в стадию 0.
   - `NodeID` обязателен и должен быть > 0; дубликат внутри сегмента пропускается с предупреждением.
   - Списки (`NextNodeID`, `GameList`) разделяются `;`, если он есть в строке, иначе `,`.
   - MinBet: при заполненном `minbet_variable` → `VariableMinBet`, иначе `FixedMinBet(250000)`.
   - Goal: при заполненном `goal_multiplier` → `SpinpadGoal`, иначе `FixedGoal(target=20)`.
   - Награды: до двух `FixedReward` в чипах (`chips_amount`, `chips_amount_2`) + `CollectableSellPacksReward`
     при заданных `pack_id` и `num_packs`; если ничего не собралось — одна награда `Chips 0`.
   - Булевы значения распознаются как `true/1/yes/да`.
4. Результат пишется через `update_event`, выводится сводка и список предупреждений
   (номера строк указываются как `idx + 2` — с поправкой на строку заголовка).

Обязательные поля маппинга — `segment_name` и `node_id`; без них кнопка импорта заблокирована.

---

## Вкладки (ui/tabs/)

### ui/tabs/editor_tab.py

**`render_editor_tab()`** — редактор LiveEvent. Вызывает `inject_sticky_right_column()`.

**Блок «🗂️ Загрузка и валидация конфига»** (expander):

- **🆕 Новый конфиг** — при непустом конфиге требует подтверждения (`editor_confirm_reset`),
  затем сбрасывает конфиг, staged, контекст редактирования и флаги создания.
- **📂 Загрузить JSON** — повторная загрузка того же имени файла игнорируется
  (`editor_last_loaded_file`). **Если событий > 1 — включается staged-режим**, иначе конфиг
  загружается напрямую.
- **Панель staged** — выбор события по `EventID`, «✏️ Открыть», «➕ Добавить»
  (форма нового события с проверкой уникальности `EventID`),
  «💾 Применить изменения в исходный конфиг» и подпись о том, что редактируется.
- **📋 Схема + ✅ Проверить валидацию** — валидирует staged-конфиг с патчем, если он есть, иначе рабочий.

**Основная область** — две колонки (`st.columns([2, 3])`): дерево слева, редактор справа.

| Шаг | Условие показа | Содержимое |
|---|---|---|
| Пакетный импорт | `batch_import_event_idx >= 0` | Заголовок с `EventID`, кнопка закрытия, `render_batch_import_panel()` |
| **ШАГ 1: Событие** | редактируется событие или `creating_event`, и не `creating_segment` | `st.form` с полями события, галочками `ManualClaim` / `ShowPopupOnEmptyReward` и проверкой уникальности `EventID`. Под `show_advanced` — expander «⚙️ Расширенные параметры события»: `IsRoundelHidden`, `ShowRoundelOnAllMachines`, группа «💵 CashOutEvent» (`UseNodeFailedNotification`, `IsPrizePursuit`, `UseForceLandscapeOnWeb`), `StartingEventCurrency`, `IsCurrencyEvent`, `TimeWarning` |
| **ШАГ 2: Сегмент** | есть текущее событие и (редактируется сегмент или `creating_segment`) | Радио «Тип `PossibleSegmentInfo`» (4 типа + «Без `PossibleSegmentInfo`») **вне** формы, затем форма с именем и значением; имя и значение обязательны |
| **ШАГ 3: Узел** | редактируется узел или `creating_node` | Для нового узла — радио выбора типа; далее `render_node_editor(node_type, node_obj, key_prefix=...)`. Ненулевой результат означает «сохранить» |

Если ни один шаг не активен, выводится подсказка «Выберите элемент в дереве для редактирования».

---

### ui/tabs/export_tab.py

| Функция | Описание |
|---|---|
| `_copy_button(text)` | HTML/JS-кнопка «Copy to clipboard»; текст передаётся через base64, id кнопки — от md5 первых 64 символов |
| `_validate_liveevent(cfg) -> list[str]` | Проверяет каждый `EventID` через `validate_event_id` и ищет дубликаты |
| `render_export_tab()` | Вкладка экспорта |

Поведение `render_export_tab()`:

- при наличии staged-конфига экспортируется **он, с патчем** текущего события (выводится плашка);
- при нуле событий — подсказка и заблокированная кнопка скачивания;
- при ошибках валидации скачивание и копирование блокируются;
- предпросмотр: «— Весь конфиг —» или одно событие
  (`{"Events": [event], "IsFallbackConfig": ...}`), с отдельными кнопками скачивания и копирования.
  Результат предпросмотра хранится в `export_preview_json` / `export_preview_filename`.

Имя файла — фиксированное `LiveEventData.json` (константы из `utils/constants.py` здесь не используются).

---

### ui/tabs/singlepick_tab.py

**Класс `SinglePickState`** (dataclass) в `st.session_state["singlepick_state"]`:

| Поле | Тип | Описание |
|---|---|---|
| `config` | `SinglePickConfig` | Рабочий конфиг |
| `editing` | `Tuple[str, str, int]` | Что открыто справа (см. ниже) |
| `confirm_delete_cs` | `str` | Имя ConfigSet, для которого запрошено удаление |
| `confirm_type_change` | `bool` | Запрошена смена типа ConfigSet |
| `staged_cfg` | `Optional[dict]` | Исходный большой конфиг (сырой словарь) |
| `staged_cs_name` | `Optional[str]` | Имя открытого ConfigSet в staged |

Семантика `editing`:

| Значение | Что показывается справа |
|---|---|
| `("", "", -1)` | Ничего (подсказка) |
| `("NEW_CS", "", -1)` | Форма нового ConfigSet |
| `(cs_name, "", -1)` | Настройки ConfigSet: тип, `TotalPickOnBoard`, `PickUntilWin` |
| `(cs_name, "pick", i)` | Редактор пика `i` |
| `(cs_name, "wedge", i)` | Редактор сектора `i` |

| Функция | Описание |
|---|---|
| `get_singlepick_state() -> SinglePickState` | Достаёт или создаёт состояние |
| `move_pick_up(picks, index)` | Меняет местами `index-1` и `index` (кнопка «↓» вызывается как `move_pick_up(picks, i+1)`) |
| `_default_pickers_config() -> PickersConfig` | `RewardPick` (1 000 000 Chips, W=1, PM=1) + `JackpotPick` (`CIJackpot` нулями) + `RetryPick`; `TotalPickOnBoard=1`, `PickUntilWin=0` |
| `_get_staged_cs_names(state) -> list` | Имена ConfigSet-ов из staged |
| `_load_staged_cs(state, cs_name)` | Загружает один ConfigSet в редактор |
| `_apply_cs_to_staged(state) -> bool` | Возвращает изменения в staged |
| `_add_cs_to_staged(state, cs_name, cs)` | Добавляет новый ConfigSet в staged и открывает его |
| `_get_staged_cfg_with_patch(state) -> dict \| None` | Staged-конфиг с патчем текущего ConfigSet |
| `_render_toolbar(state)` | Новый конфиг (с подтверждением), загрузка файла, панель staged, валидация |
| `_render_tree(state)` | Дерево ConfigSet-ов: настройки, дублирование, удаление (с подтверждением), список пиков/секторов с кнопками ✏️ 📋 ↑ ↓ ❌, добавление элементов |
| `_render_editor(state)` | Правая панель по значению `editing` |
| `_render_reward_pick_form(state, pickers, i, pick)` | `Weight`, `PossibleMax`, список наград |
| `_render_jackpot_pick_form(state, pickers, i, pick)` | `Weight`, `PossibleMax`, переключатель `FixedJackpot`/`CIJackpot` (смена типа пересоздаёт джекпот нулями), поля Min/Max/CIMin/CIMax, инлайн-ошибка при `Min > Max` |
| `_render_retry_pick_form(state, pickers, i, pick)` | То же, что `RewardPick`, с пометкой «Награды необязательны» |
| `_render_wedge_form(state, wheel, i, wedge)` | `Weight` + список наград |
| `render_singlepick_tab()` | Точка входа: тулбар, разделитель, две колонки `[2, 3]` — дерево и редактор |

Особенности:

- staged-режим включается при **> 1** ConfigSet; при 0–1 конфиг открывается напрямую;
- `ValueError` из `SinglePickConfig.from_dict` показывается как «Файл не является SinglePick конфигом»;
- смена типа ConfigSet требует подтверждения и **удаляет текущее содержимое**;
- валидация в тулбаре: сначала логическая (`validate_singlepick`); проверка по JSON Schema выполняется
  только если логическая прошла **и** файл схемы загружен;
- формы правят объекты модели напрямую (без отдельной кнопки «Сохранить»);
- новые пики из дерева создаются с `PossibleMax = 0`, а `JackpotPick` — с `FixedJackpot`.

---

### ui/tabs/singlepick_export_tab.py

**`render_singlepick_export_tab()`** — вкладка экспорта SinglePick. Содержит свою копию `_copy_button`.

- Источник данных: staged-конфиг с патчем, если он есть, иначе `state.config.to_dict()`.
- Счётчик ConfigSet-ов, подсказка и заблокированная кнопка при пустом конфиге.
- Ошибки `validate_singlepick` выводятся как `[<ConfigSet>] <field>: <message>` и блокируют
  скачивание и копирование.
- Предпросмотр: «— Весь конфиг —» или один ConfigSet (`{"ConfigSets": {name: ...}}`).
- Имя файла — `SinglePickConfig.json`.

> В staged-режиме логическая валидация проверяет **только текущий редактируемый ConfigSet**,
> хотя экспортируется весь исходный конфиг.

---

### ui/tabs/validation_tab.py

**`render_validation_tab()`** — простая страница: загрузка JSON (пишется в `AppState.set_cfg`),
загрузка схемы, кнопка проверки через `validate_config`.

> Вкладка **не подключена** в `app.py` — функция только реэкспортируется из `ui/tabs/__init__.py`
> и `ui/__init__.py`. Схемная валидация LiveEvent доступна внутри `editor_tab`.

---

## Виджеты (ui/widgets/)

### ui/widgets/event_tree.py

**`render_event_tree()`** — иерархия Событие → Сегмент → Стадия/Узел. Константы:
`MAX_EVENTS_VISIBLE = 20`, `MAX_NODES_PER_SEGMENT = 10`.

| Возможность | Описание |
|---|---|
| Отложенное открытие узла | Ключ `_pending_edit_node`: если уже редактируется узел, дерево сначала делает `clear_editing()` + `rerun`, и только затем открывает новый |
| Пагинация событий | Постраничная (`tree_events_page`), кнопки ◀ ▶ при > 20 событиях |
| Пагинация узлов | Первые 10 узлов сегмента + кнопка «Показать ещё N узлов» / «Скрыть узлы» (`tree_show_all_{idx}_{seg}`) |
| Кнопки события | ✏️ редактировать · 📋 дублировать · ❌ удалить · 📥 пакетный импорт · ➕ добавить сегмент |
| Кнопки сегмента | ✏️ · 📋 · ❌ · ➕ добавить ноду |
| Кнопки узла | ✏️ · 📋 · ❌; в подписи — тип, `NodeID` и `NextNodeID` |

Дерево читает **сырые словари** (`get_events_raw()`), а не десериализованные модели.

---

### ui/widgets/node_editor.py

#### Система снимков

Streamlit кэширует значения виджетов по их ключам, поэтому при переключении на другой узел форма
показала бы данные предыдущего. Решение — «снимок» в `session_state` плюс принудительный сброс ключей.

| Функция | Описание |
|---|---|
| `_snapshot_key(prefix)` | `f"_node_snapshot_{prefix}"` |
| `set_node_snapshot(prefix, node)` | Кладёт снимок и сбрасывает ключи виджетов (в приложении не вызывается) |
| `_clear_widget_keys(prefix, node)` | Удаляет из `session_state` ключи виджетов, перечисленные **явными списками** для каждого типа узла |
| `_get_snapshot(prefix)` / `_clear_snapshot(prefix)` | Чтение / удаление снимка |

#### Формы

| Функция | Подпись | Возврат |
|---|---|---|
| `render_progress_node_form(prefix, existing=None)` | «📊 Progress Node» | `ProgressNode` при нажатии «💾 Сохранить», иначе `None` |
| `render_entries_node_form(prefix, existing=None)` | «🚪 Entries Node» | `EntriesNode` или `None` |
| `render_dummy_node_form(prefix, existing=None)` | «🎲 Dummy Node» | `DummyNode` или `None` |
| `render_node_editor(node_type, existing=None, key_prefix="node")` | — | Делегирует нужной форме; при неизвестном типе выводит ошибку |

`render_node_editor` сравнивает `(тип, node_id)` переданного узла с `_node_loaded_id_{prefix}`;
при расхождении сбрасывает ключи виджетов, обновляет снимок и вызывает `st.rerun()`.

Что показывают формы:

- **ProgressNode** — `NodeID`, `NextNodeID`, `GameList`, `MiniGame`, кнопочные поля, `IsLastNode`,
  MinBet, цель, список наград, `CustomTexts`, `PossibleItemCollect`,
  `PrizeBoxIndex` (подпись «0 = не задано»); под `show_advanced` — `ResegmentFlag`,
  `HideLoadingScreenForReward`, `ContributionLevel`.
  Пустой `PossibleItemCollect` при сохранении заменяется на `"Default"`; пустой `NextNodeID` → `[2]`.
- **EntriesNode** — `NodeID`, `GameList`, `GoalType`, `EntryTypes`, MinBet, кнопочные поля,
  `CustomTexts`, `PossibleItemCollect`, `PrizeBoxIndex`; под `show_advanced` — `ResegmentFlag`.
- **DummyNode** — `NodeID`, `NextNodeID` (пустой → `[11, 21, 31]`), `DefaultNodeID`, `CustomTexts`;
  всё остальное (`ResegmentFlag`, `IsLastNode`, `IsChoiceEvent`, `HideLoadingScreenForReward`,
  `PrizeBoxIndex`, `MiniGame`, `ContributionLevel`, кнопочные поля) — только под `show_advanced`.
  **Награды не редактируются**: при сохранении всегда подставляется `[get_default_reward()]`.

---

### ui/widgets/minbet_widget.py

**`render_minbet_widget(prefix, existing=None) -> FixedMinBet | VariableMinBet`**

Радио `Fixed` / `Variable`. Дефолты: `Fixed` — `250 000`; `Variable` — `0.8` / `25 000` / `5 000 000`.
Ключи виджетов: `{prefix}_minbet_type`, `{prefix}_fixed`, `{prefix}_var`, `{prefix}_min`, `{prefix}_max`.
Объект возвращается на каждом рендере, отдельной кнопки сохранения нет.

---

### ui/widgets/goal_widget.py

**`render_goal_widget(prefix, existing=None) -> Goal`**

Текстовое поле `Type` (по умолчанию `Spins`) + селектор параметров из шести значений:
`SpinpadGoal`, `FixedGoal`, `ConsecutiveWinsGoal`, `TotalCoinsPerDay`,
`TotalCoinsPerDayWithSpinLimiter`, `FixedGoalWithSpinLimiter`. Тип текущих параметров определяется
по `isinstance`; поля рисуются под выбранный тип. Изменения применяются сразу.

Для `ConsecutiveWinsGoal` подписи полей соответствуют схеме: скаляр — `WinsInStreakTarget`
(побед в серии), блок `Multiplier`/`Min`/`Max` — `NumberOfStreaksSpinPadGoal` (количество серий).
`Multiplier` ограничен снизу значением `0.001`, поскольку схема требует `exclusiveMinimum: 0`.

---

### ui/widgets/reward_widget.py

**`render_reward_widget(prefix, index, existing=None) -> Reward`**

Селектор типа из `REWARD_TYPES` (12 значений) с обратным определением типа по существующей награде.
Соответствие «тип в UI → модель»:

| Тип в UI | Модель | `Currency` |
|---|---|---|
| `Chips` | `FixedReward` | `Chips` |
| `MLM` | `FixedReward` | `Tickets` |
| `Loyalty Point` | `FixedReward` | `Loyalty` |
| `Vip Points` | `FixedReward` | `VipPoints` |
| `Sweepstakes` | `FixedReward` | `Entries_Name` |
| `BoardGameDices` / `BoardGameBuilds` / `BoardGameRareBuilds` | `FixedReward` | одноимённая |
| `VariableChips` | `RtpReward` | `Chips` |
| `FreePlays` | `FreeplayUnlockReward` | — |
| `Packs` | `CollectableSellPacksReward` | — |
| `MagicPacks` | `CollectableMagicPacksReward` | — (1–5 пачек) |

---

### ui/widgets/rewards_editor.py

| Функция | Описание |
|---|---|
| `get_default_reward() -> Reward` | `FixedReward(Chips, 2 500 000)` |
| `render_rewards_editor(prefix, existing_rewards) -> List[Reward]` | Список наград с кратким описанием, кнопками ✏️/❌, добавлением и отменой |

Состояние: `{prefix}_rewards` (сам список), `{prefix}_editing_idx`, `{prefix}_show_add`.
Список инициализируется из `existing_rewards` **только при первом вызове**; если он пуст,
подставляется одна награда по умолчанию.

---

### ui/widgets/singlepick_reward_widget.py

**`render_sp_reward_widget(prefix, index, existing=None) -> SPReward`**

Локальный список `SP_REWARD_TYPES` (12 значений; есть `PurchaseReward`, нет `MagicPacks`) и
`_CURRENCY_MAP` / `_CURRENCY_TO_TYPE` для обратного определения типа через `_detect_type`.
Типы: фиксированные валюты → `FixedSPReward`, `VariableChips` → `RtpSPReward`,
`FreePlays` → `FreeplaySPReward`, `Packs` → `PacksSPReward`, иначе `PurchaseSPReward`
(поля `ShopType` и `ShopName`). Суммы приводятся к `int`.

---

### ui/widgets/singlepick_rewards_editor.py

| Функция | Описание |
|---|---|
| `_reward_desc(reward) -> str` | Краткое описание для списка |
| `get_default_sp_reward() -> SPReward` | `FixedSPReward(Chips, 1 000 000)` (импортируется в `singlepick_tab`, но не вызывается) |
| `render_sp_rewards_editor(prefix, existing_rewards) -> List[SPReward]` | Аналог `render_rewards_editor`; пустой список остаётся пустым |

Состояние: `{prefix}_sp_rewards`, `{prefix}_sp_editing_idx`, `{prefix}_sp_show_add`.
При удалении редактируемой награды индекс редактирования сбрасывается.

---

## Утилиты (utils/)

### utils/constants.py

| Группа | Константы |
|---|---|
| Дефолты события | `DEFAULT_EVENT_ID`, `DEFAULT_ASSET_BUNDLE`, `DEFAULT_BLOCKER_PREFAB`, `DEFAULT_ROUNDEL_PREFAB`, `DEFAULT_EVENT_CARD_PREFAB`, `DEFAULT_NODE_COMPLETION_PREFAB`, `DEFAULT_CONTENT_KEY`, `DEFAULT_MIN_LEVEL`, `DEFAULT_REPEATS`, `DEFAULT_SEGMENT` |
| Сегменты | `DEFAULT_VIP_RANGE = "1-10+"`, `SEGMENT_INFO_TYPES` (4 типа → подписи для UI), `SEGMENT_INFO_NONE = ""` |
| Дефолты узла | `DEFAULT_GAME_LIST`, `DEFAULT_BUTTON_TEXT`, `DEFAULT_MINIGAME`, `DEFAULT_CONTRIBUTION_LEVEL` |
| Типы наград | `REWARD_TYPES` (12 значений) |
| Типы целей | `GOAL_TYPES` (`Spins`, `Coins`, `Wins`, `ConsecutiveWins`, `TotalCoinsPerDay`) |
| Валюты | `CURRENCY_TYPES` (8 значений) |
| Имена файлов | `DEFAULT_OUTPUT_FILENAME = "LiveEventData.json"`, `DEFAULT_SCHEMA_FILENAME = "schema.json"` |
| Прочее | `MAX_NODE_ID = 999999`, `MIN_BET_MIN_VALUE = 0.0`, `MIN_BET_MAX_VALUE = 1_000_000_000.0` |

Реально импортируются только `DEFAULT_VIP_RANGE`, `SEGMENT_INFO_TYPES`, `SEGMENT_INFO_NONE`
(в `editor_tab`) и `REWARD_TYPES` (в `reward_widget`); остальные значения продублированы литералами
в коде форм. `utils/__init__.py` не реэкспортирует `SEGMENT_INFO_TYPES`, `SEGMENT_INFO_NONE`,
`DEFAULT_OUTPUT_FILENAME`, `DEFAULT_SCHEMA_FILENAME`, `MAX_NODE_ID`, `MIN_BET_*`.

### utils/helpers.py

| Функция | Описание | Используется |
|---|---|---|
| `parse_comma_separated_list(text) -> List[str]` | Разбор строки через запятую, пустые элементы отбрасываются | да |
| `join_list_to_comma_string(items) -> str` | `", ".join(items)` | нет |
| `process_multiline_text(text) -> List[str]` | Непустые строки многострочного текста | да |
| `format_number(value, precision=2) -> str` | Форматирование с заданной точностью | нет |

### utils/validators.py

**Все функции возвращают `List[str]`** — список сообщений об ошибках; пустой список означает
успешную валидацию.

| Функция | Проверки |
|---|---|
| `validate_event_id(event_id)` | Непустой; только латиница, цифры, `_`, `-` |
| `validate_node_id(node_id, existing_ids=None)` | Положительный; отсутствует в `existing_ids` |
| `validate_game_list(game_list)` | Список непуст; имена непусты |
| `validate_min_bet(min_bet)` | `FixedMinBet.amount >= 0`; для `VariableMinBet`: `variable > 0`, `min >= 0`, `max >= min` |
| `validate_goal(goal)` | `Goal.type` непуст |
| `validate_rewards(rewards)` | Список непуст; `amount > 0`, если поле есть |
| `validate_segment_name(name)` | Непустое; только латиница, цифры, `_`, `-` |
| `validate_vip_range(value)` | Формат `1-10` или `1-10+` |

Из модуля вызывается только `validate_event_id` (в `export_tab`); валидация в формах реализована
инлайн, поэтому, например, имена сегментов с кириллицей формы пропускают.

---

## Потоки данных

```
Загрузка LiveEvent
    └─> load_config_from_json(bytes)          # кодировки, setdefault корневых ключей
    ├─ событий > 1 ──> AppState.set_staged_cfg()  ──> load_staged_event(idx) ──> set_cfg({одно событие})
    └─ событий ≤ 1 ──> AppState.set_cfg() + clear_staged()

Редактирование
    └─> дерево: start_editing_event / _segment / _node   # deepcopy в editing_context
    └─> формы правят копию
    └─> apply_editing() ──> update_event() ──> инвалидация _event_cache

Возврат в исходник (staged)
    └─> apply_event_to_staged()               # по кнопке
    └─> get_staged_cfg_with_patch()           # автоматически при экспорте и валидации

Экспорт LiveEvent
    └─> _validate_liveevent(cfg)              # EventID: формат и дубликаты
    └─> save_config_to_json(cfg)              # indent=4, UTF-8
    └─> download_button / _copy_button

Валидация по схеме
    └─> validate_config(cfg, schema)          # jsonschema; без схемы — (False, "Схема не загружена")

SinglePick
    └─> load_config_from_json ──> SinglePickConfig.from_dict   # ValueError = не тот формат
    ├─ ConfigSet-ов > 1 ──> state.staged_cfg ──> _load_staged_cs(name)
    └─ ConfigSet-ов ≤ 1 ──> state.config
    └─> формы правят модель напрямую
    └─> validate_singlepick(state.config) ──> to_dict() / _get_staged_cfg_with_patch() ──> экспорт
```

---

## Ключи `st.session_state`

| Ключ | Назначение |
|---|---|
| `app_state`, `singlepick_state` | Экземпляры состояния |
| `show_advanced` | Тумблер расширенных параметров (вкладка «Настройки») |
| `creating_event`, `creating_segment`, `creating_node` | Флаги режима создания в редакторе LiveEvent |
| `editor_confirm_reset` | Запрошен сброс конфига |
| `editor_last_loaded_file`, `editor_staged_file_name` | Защита от повторной загрузки и имя staged-файла |
| `editor_staged_selected_idx`, `editor_staged_creating_new` | Открытое событие staged и форма нового события |
| `editor_json_uploader`, `editor_schema_uploader` | Загрузчики файлов |
| `batch_import_event_idx` | Индекс события для пакетного импорта (`-1` — панель закрыта) |
| `map_{field}`, `file_uploader_{key}` | Маппинг колонок и загрузчик импорта |
| `tree_events_page`, `tree_show_all_{idx}_{seg}` | Пагинация дерева |
| `_pending_edit_node` | Отложенное открытие узла после `clear_editing` |
| `_node_snapshot_{prefix}`, `_node_loaded_id_{prefix}` | Снимок узла и признак загруженного узла |
| `segment_info_type_selector`, `…_radio` | Тип `PossibleSegmentInfo` в форме сегмента |
| `{prefix}_rewards`, `{prefix}_editing_idx`, `{prefix}_show_add` | Состояние редактора наград LiveEvent |
| `{prefix}_sp_rewards`, `{prefix}_sp_editing_idx`, `{prefix}_sp_show_add` | То же для SinglePick |
| `export_filter_event_id`, `export_preview_json`, `export_preview_filename` | Предпросмотр экспорта LiveEvent |
| `sp_confirm_reset`, `sp_last_loaded_file`, `sp_staged_cs_selector`, `sp_staged_selected_cs`, `sp_staged_creating_new` | Тулбар SinglePick |
| `singlepick_export_filter`, `singlepick_export_preview_json`, `singlepick_export_preview_filename` | Предпросмотр экспорта SinglePick |

`AppState.clear_editing()` дополнительно удаляет все ключи с префиксами `_node_loaded_id_`
и `_node_snapshot_`.

---

## Ключевые особенности

**Staged-конфиг** — при загрузке файла с более чем одним событием (или более чем одним ConfigSet)
в рабочую память берётся только один элемент, остальное хранится в исходном виде.
При экспорте и валидации изменения накладываются патчем. Подробности — в
[STAGED_CONFIG_USAGE.md](STAGED_CONFIG_USAGE.md).

**Кэширование событий** — `AppState._event_cache` хранит десериализованные события по индексу;
кэш инвалидируется при обновлении и корректно переиндексируется при удалении и дублировании.

**Редактирование через копию** — `editing_context` держит `deepcopy`, поэтому отмена не оставляет
следов в конфиге.

**Система снимков** — обходит кэширование значений виджетов Streamlit при переключении между узлами.

**Пакетный импорт** — CSV/Excel с автоопределением строки заголовка и сопоставлением колонок
по синонимам, включая русские названия.

**Дублирование** — события, сегменты, узлы, ConfigSet-ы, пики и секторы; для имён генерируется
суффикс `_copy` / `_copy2` / …

**Расширенные параметры** — редкие поля скрыты за тумблером на вкладке «⚙️ Настройки».

**Sticky-панель** — CSS делает последнюю колонку (редактор) фиксированной при прокрутке дерева.

---

## Неиспользуемый код

Перечисленное ниже присутствует в репозитории, но не вызывается приложением:

| Объект | Файл |
|---|---|
| Весь модуль фабрик (и он же неполный) | `services/builders.py` |
| `render_validation_tab` — вкладка не подключена в `app.py` | `ui/tabs/validation_tab.py` |
| `render_import_tab` — импортируется в `app.py`, но не вызывается | `ui/import_tab.py` |
| `_read_file` — заменён `_load_with_header_detection` | `ui/import_tab.py` |
| `confirm_button`, `styled_info`, `styled_error`, `format_key` | `ui/common.py` |
| `set_node_snapshot` | `ui/widgets/node_editor.py` |
| `get_default_sp_reward` — импортируется, но не вызывается | `ui/widgets/singlepick_rewards_editor.py` |
| `save_config_to_json_compact` | `services/json_io.py` |
| `join_list_to_comma_string`, `format_number` | `utils/helpers.py` |
| Все валидаторы, кроме `validate_event_id` | `utils/validators.py` |
| Большинство константных значений (см. выше) | `utils/constants.py` |
| `set_temp` / `get_temp` / `clear_temp`, свойство `Segment.vip_range` | `services/state_manager.py`, `models/event.py` |

Тестов в репозитории нет: в `.kiro/specs/singlepick-tab/tasks.md` все задачи с юнит- и property-тестами
помечены как опциональные и не выполнены, каталога `tests/` не существует.

---

## Известные ограничения

- **`PrizeBoxIndex = 0` не сохраняется.** Все три типа узлов пишут ключ только при значении `> 0`,
  а формы подписывают поле как «0 = не задано», поэтому нулевой индекс молча выпадает из JSON.
  Схема V10 при этом допускает и `0`, и отрицательные значения — см.
  [«Расхождения со схемой V10»](#расхождения-со-схемой-v10).
- **`DummyNode` теряет награды.** Форма не редактирует список наград и при сохранении всегда
  подставляет одну награду по умолчанию (`Chips 2 500 000`), затирая исходные.
- **Сброс ключей виджетов неполон.** Списки в `_clear_widget_keys` не содержат ключей расширенных
  параметров (`_p_resegment`, `_p_contrlevel`, `_e_resegment`, `_d_*` и др.), поэтому при включённом
  `show_advanced` и переключении между узлами эти поля могут показывать значения предыдущего узла.
- **Текст ошибки про `Percentage` расходится с проверкой.** `is_percentage_valid` допускает до трёх
  знаков после запятой, а сообщение и спецификация говорят «кратно 0.01».
- **Уникальность имён ConfigSet внутри одного конфига не проверяема** — они являются ключами `dict`;
  `validate_configset_name` защищает только ввод нового имени.
- **Валидация SinglePick в staged-режиме частичная** — проверяется лишь открытый ConfigSet,
  тогда как экспортируется весь исходный конфиг.
- **Валидация имён в формах слабее, чем в `utils/validators.py`.** Формы требуют лишь непустое имя,
  так что сегмент с кириллицей или пробелами создать можно, хотя `validate_segment_name` его отверг бы.
- **Один уровень стадий в UI.** Узлы всегда добавляются в `Stages[0]`; существующие стадии
  отображаются и редактируются, но создать новую через интерфейс нельзя.
- **`datetime.utcnow()`** в `get_default_time_warning()` помечен как устаревший в актуальных версиях
  Python.
- **Переменные колонок в `editor_tab` названы наоборот** (`right_col, left_col = st.columns([2, 3])`):
  дерево отображается в левой колонке, редактор — в правой.

---

## Расхождения со схемой V10

Сверено со схемой [schema/LiveEventData_V10.json](schema/LiveEventData_V10.json)
(`title: "LiveEventData_V10_Generated"`, `description: "fix minigame"`, 35 определений).
Её же нужно подсовывать в поле «📋 Схема» на вкладке редактора, чтобы проверить конфиг из UI.
Результаты ниже получены прогоном вывода моделей через `jsonschema.Draft7Validator` и проверкой
цикла «загрузить → сохранить».

### 1. Обязательные `ManualClaim` и `ShowPopupOnEmptyReward` — ✅ исправлено

Ранее `NodeEventData.required` содержал два поля, которых в коде не было вообще, из-за чего **любой**
экспортированный конфиг давал две ошибки (`'ManualClaim' is a required property`,
`'ShowPopupOnEmptyReward' is a required property`).

Что сделано: поля `manual_claim` и `show_popup_on_empty_reward` добавлены в
`PossibleNodeEventData` (сериализация как `ManualClaim` / `ShowPopupOnEmptyReward`, чтение с дефолтом
`False`), в `make_node_event` и в форму события — две галочки рядом с `IsRoundelHidden`
и `ShowRoundelOnAllMachines`. Проверено валидатором: конфиги с `ProgressNode`, `EntriesNode`
и `DummyNode` теперь проходят схему без ошибок.

**Остаётся:** необязательное `SkipLastManualClaim` приложение по-прежнему не знает и вырезает
при сохранении (см. пункт 4).

### 2. `ConsecutiveWinsGoal`: имена полей — ✅ исправлено

Схема требует `WinsInStreakTarget` (integer) и `NumberOfStreaksSpinPadGoal`
(`MultiplierBasedValue`), а приложение писало эти имена перекрёстно —
`NumberOfStreaksTarget` и `WinsInStreakSpinPadGoal`, — поэтому цель схему не проходила.

Что сделано:

- поле модели `number_of_streaks_target` переименовано в `wins_in_streak_target`,
  `to_dict()` пишет `WinsInStreakTarget` и `NumberOfStreaksSpinPadGoal`;
- `from_dict()` читает новые имена, а при их отсутствии — старые
  (`NumberOfStreaksTarget` / `WinsInStreakSpinPadGoal`), поэтому ранее созданные конфиги
  открываются без ошибок и при сохранении переписываются в схемные имена;
- в `goal_widget` подписи приведены к схеме: скаляр — «WinsInStreakTarget (побед в серии)»,
  блок `Multiplier`/`Min`/`Max` подписан как `NumberOfStreaksSpinPadGoal` (количество серий);
- `Multiplier` ограничен снизу значением `0.001` — схема требует `exclusiveMinimum: 0`,
  а прежний виджет допускал `0.0`.

> **Внимание при открытии старых конфигов.** Значения читаются позиционно: скаляр остаётся скаляром,
> блок `Multiplier/Min/Max` — блоком. Но по прежним (неверным) подписям в UI скаляр заполняли как
> «число серий», а теперь он означает «побед в серии». Восстановить исходный замысел автоматически
> нельзя, поэтому у ранее собранных целей этого типа значения стоит перепроверить вручную.

### 3. Сущности схемы, на которых приложение падает или портит данные

| Сущность схемы | Поведение приложения |
|---|---|
| `PossibleLeaderboardEventData` — второй допустимый тип события в `EventData` | Дерево падает с `KeyError` на `event_dict["PossibleNodeEventData"]` ([event_tree.py:56](ui/widgets/event_tree.py:56)), `duplicate_event` — тоже `KeyError`. `PossibleNodeEventData.from_dict()` молча возвращает пустое событие со всеми дефолтами (`EventID = "MyEvent"`), и сохранение затирает оригинал |
| `EntriesProgressNode` | `node_from_dict` → `ValueError: Unknown node type` — событие невозможно открыть |
| `PrizePoolNode` | то же самое |
| `Rounds` вместо `Stages` в сегменте | Загружается без ошибки, но теряется: `Segment.from_dict` читает только `Stages` и `PossibleSegmentInfo` |

### 4. Молчаливая потеря полей при цикле «загрузить → сохранить»

Поля ниже присутствуют в схеме, но не читаются моделями, поэтому вырезаются из результата
без предупреждения (проверено round-trip'ом):

| Уровень | Теряется |
|---|---|
| Событие | `SkipLastManualClaim`, `Test1`, `Test2` (`ManualClaim` и `ShowPopupOnEmptyReward` сохраняются с тех пор, как реализован пункт 1) |
| Нода (`ProgressNode` и др.) | `FallbackGoal`, `PossibleTimeGate`, `ClaimTooltipText` |
| Цель | `Conditions` (`MinWin` / `Threshold` → `AvgBetBasedThreshold` / `FixedValue`) |
| Сегмент | `Rounds` |

В staged-режиме потери ограничены тем событием, которое действительно открывали в редакторе:
остальные события хранятся сырыми словарями и остаются нетронутыми.

### 5. UI не ограничивает значения, заданные в схеме через enum и pattern

| Поле | Ограничение схемы | Поведение приложения |
|---|---|---|
| `ProgressNode.MiniGame` | `anyOf`: `FlatReward` либо `^SinglePick_` | Свободное текстовое поле. У `DummyNode` и `EntriesProgressNode` `MiniGame` — обычная строка, ограничение действует только для `ProgressNode` |
| `FreeplayUnlockReward.GameName` | enum из 227 значений | Свободное текстовое поле (дефолт `Buffalo` в enum есть) |
| `CollectableSellPacksReward.PackId` | enum `sellPack*` | Свободное поле + колонка `pack_id` в CSV-импорте |
| `CollectableMagicPacksReward.PackId` | enum `magicPack*` | Свободное поле |
| `NumPacks` | `maximum: 5` | Для `Packs` верхней границы в UI нет, дефолт модели — `4`; для `MagicPacks` ограничение `max_value=5` выставлено. Импорт из CSV границу не проверяет |
| `FixedReward.Currency` | pattern `^(Entries_[a-zA-Z0-9]+\|Tickets\|Chips\|Loyalty\|VipPoints\|BoardGame(Dices\|Builds\|RareBuilds))$` | Тип «Sweepstakes» подставляет литерал `Entries_Name` — формально pattern проходит, но это заглушка вместо реального имени entries |
| `RtpReward.Currency` | enum `["Chips"]` | Захардкожен `Chips` — совпадает |

### 6. `PrizeBoxIndex`

Схема объявляет поле как `integer` без границ, то есть `0` и отрицательные значения допустимы.
Приложение пишет ключ только при значении `> 0`, поэтому задать `0` нельзя, а загруженный из файла
`0` при сохранении исчезает.

### 7. Что сходится

Совпадают: корень (`Events` + `IsFallbackConfig`), `Stage`, `SegmentInfoJson` (4 типа и опущение
блока при пустом значении), `MinBetJson` (`FixedMinBet.MinBet`, `MinBetVariable.Variable/Min/Max`),
`RewardJson` (все пять типов и их поля), `FixedGoal`, `SpinpadGoal`, `TotalCoinsPerDay`,
`TotalCoinsPerDayWithSpinLimiter`, `FixedGoalWithSpinLimiter`, а также полные наборы `required`
у `ProgressNode`, `EntriesNode` и `DummyNode`.

### 8. Замечания к самой схеме

Не относятся к приложению, но влияют на то, как строить в нём выпадающие списки:

- `PurchaseRewardConfig` определён, но ни из одного места не используется (`RewardJson` его не включает)
  — в LiveEvent награда-покупка недоступна, `PurchaseReward` существует только в схеме SinglePick.
- enum `GameName` содержит **227 значений при 217 уникальных**. Дубликаты: `MoneyInTheBankBaconBlvd`,
  `WingsOfThePhoenix`, `SafariStacks`, `SafariStacks_HR`, `PrettyDevil`, `LadyOfCythera`,
  `LadyOfCythera_HR`, `FestivalOfRiches`, `LuckyHog`, `TreasureVoyage`. Есть пары, различающиеся только
  регистром: `LuckyHoneyCombFortuneBags` / `LuckyHoneycombFortuneBags`, а также
  `ChiliChiliFireBoosted` и `ChilliChilliFireBoosted`.
- `Test1` и `Test2` в `NodeEventData` выглядят как отладочные остатки.
- Опечатка в имени определения: `EntiresNodeJson` (ключ узла `EntriesNode` при этом корректный).
- `TimeWarning` и `PossibleTimeGate` объявлены с `format: date-time`, но `validate_config` вызывает
  `jsonschema.validate` **без** `format_checker`, поэтому формат даты фактически не проверяется даже
  при загруженной схеме.
